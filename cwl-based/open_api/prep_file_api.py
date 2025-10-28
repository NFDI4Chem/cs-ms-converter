import os
import shutil

os.path.dirname(os.getcwd())
main_dir = os.getcwd()

sub_dir = "input_files"
int_dir = "intermediate_files_"
int_path = os.path.join(main_dir, int_dir)
work_path = os.path.join(main_dir, sub_dir)
os.chdir(main_dir)
execution_path = os.path.join(main_dir, "main_cwl.sh")
config_path = os.path.join(main_dir,"config.txt")


class preparation:
    def __init__(self, folder_name, config_file_params=None):
        self.root = None
        self.folder_name =  folder_name
        self.config_file_params = config_file_params


    def current_path(self):
        print(main_dir)

    def cleanup_files(self):
        for file in os.listdir(int_path):
            if os.path.isfile(os.path.join(int_path, file)):
                os.remove(os.path.join(int_path, file))
            if os.path.isdir(os.path.join(int_path, file)):
                shutil.rmtree(os.path.join(int_path, file))

        for file in os.listdir(work_path):
            if os.path.isfile(os.path.join(work_path, file)):
                os.remove(os.path.join(work_path, file))
            if os.path.isdir(os.path.join(work_path, file)):
                shutil.rmtree(os.path.join(work_path, file))
        os.chdir(main_dir)

    def create_intermediate_files(self):
        new_work_path = os.path.join(work_path, self.folder_name)
        os.chdir(new_work_path)
        for file in os.listdir(os.getcwd()):
            if (os.path.isfile(file) or os.path.isdir(file)) and file != ".gitkeep":
                tmp_file_basename = os.path.splitext(file)[0]
                # os.chdir(os.path.join(main_dir, sub_dir))
                os.chdir(main_dir)

                tmp_intermediate_file = int_dir + "/msconvert_workflow_file_" + self.folder_name + "_"+ tmp_file_basename + ".yml"
                # file_location = work_path
                with open(tmp_intermediate_file, 'w') as g:
                    g.write(f'in_file1:\n    class: File\n    path: {execution_path}\n')
                    g.write(f'in_file2:\n    class: File\n    path: {self.config_file_params}\n')
                    g.write('in_file:\n    class: File\n    format: http://edamontology.org/format_3245\n')
                    g.write(f'    path: {os.path.join(new_work_path, file)}')
                print(f'The Intermediate-File for the file : {file} is COMPLETED.')
                os.chdir(new_work_path)
            else:
                print(f'No files or correct format found')

            os.chdir(new_work_path)
        os.chdir(main_dir)

#est = preparation("qkxbos91")
#test.create_intermediate_files()
#os.chdir(main_dir)
