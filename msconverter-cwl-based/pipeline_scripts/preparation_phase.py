import os

## Requirements
## The folders: intermediate_files, mzml_conversion, mzml_validation are created beforehand using the CI/CD-editor
##
# Main Objective of Module:
# a) Create an intermediate files  (.yml ) for easy conversion to mzML
# b) Create another intermediate files : "*_mzml_conversion_op.txt" and "*_mzml_validation_op.txt"  which are metadata files for Junit
#    report
#
#

#
#Here:
# (i)- The working directory is set 
# (ii)- The names of instrument as a list is provided on variable "directory names".
#
os.path.dirname(os.getcwd())
directory_names = ["MS+Thermo_Finnigan", "MS+Thermo_Scientific", "MS+Agilent_MassHunter_D", "MS+Sciex_WIFF"]
#directory_names = ["MS+Sciex_WIFF", "MS+Thermo_Finnigan"]
main_dir = os.getcwd()
sub_dir = "example_file"
int_dir = "intermediate_files"
work_path = os.path.join(main_dir, sub_dir)
execution_path = os.path.join(main_dir, "main_cwl.sh")
config_path = os.path.join(main_dir,"config.txt")
os.chdir(work_path)


class preparation:
    def __int__(self):
        self.root = None

    def create_intermediate_files(self):
        os.chdir(work_path)
        for fld in directory_names:
            print("-----------------------")
            # Displaying the instrument name for which further processing will be carried out.
            print(fld)
            print("-----------------------")
            if fld in os.listdir(os.getcwd()):
                print(f'Working on the instrument "{fld}"::')
                os.chdir(fld)
                for file in os.listdir(os.getcwd()):
                    if (os.path.isfile(file) or os.path.isdir(file)) and file!= ".gitkeep":
                        tmp_file_basename = os.path.splitext(file)[0]
                        tmp_file_name = tmp_file_basename + ".mzML"
                        os.chdir(os.path.join(main_dir, sub_dir))
                        # Creating intermediate files for junit xml report (both conversion and validation)
                        report_conversion = "mzml_conversion/" + tmp_file_basename + "_mzML_conversion_op.txt"
                        report_validation = "mzml_validation/" + tmp_file_basename + "_mzML_validation_op.txt"

                        with open(report_conversion, 'w') as f:
                            f.write(file)

                        with open(report_validation, 'w') as f:
                            f.write(tmp_file_name)
                        #print(os.getcwd())
                        os.chdir(main_dir)

                        # Creating intermediate .yml file for "conversion" stage
                        tmp_intermediate_file = "intermediate_files/msconvert_workflow_file_" + tmp_file_basename + ".yml"
                        file_location = os.path.join(work_path, fld)
                        with open(tmp_intermediate_file, 'w') as g:
                            g.write(f'in_file1:\n    class: File\n    path: {execution_path}\n')
                            g.write(f'in_file2:\n    class: File\n    path: {config_path}\n')                 
                            g.write('in_file:\n    class: File\n    format: http://edamontology.org/format_3245\n')
                            g.write(f'    path: {os.path.join(file_location, file)}')
                        print(f'The Intermediate file Completed: {file} ')
                        os.chdir(os.path.join(work_path, fld))
                        #print(f'The name of the file is {os.path.splitext(file)[0]}')
                    else:
                        print(f'Skipping the file: {file}')
            else:
                print("No files found in the registered list")
            os.chdir(work_path)


test = preparation()
test.create_intermediate_files()
os.chdir(main_dir)