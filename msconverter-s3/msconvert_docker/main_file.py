from pathlib import Path
from flask import Flask, request, jsonify, abort , make_response
import tarfile
import re
import os
import logging
from threading import Lock
import time
from collections import deque
from subprocess import PIPE, run
import requests
from io import BytesIO
import shlex
import tarfile
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import BinaryIO, Union
import sys, traceback
import json
import datetime
import shutil
import pytz

app = Flask(__name__)
current_dir= os.getcwd()
working_dir = os.path.join(current_dir, "input_files")
# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler('app.log'),
                              logging.StreamHandler()])

# Create separate logger for endpoint requests
request_logger = logging.getLogger('endpoint_requests')
request_logger.setLevel(logging.INFO)
handler = logging.FileHandler('endpoint_requests.log', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
request_logger.addHandler(handler)

# loading credentials

CREDENTIALS = os.path.join(current_dir, "credentials/.env")
load_dotenv(CREDENTIALS)


# Global lock and pending requests queue
global_lock = Lock()
pending_requests = deque()
request_counter = 0


# configurations
FILE_LIMIT = 5 * 1024 * 1024
INPUT_DIR = Path("input_files")
INPUT_DIR.mkdir(exist_ok=True)
CHUNK = 16 * 1024 * 1024

session = requests.Session()


# Usable S3 Clients

def get_s3_client() -> boto3.client:
    """Return a boto3 S3 client configured for Ceph."""
    try:
        return boto3.client(
            "s3",
            endpoint_url=os.getenv("ENDPOINT_URL"),
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY"),
            region_name="",  # Ceph does not use AWS regions
        )
    except KeyError as e:  # noqa: BLE001
        raise RuntimeError(f"Missing S3 credential: {e}") from None
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"Cannot create s3 client: {e}") from e



# ------------------------------------------------------------------
# Upload helpers
# ------------------------------------------------------------------
def generate_presigned_put_url(
    key: str,
    *,
    expires_in: int = 3_600,
) -> str:
    """Return a one-off PUT URL for the given object key."""
    s3 = get_s3_client()
    bucket = os.getenv("BUCKET")
    try:
        return s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError("Could not create pre-signed URL") from exc


#Upload helpers

def upload_via_presigned_url(
    url: str,
    file_handle: BinaryIO,
    *,
    chunk_size: int = 16 * 1024 * 1024,
) -> None:
    """Stream *file_handle* to *url* using HTTP PUT."""
    resp = requests.put(
        url, 
        data=file_handle, 
        headers={"Content-Type": "application/octet-stream"},
        timeout=None
        )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Upload failed: HTTP {resp.status_code} – {resp.text}"
        )



# ------------------------------------------------------------------
# Convenience wrapper
# ------------------------------------------------------------------
def upload_fileobj(
    file_handle: BinaryIO,
    filename: str,
    file_id: str,
) -> None:
    """Upload *file_handle* under 'nfdi4chemCSFlask/{file_id}/{filename}'."""
    bucket = os.getenv("BUCKET")
    key = f"{file_id}/{filename}"
    url = generate_presigned_put_url(key)
    print(url)
    upload_via_presigned_url(url, file_handle)
    print(f"✔ {filename} uploaded to {key}")
    return




# Generates a download link to download file
def download_file(filename, file_id):
    s3 = get_s3_client()
    bucket = os.getenv("BUCKET")    
    data_key = file_id+ '/' +filename
    response = s3.generate_presigned_url('get_object',
                                         Params={'Bucket': os.getenv('BUCKET'), 'Key': data_key}
                                         )
    
    print("--------------------------------------")
    print("Download Link")
    print(response)
    print("--------------------------------------")
    #content = requests.get(response)
    sys.stdout.flush()
    return response




def fetch_file(url: str, filename:str, folder_id:str):
    """
    Downloads *url* to  INPUT_DIR / folder_id / filename
    and returns the Path object (guaranteed to exist).
    """
    target_dir = INPUT_DIR / folder_id
    target_dir.mkdir(parents=True, exist_ok=True)

    path = target_dir / Path(filename).name

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=CHUNK):
                if chunk:
                    f.write(chunk)
    return path


