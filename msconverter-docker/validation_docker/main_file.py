from flask import Flask, request, jsonify
from pathlib import Path
import tarfile
import re
import os
import logging
from threading import Lock
import time
from collections import deque
from subprocess import PIPE, run
from typing import Union
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
            filename = data.get("filename")
            folder_id = data.get("foldername")
            
            output_folder_path = os.path.join(working_dir, folder_id)
            new_path = os.path.join(output_folder_path, filename)
        
            # Creating a unique folder_id if provided
                        
            request_logger.info('Received request to check file: {}'.format(filename))
            base_path = "input_files/" + folder_id + filename
            
            #checking if the new_path is a valid_file
            if not filename:
                pending_requests.popleft()
                return jsonify({'error': 'No path provided'}), 400
            
            if not os.path.isfile(new_path):
                pending_requests.popleft()
                return jsonify({'error': 'Not a valid file'}), 400

            
            if filename.lower().endswith('.mzml'):
                base_name = os.path.splitext(filename)[0]
                output_filename = base_name + '_validation_result.txt'
                output_filepath = os.path.join(output_folder_path, output_filename)
            else:
                pending_requests.popleft()
                return jsonify({'error': 'File is not of mzML extention'}), 400
            
            pending_requests.popleft()

            # Doing the actual conversion with the parmeters
            start_time = time.time()
            result= run(["FileInfo_anyuser", "-v", "-in",
                            new_path,"-out", output_filepath],
                            stdout=PIPE, stderr=PIPE, universal_newlines=True)
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)

            if result.stderr:
                return jsonify({'error': 'Error executing file', 
                                'details': result.stderr,
                                'time_taken_sec': time_taken}), 500
            else:
                with open(output_filepath, 'r') as f:
                    content = f.read()
                clean_content = re.sub(r'\s+', ' ', content).strip()
                return jsonify({'message': 'Validation Successful!!', 
                                'time_taken_sec': time_taken,
                                'output_messge': clean_content}), 200
    except Exception as e:
        # Remove from pending queue if an error occurs
        if pending_requests:
            pending_requests.popleft()
        request_logger.error('Exception occurred: {}'.format(str(e)))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    
    finally:
        delete_old_folder(working_dir)
    

# Endpoint for conversion to mzML fof Raw or will file
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
            filename = data.get("filename")
            folder_id = data.get("foldername")

            request_logger.info('Received request to check file: {}'.format(filename))
            
            output_folder_path = os.path.join(working_dir, folder_id)
            output_filepath = os.path.join(output_folder_path, filename)
            
            #checking if the new_path is a valid_file
            if not filename:
                pending_requests.popleft()
                return jsonify({'error': 'No path provided'}), 400
            
            if not os.path.isfile(output_filepath):
                pending_requests.popleft()
                return jsonify({'error': 'Not a valid file'}), 400
            
            if filename.lower().endswith('.mzml'):
                new_path = os.path.join(output_folder_path,filename)
                base_name = os.path.splitext(filename)[0]
                output_filename = base_name + '_FileConverter_output.mzML'
                output_filename_validation = base_name + '_FileConverter_output_validation_result.txt'
                output_filepath = os.path.join(output_folder_path, output_filename)
                output_filepath_validation = os.path.join(output_folder_path, output_filename_validation)
            else:
                pending_requests.popleft()
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
                return jsonify({'error': 'Error in FileConvert process', 
                                'details': result.stderr,
                                'time_taken_fileconvert_sec': time_taken}), 500
            else:
                # Doing the validation of the converted File

                start_time_validation = time.time()
                result_validation = run(["FileInfo_anyuser", "-v", "-in",
                                        output_filepath, "-out", output_filepath_validation],
                                        stdout=PIPE, stderr=PIPE, universal_newlines=True)
                end_time_validation = time.time()
                time_taken_validation = round(end_time_validation - start_time_validation, 2)
                

                if result_validation.stderr:
                    return jsonify({'error': 'FileConvert Success but Error in Validation file', 
                                'details': result_validation.stderr,
                                'time_taken_fileconvert_sec': time_taken,
                                'time_taken_validation_sec': time_taken_validation}), 500
                else:
                    with open(output_filepath_validation, 'r') as f:
                        content = f.read()
                    clean_content = re.sub(r'\s+', ' ', content).strip()
                return jsonify({'message': 'Fileconvert + Validation Successful!!', 
                                'time_taken_fileconvert_sec': time_taken,
                                'time_taken_validation_sec': time_taken_validation,
                                'Validation_message':clean_content }), 200
    except Exception as e:
        if pending_requests:
            pending_requests.popleft()
        request_logger.error('Exception occurred: {}'.format(str(e)))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    finally:
        delete_old_folder(working_dir)


# Endpoint to check the status of pending requests:
@app.route('/validation_status', methods=['GET'])
def status():
    return jsonify({
        'pending_count': len(pending_requests)
        #'pending_requests': list(pending_requests)
    })


# Deleting the folder which are older than 1 hour

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
    app.run(host='0.0.0.0', port=3000, debug=False)