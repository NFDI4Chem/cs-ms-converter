from flask import Flask, request, jsonify, abort
from pathlib import Path
import tarfile
import re
import os, sys
import logging
from threading import Lock
import time
from collections import deque
from subprocess import PIPE, run
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import datetime
import json
import requests
from io import BytesIO
from typing import BinaryIO, Union
import shutil


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


# Loading Credentials

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


# Use of S3 Clients


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


# Upload helpers

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



# Validation of the mzml file
@app.route('/fileinfo_mzml', methods=['POST'])
def validate_file():
    global request_counter
    request_counter += 1
    req_id = request_counter
    req_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Add request to pending queue
    pending_requests.append({
        'id': req_id,
        'endpoint': '/fileinfo_mzml',
        'request_given': req_time
    })

    try:
        with global_lock:
            data = request.get_json(silent=True) or {}
            url = data.get("download_url")
            filename = data.get("filename")
            folder_id = data.get("foldername")
            if not url or not data:
                remove_folder(output_folder_path)
                abort(400, description="missing 'url' in JSON body/empty JSON")
            output_folder_path = os.path.join(working_dir, folder_id)
            new_path = fetch_file(url=url, filename=filename, folder_id= folder_id)
            
            if not os.path.isfile(new_path):
                pending_requests.popleft()
                remove_folder(output_folder_path)
                return jsonify({'error': 'Not a valid file'}), 400

            if filename.lower().endswith('.mzml'):
                base_name = os.path.splitext(os.path.basename(new_path))[0]
                output_filename = base_name + '_validation_result.txt'
                output_filepath = os.path.join(output_folder_path, output_filename)
            else:
                pending_requests.popleft()
                remove_folder(output_folder_path)
                return jsonify({'error': 'File is not of mzML extention'}), 400

            request_logger.info('Input Path: %s', new_path)
            request_logger.info('Going for validation of input file')
            pending_requests.popleft()
            # Doing the actual conversion with the parmeters
            start_time = time.time()
            result= run(["FileInfo_anyuser", "-v", "-in",
                            new_path,"-out", output_filepath],
                            stdout=PIPE, stderr=PIPE, universal_newlines=True)
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)

            if result.stderr:
                remove_folder(output_folder_path)
                return jsonify({'error': 'Error executing file', 
                                'details': result.stderr,
                                'time_taken_sec': time_taken}), 500
            else:
                with open(output_filepath, 'r') as f:
                    content = f.read()
                clean_content = re.sub(r'\s+', ' ', content).strip()
                remove_folder(output_folder_path)
                return jsonify({'message': 'Validation Successful!!', 
                                'time_taken_sec': time_taken,
                                'output_message': clean_content}), 200


    except Exception as e:
        # Remove from pending queue if an error occurs
        if pending_requests:
            pending_requests.popleft()
        remove_folder(output_folder_path)
        request_logger.error('Exception occurred: {}'.format(str(e)))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    

# File Convert and Validation of the File
@app.route('/fileconvert_mzml', methods=['POST'])
def file_convert():
    global request_counter
    request_counter += 1
    req_id = request_counter
    req_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Add request to pending queue
    pending_requests.append({
        'id': req_id,
        'endpoint': '/fileconvert_mzml',
        'request_given': req_time
    })
    
    try:
        with global_lock:
            data = request.get_json(silent=True) or {}
            url = data.get("download_url")
            filename = data.get("filename")
            folder_id = data.get("foldername")
            config_raw = data.get("config") or ''
            config = re.sub(r'(-o|--outdir|string)\s+\S+', '',config_raw).strip()
            if not url:
                remove_folder(output_folder_path)
                abort(400, description="missing 'url' in JSON body")
            
            output_folder_path = os.path.join(working_dir, folder_id)
            new_path = fetch_file(url=url, filename=filename, folder_id= folder_id)

            if not new_path:
                pending_requests.popleft()
                remove_folder(output_folder_path)
                return jsonify({'error': 'No path provided'}), 400
            
            if not os.path.isfile(new_path):
                pending_requests.popleft()
                remove_folder(output_folder_path)
                return jsonify({'error': 'Not a valid file'}), 400
            
            if filename.lower().endswith('.mzml'):
                base_name = os.path.splitext(os.path.basename(new_path))[0]
                output_filename = base_name + '_FileConverter_output.mzML'
                output_filename_validation = base_name + '_FileConverter_output_validation_result.txt'
                output_filepath = os.path.join(output_folder_path, output_filename)
                output_filepath_validation = os.path.join(output_folder_path, output_filename_validation)
            else:
                pending_requests.popleft()
                remove_folder(output_folder_path)
                return jsonify({'error': 'File is not of mzML extention'}), 400


            pending_requests.popleft()
            # Doing the actual conversion with the parmeters
            start_time = time.time()
            result= run(["FileConverter_anyuser","-write_scan_index", "true", "-in",
                        new_path,"-out",output_filepath],
                        stdout=PIPE, stderr=PIPE, universal_newlines=True)
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)

        
            # checking if there is any error in FileConvert process
            if result.stderr:
                remove_folder(output_folder_path)
                return jsonify({'error': 'Error in FileConvert process', 
                                'details': result.stderr,
                                'time_taken_fileconvert_sec': time_taken}), 500
            else:
                with open(output_filepath, 'rb') as fh:
                    upload_fileobj(fh, output_filename, folder_id)
                download_url = download_file(filename=output_filename, file_id= folder_id)
                # Doing the validation of the converted File
                start_time_validation = time.time()
                result_validation = run(["FileInfo_anyuser", "-v", "-in",
                                        output_filepath, "-out", output_filepath_validation],
                                        stdout=PIPE, stderr=PIPE, universal_newlines=True)
                end_time_validation = time.time()
                time_taken_validation = round(end_time_validation - start_time_validation, 2)

                if result_validation.stderr:
                    remove_folder(output_folder_path)
                    return jsonify({'error': 'FileConvert Success but Error in Validation file', 
                                'details': result_validation.stderr,
                                'time_taken_fileconvert_sec': time_taken,
                                'time_taken_validation_sec': time_taken_validation}), 500
                else:
                    with open(output_filepath_validation, 'r') as f:
                        content = f.read()
                    clean_content = re.sub(r'\s+', ' ', content).strip()
                remove_folder(output_folder_path)    
                return jsonify({'message': 'Fileconvert + Validation Successful!!', 
                                'time_taken_fileconvert_sec': time_taken,
                                'time_taken_validation_sec': time_taken_validation,
                                'Validation_message':clean_content,
                                'mzml_fileconvert_download_link': download_url,
                                'fileconvert_filename': output_filename }), 200
    except Exception as e:
        if pending_requests:
            pending_requests.popleft()
        remove_folder(output_folder_path)
        request_logger.error('Exception occurred: {}'.format(str(e)))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
            


# Endpoint to check the status of pending requests:
@app.route('/validation_status', methods=['GET'])
def status():
    return jsonify({
        'pending_count': len(pending_requests)
        #'pending_requests': list(pending_requests)
    })



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
    app.run(host='0.0.0.0', port=3000, debug=False)