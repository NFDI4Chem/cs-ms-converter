import os
import time
from subprocess import PIPE, run
#from loading_animation import Loader

#main_path = os.path.dirname(os.getcwd())
main_path = os.getcwd()
sec_path = "intermediate_files_"
ter_path = "input_files"
tertiary_path = os.path.join(main_path,ter_path)
cwl_path = os.path.join(main_path, "msconvert_workflow_main.cwl")
yml_path = os.path.join(main_path, "intermediate_files_")
os.chdir(main_path)

class conversion_stage:
    def __init__(self, folder_name):
        self.result = None
        self.file = None
        self.folder_name = folder_name

    def current_path(self):
        print(f'Current Path: {main_path}')
        print(f'current wd: {os.getcwd()}')



    def create_bash(self):
        for self.file in os.listdir(os.path.join(main_path, sec_path)):
            file_name = self.file.replace("msconvert_workflow_file_", "")
            if self.folder_name in file_name:
                bash_file_name = "cwl_exec_" + os.path.splitext(file_name)[0] + ".sh"
                with open(bash_file_name, "w") as f:
                    f.write('#!bin/bash\n')
                    #f.write(f'cd {os.path.join(main_path, sec_path)}\n')
                    #f.write(f'cp {self.file} {main_path}')
                    #f.write(f'\ncd ..')
                    f.write(f'\ncwltool --no-read-only {cwl_path} {os.path.join(yml_path, self.file)}')
                start_time = time.time()
                self.result = run(["sh", bash_file_name], stdout=PIPE, stderr=PIPE, universal_newlines=True)
                end_time = time.time()
                diff_time = end_time - start_time
                print(f'\nTime taken by server: {diff_time}sec')
                if self.result.stdout:
                    print(f'Standard Output:\n--------------------------\n{self.result.stdout}')
                if "error" in self.result.stderr.lower():
                    print(f'Standard Error:\n--------------------\n {self.result.stderr}')
                else:
                    print(f'mzML conversion of the file\n{self.file} ::--> SUCCESS')

                os.remove(bash_file_name)

        for file in os.listdir(os.path.join(main_path, sec_path)):
            if self.folder_name in file:
                os.remove(os.path.join(yml_path, file))

    def cleanup(self):
        for self.file in os.listdir(os.path.join(main_path, ter_path)):
            if os.path.isfile(os.path.join(tertiary_path, self.file)):
                os.remove(os.path.join(tertiary_path, self.file))
                print(f'File: {self.file} removed!')
            if os.path.isdir(os.path.join(work_path, self.file)):
                shutil.rmtree(os.path.join(work_path, self.file))
                print(f'Folder {self.file} has been removed!')
            #if os.path.isdir(os.path.join(tertiary_path, self.file)):
                #os.rmdir(os.path.join(tertiary_path, self.file))
                #print(f'Folder: {self.file} removed!')
        print("All files or folders are removed!!")


#if __name__ == "__main__":
    #loader = Loader("Loading with object...", "That was fast!", 0.05).start()
#    test = conversion_stage("100000")
#    test.create_bash()
    #loader.stop()
#    os.chdir(main_path)