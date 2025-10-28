import os
from subprocess import PIPE, run
import time

#
# Setting up the working directory
#

os.path.dirname(os.getcwd())
main_path = os.getcwd()
sec_path = "example_file"
folder_path = os.path.join(main_path, sec_path)
conversion_path = "example_file/mzml_conversion"
validation_path = "example_file/mzml_validation"
os.chdir(main_path)


class validation_stage:
    def __init__(self):
        self.result = None
        self.folder = None
        self.file = None
        self.filepath = None
        self.file_name = None
        self.int = 0
    def validation_process(self):
        for self.folder in os.listdir(os.path.join(main_path, sec_path)):
            #if self.folder in directory_names:
            if self.folder != 'mzml_conversion' and self.folder != 'mzml_validation' and self.folder !='.gitkeep':
                #print(self.folder)
                # carrying out the validation process using a bash command
                for file in os.listdir(os.path.join(folder_path, self.folder)):
                    if "_validation_file.yml" in file:
                        #self.filepath = os.path.abspath(file)
                        self.filepath = os.path.join(os.path.join(folder_path, self.folder), file)
                        os.chdir(main_path)
                        self.file_name = file.split("_validation_file.yml")[0]
                        bash_file_name = "validation_exec_" + self.file_name + ".sh"
                        with open(bash_file_name, "w") as f:
                            f.write('#!bin/bash\n')
                            f.write(f'\ncwltool validation.cwl {self.filepath}')
                        start_time = time.time()
                        self.result = run(["sh", bash_file_name], stdout=PIPE, stderr=PIPE, universal_newlines=True)
                        end_time = time.time()
                        diff_time = end_time -  start_time
                        #if "Failed" in self.result.stderr:
                        # Filling up the intermediate steps with metadata for junit report
                        for file2 in os.listdir(os.path.join(main_path, validation_path)):
                            if self.file_name in file2:
                                tmp_error_report = file2
                                break
                            else:
                                continue
                        standard_error_report = self.result.stderr.replace("Error: No such object: biocontainers/openms:2.2.0_cv5","")
                        #standard_error_report = self.result.stderr
                        self.validation_file_name = self.file_name + "_validation_result.txt"
                        
                        current_folder = os.path.join(folder_path,self.folder)
                        error_check_file_path = os.path.join(current_folder,self.validation_file_name)
                        if os.path.exists(error_check_file_path):
                            with open(error_check_file_path, 'r') as file:
                                content = file.readlines()
                                for line in content:
                                    if "Failed - errors are listed above!" in line:
                                        print(f'Standard Error:\n------------------\n {self.result.stderr}')
                                        print(f'Validation Report:\n------------\n{self.file_name} ::-->FAIL')
                                        os.chdir(os.path.join(main_path, validation_path))
                                        with open(tmp_error_report, 'a') as f:
                                            f.write('\nfailure')
                                            f.write(f'\n{diff_time}')
                                        tmp_error_report2 = self.file_name + "_stderr_report.txt"
                                        with open(tmp_error_report2, "w") as f:
                                            f.write(self.result.stderr)
                                        os.chdir(main_path)
                                        break
                                    
                                    elif "Success - the file is valid!" in line:            
                                        print(f'Standard Error:\n------------------\n {self.result.stderr}')
                                        print(f'Validation Report:\n------------\n{self.file_name} ::-->SUCCESS')
                                        os.chdir(os.path.join(main_path, validation_path))
                                        with open(tmp_error_report, 'a') as f:
                                            f.write('\nsuccess')
                                            f.write(f'\n{diff_time}')
                                        os.chdir(main_path)
                                        break

                        #if "error" in standard_error_report.lower():
                        #    print(f'Standard Error:\n------------------\n {self.result.stderr}')
                        #    print(f'Validation Report:\n------------\n{self.file_name} ::-->FAIL')
                        #    os.chdir(os.path.join(main_path, validation_path))
                        #    with open(tmp_error_report, 'a') as f:
                        #        f.write('\nfailure')
                        #        f.write(f'\n{diff_time}')
                        #    tmp_error_report2 = self.file_name + "_stderr_report.txt"
                        #    with open(tmp_error_report2, "w") as f:
                        #        f.write(self.result.stderr)
                        #    os.chdir(main_path)
                        #else:
                        #    print(f'Standard output:\n------------------\n {self.result.stdout}')
                        #    print(f'Standard Error:\n------------------\n {self.result.stderr}')
                        #    print(f'Validation Report:\n------------\n{self.file_name} ::-->SUCCESS')
                        #    os.chdir(os.path.join(main_path, validation_path))
                        #    with open(tmp_error_report, 'a') as f:
                        #        f.write('\nsuccess')
                        #        f.write(f'\n{diff_time}')
                        #    os.chdir(main_path)
                       
                        os.remove(bash_file_name)


test = validation_stage()
test.validation_process()
os.chdir(main_path)