import os
from subprocess import PIPE, run
import time

#
# Setting up the working directory
#

os.path.dirname(os.getcwd())
main_path = os.getcwd()
ter_path = "input_files"

int_path = os.path.join(main_path, ter_path)
validation_path = os.path.join(main_path,"File_convert_validate.cwl")
os.chdir(main_path)


class FileConverter():
    def __init__(self, folder_name):
        self.result = None
        self.folder = None
        self.file = None
        self.filepath = None
        self.folder_name = folder_name
        self.new_ter_path = os.path.join(ter_path, self.folder_name)

    def cleanup_old_files(self):
        for file in os.listdir(int_path):
            if os.path.isfile(os.path.join(int_path, file)):
                os.remove(os.path.join(int_path, file))
            if os.path.isdir(os.path.join(int_path, file)):
                os.rmdir(os.path.join(int_path, file))
        os.chdir(main_path)

    def create_fileconverter_file(self):
        for file in os.listdir(os.path.join(main_path, self.new_ter_path)):
            if ".mzML" in file:
                file_path = os.path.join(os.path.join(main_path, self.new_ter_path), file)
                file_name = file.split(".mzML")[0]
                os.chdir(os.path.join(main_path, self.new_ter_path))
                file_name_yml = file_name + "_fileconverter_file.yml"
                bash_file = os.path.join(main_path,"fileconverter_cwl.sh")
                if os.path.isfile(os.path.join(os.path.join(main_path, self.new_ter_path), file_name_yml)):
                    os.remove(os.path.join(os.path.join(main_path, self.new_ter_path), file_name_yml))
                with open(file_name_yml, "w") as f:
                    f.write(f'in_file1:\n  class: File\n  path: {bash_file}\n')
                    f.write('in_file:\n  class: File\n  format: http://edamontology.org/format_3245\n')
                    f.write(f'  path: {file_path}\n')
                    f.write(f'in_dir: {os.path.join(main_path, self.new_ter_path)}')
                print(f'Creation of Intermediate file for FileConverter_Validation Process ::  Completed')
                os.chdir(main_path)

    def fileconverter_validation_process(self):
        self.create_fileconverter_file()
        for file in os.listdir(os.path.join(main_path, self.new_ter_path)):
            if "_fileconverter_file.yml" in file:
                self.filepath = os.path.join(os.path.join(main_path, self.new_ter_path), file)
                os.chdir(main_path)
                file_name = file.split("_fileconverter_file.yml")[0]
                bash_file_name = "validation_exec_" + file_name + ".sh"
                with open(bash_file_name, "w") as f:
                    f.write('#!bin/bash\n')
                    f.write(f'\ncwltool {validation_path} {self.filepath}')
                start_time = time.time()
                self.result = run(["sh", bash_file_name], stdout=PIPE, stderr=PIPE, universal_newlines=True)
                end_time = time.time()
                diff_time = end_time - start_time
                print(f'Time taken: {diff_time}sec')
                if self.result.stdout:
                    print(f'Standard Output:\n--------------------------\n{self.result.stdout}')
                if "error" in self.result.stderr.lower():
                    print(f'Standard Error:\n------------------\n {self.result.stderr}')
                else:
                    print(f'Validation Report:\n------------\n{file_name} ::-->SUCCESS')
                    os.chdir(main_path)
                os.remove(bash_file_name)

        os.chdir(main_path)

#if __name__ == "__main__":
#    test = FileConverter("100000")
#    test.fileconverter_validation_process()
#    os.chdir(main_path)