# Endpoint for conversion to mzML fof Raw or wiff file or .d folder
@app.route('/msconvert_file', methods=['POST'])
def check_file():
    global request_counter
    request_counter += 1
    req_id = request_counter
    req_time = time.strftime('%Y-%m-%d %H:%M:%S')
    # Add request to pending queue
    pending_requests.append({
        'id': req_id,
        'endpoint': '/msconvert_file',
        'request_given': req_time
    })
    try:
        with global_lock:
            data = request.get_json(silent=True) or {}
            url = data.get("download_url")
            filename = data.get("filename")
            folder_id = data.get("foldername")
            config_raw = data.get("config") or ''
            config = re.sub(r'(?:-o|--outdir)\s+\S+|\bstring\b', '', config_raw, flags=re.I).strip()
            if not url or not data:
                remove_folder(output_folder_path)
                abort(400, description="missing 'url' in JSON body / Empty JSON ")

            output_folder_path = os.path.join(working_dir, folder_id)

            new_path = fetch_file(url=url, filename=filename, folder_id= folder_id)
            
            for file in os.listdir(output_folder_path):
                if file.lower().endswith('.raw'):
                    new_path = os.path.join(output_folder_path,file)
                    if not os.path.isfile(new_path):
                        pending_requests.popleft()
                        remove_folder(output_folder_path)
                        return jsonify({'error': 'Not a valid file'}), 400
                elif file.lower().endswith(('.tar', '.tar.gz', '.tar.xz')):
                    abs_path = os.path.join(output_folder_path, file)
                    if has_wiff(abs_path):
                        print("Input File: Wiff")
                        new_path = open_tar_folder_wiff(os.path.join(output_folder_path,file), output_folder_path)
                        if not os.path.isfile(new_path):
                            pending_requests.popleft()
                            remove_folder(output_folder_path)
                            return jsonify({'error': 'Not a valid file'}), 400
                    else:
                        print("Input Categories: Folder")
                        open_tar_folder(os.path.join(output_folder_path,file), output_folder_path)
                        dirs = [d for d in Path(output_folder_path).iterdir() if d.is_dir()]
                        if (n := len(dirs)) != 1:
                            raise ValueError(f"Expected exactly one folder in {output_folder_path}, found {n}")
                        new_path = dirs[0]
                        if not os.path.isdir(new_path):
                            pending_requests.popleft()
                            remove_folder(output_folder_path)
                            return jsonify({'error': 'Neither a valid file nor a folder'}), 400

                    
            print(f'Input Path: {new_path}')
            #checking if the new_path is a valid_file
            print("Going for conversion of input file")
            pending_requests.popleft()
            # Doing the actual conversion with the parmeters
            start_time = time.time()
            cmd = ["wine_anyuser", "msconvert", new_path, "-o", output_folder_path] 
            if config:
                cmd[2:2] = shlex.split(config)     # slip config flag before "-o ..."
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            print("Out from the Coversion")

            if result.stderr:
                print(f"error in the result: {result.stderr}")
                remove_folder(output_folder_path)
                return jsonify({'error': 'Error executing file', 
                                'details': result.stderr,
                                'time_taken_sec': time_taken}), 500
            else:
                output_file_path = Path(output_filepath(new_path))
                print("now doing the upload into s3")

                with output_file_path.open("rb") as fh:
                    upload_fileobj(fh,output_file_path.name,folder_id)
                print("upload completed!! now creating download_link")
                download_url = download_file(filename=output_file_path.name, file_id= folder_id)
                #Print the output on the server
                response_data = jsonify(
                    message='Conversion Successful!!',
                    time_taken_sec=time_taken,
                    mzml_download_url=download_url
                )

                resp = make_response(response_data, 200)
                resp.headers['Content-Length'] = str(len(resp.get_data()))
                json_bytes = resp.get_data()
                payload = json.loads(json_bytes)
                print(json.dumps(payload, indent=2), file=sys.stderr)
                remove_folder(output_folder_path)
                sys.stderr.flush()
                return jsonify({'message': 'Conversion Successful!!', 
                                'time_taken_sec': time_taken,
                                'mzml_download_url': download_url,
                                'mzml_outputfile_name': output_file_path.name}), 200

            
    except Exception as e:
        # Remove from pending queue if an error occurs
        if pending_requests:
            pending_requests.popleft()
        remove_folder(output_folder_path)
        request_logger.error('Exception occurred: {}'.format(str(e)))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500



