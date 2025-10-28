from flask import Flask, request, jsonify
from typing import BinaryIO, Union
from pathlib import Path
import tarfile
import re
import os
import logging
from threading import Lock
import time
from collections import deque
from subprocess import PIPE, run
import shlex
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


# Global lock and pending requests queue
global_lock = Lock()
pending_requests = deque()
request_counter = 0

# Endpoint for conversion to mzML fof Raw or will file
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
            filename = data.get("filename")
            folder_id = data.get("foldername")
            config_raw = data.get("config") or ''
            config = re.sub(r'(?:-o|--outdir)\s+\S+|\bstring\b', '', config_raw, flags=re.I).strip()

            
            request_logger.info(f'Received request to check folder: {filename}')
            base_path = "input_files/" + folder_id + filename
            output_folder_path = os.path.join(working_dir, folder_id)

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
                        #tar_folder_path = Path(os.path.join(output_folder_path,file))
                        #if file.lower().endswith('.tar'):
                        #    new_path = tar_folder_path.with_suffix('')
                        #elif file.lower().endswith(('.tar.gz', '.tar.xz')):
                        #    new_path = tar_folder_path.with_suffix('').with_suffix('')
                        #else:
                        dirs = [d for d in Path(output_folder_path).iterdir() if d.is_dir()]
                        if (n := len(dirs)) != 1:
                            raise ValueError(f"Expected exactly one folder in {output_folder_path}, found {n}")
                        new_path = dirs[0]
                        if not os.path.isdir(new_path):
                            pending_requests.popleft()
                            remove_folder(output_folder_path)
                            return jsonify({'error': 'Neither a valid file nor a folder'}), 400

            print(f'Input Path: {new_path}')
            
            # acually doing the conversion with the parameters
            print("Starting Conversion Process!!")
            pending_requests.popleft()
            start_time = time.time()
            cmd = ["wine_anyuser", "msconvert", new_path, "-o", output_folder_path] 
            if config:
                cmd[2:2] = shlex.split(config)     # slip config flag before "-o ..."
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)

            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            print("Successfully converted the file!!")
            output_file_path, outputfilename = output_filepath(new_path)

            if result.stderr:
                return jsonify({'error': 'Error executing file', 
                                'details': result.stderr,
                                'time_taken_sec': time_taken}), 500
            else:
                #output_file_path = Path(output_filepath(filename))
                return jsonify({'message': 'Conversion Successful!!', 
                                'time_taken_sec': time_taken,
                                'output_file_path': output_file_path,
                                'mzml_outputfile_name': outputfilename}), 200
    except Exception as e:
        # Remove from pending queue if an error occurs
        if pending_requests:
            pending_requests.popleft()
        request_logger.error('Exception occurred: {}'.format(str(e)))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    finally:
        delete_old_folder(working_dir)



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
    return output_file_path , output_file



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
    



def remove_folder(abs_path: Union[str, Path]) -> None:
    path = Path(abs_path)

    if not path.is_absolute():
        raise ValueError("Path must be absolute – got: {}".format(path))

    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    shutil.rmtree(path)


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



def delete_old_folder(root: Union[Path,str]) -> None:
    """
    Recursively delete every *directory* under `root` whose mtime
    is older than 1 hour.  Files directly under `root` are left untouched.
    """
    root = Path(root)
    if not root.is_dir():
        return

    now = time.time()
    one_hour = 3600  # seconds

    for item in root.iterdir():
        if item.is_dir() and (now - item.stat().st_mtime) > one_hour:
            shutil.rmtree(item, ignore_errors=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False)