import os
import time
from subprocess import PIPE, run

#
# (i) Setting up the working directory
#

os.path.dirname(os.getcwd())
main_path = os.getcwd()
sec_path = "intermediate_files"
conversion_path = "example_file/mzml_conversion"
validation_path = "example_file/mzml_validation"
os.chdir(main_path)

class conversion_stage:
    def __init__(self):
        self.result = None
        self.file = None

    def create_bash(self):
        for self.file in os.listdir(os.path.join(main_path, sec_path)):
            # Creating an intermediate bash script  to execute the cwl command
            file_name = self.file.replace("msconvert_workflow_file_", "")
            bash_file_name = "cwl_exec_" + os.path.splitext(file_name)[0] + ".sh"
            with open(bash_file_name, "w") as f:
                f.write('#!bin/bash\n')
                f.write(f'cd {os.path.join(main_path, sec_path)}\n')
                f.write(f'cp {self.file} {main_path}')
                f.write(f'\ncd ..')
                f.write(f'\ncwltool --no-read-only msconvert_workflow_main.cwl {self.file}')
            start_time = time.time()
            self.result = run(["sh", bash_file_name], stdout=PIPE, stderr=PIPE, universal_newlines=True)
            end_time = time.time()
            diff_time = end_time - start_time
            if self.result.stdout:
                print(f'Standard Output:\n--------------------\n{self.result.stdout}')
            tmp_error_report = os.path.splitext(file_name)[0] + "_mzML_conversion_op.txt"
            standard_error_report = self.result.stderr.replace("Error: No such object: chambm/pwiz-skyline-i-agree-to-the-vendor-licenses","")
            # If "error" is present in the standard error, then the standard error is printed out 
            # and corresponding data ( as success or failure) on intermediate files 
            if "error" in standard_error_report.lower() :
                print(f'Standard Error:\n--------------------\n {self.result.stderr}')
                print(f'mzML conversion of the file\n{self.file} ::--> fail')
                os.chdir(os.path.join(main_path, conversion_path))
                with open(tmp_error_report, 'a') as f:
                    f.write('\nfailure')
                    f.write(f'\n{diff_time}')
                tmp_error_file_name = os.path.splitext(file_name)[0] + "_stderr_report.txt"
                with open(tmp_error_file_name, "w") as f:
                    f.write(self.result.stderr)
                os.chdir(main_path)
            else:
                print(f'mzML conversion of the file\n{self.file} ::--> success')
                os.chdir(os.path.join(main_path, conversion_path))
                with open(tmp_error_report, 'a') as f:
                    f.write('\nsuccess')
                    f.write(f'\n{diff_time}')
                os.chdir(main_path)

            os.remove(bash_file_name)



test = conversion_stage()
test.create_bash()
os.chdir(main_path)