# Endpoint to check the status of pending requests:
@app.route('/msconvert_status', methods=['GET'])
def status():
    return jsonify({
        'pending_count': len(pending_requests)
        #'pending_requests': list(pending_requests)
    })



#Function to generate output file path
def output_filepath(path):
    dir_name = os.path.dirname(path)
    base_name = os.path.splitext(os.path.basename(path))[0]
    output_file = base_name + '.mzML' 
    output_file_path = os.path.join(dir_name, output_file)
    return output_file_path



# Function to open tar folder and extract files
def open_tar_folder(tar_file_path, destination_folder):
    try:
        with tarfile.open(tar_file_path,'r') as tar:
            tar.extractall(path=destination_folder)
        os.remove(tar_file_path)
        return "Extraction compelted successfully!!"
    except Exception as e:
        return "Error incurred during extration from tar: "+ str(e)



#function to open tar folder and return the correct path for wiff file specifically
def open_tar_folder_wiff(tar_file_path, destination_folder):
    try:
        with tarfile.open(tar_file_path,'r') as tar:
            tar.extractall(path=destination_folder)
        os.remove(tar_file_path)
        for file in os.listdir(destination_folder):
            if file.lower().endswith('.wiff'):
                return os.path.join(destination_folder,file)
            if os.path.isdir(os.path.join(destination_folder,file)):
                wiff_folder = os.path.join(destination_folder,file)
                for file in os.listdir(wiff_folder):
                    if file.lower().endswith('.wiff'):
                        return os.path.join(wiff_folder,file)
        
    except Exception as e:
        return "Error incurred during extration from wiff.tar: "+ str(e)
    
#  to test if the .tar file has wiff extention as well
def has_wiff(tar_path: str) -> bool:
    """Return True if any .wiff file exists at tar root OR one folder deep."""
    try:
        with tarfile.open(tar_path, "r") as tar:
            for m in tar.getmembers():
                if m.isfile() and Path(m.name).suffix.lower() == ".wiff":
                    depth = m.name.count("/")
                    if depth <= 1:          # 0 → root, 1 → one folder deep
                        return True
    except Exception:
        pass
    return False




# cleans up the s3 bucket : objects older than 1 hour
def cleanup() -> None:
    s3 = get_s3_client()
    bucket = os.getenv('BUCKET')
    if not bucket:
        print("BUCKET environment variable not set proerly.")
        return

    cutoff = datetime.datetime.now(pytz.UTC) - datetime.timedelta(hours=1)

    paginator = s3.get_paginator('list_objects_v2')
    deleted = 0
    try:
        for page in paginator.paginate(Bucket=bucket):
            for obj in page.get('Contents', []):
                if obj['LastModified'] < cutoff:
                    key = obj['Key']
                    print(f"Deleting {key} (Last Modified: {obj['LastModified']})")
                    s3.delete_object(Bucket=bucket, Key=key)
                    deleted += 1
    except (ClientError, BotoCoreError) as e:
        print(f" Error listing objects in bucket {bucket}: {e}")

    print(f"Cleanup finished. Deleted {deleted} objects.")



def remove_folder(abs_path: Union[str, Path]) -> None:
    path = Path(abs_path)

    if not path.is_absolute():
        raise ValueError("Path must be absolute – got: {}".format(path))

    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    shutil.rmtree(path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)