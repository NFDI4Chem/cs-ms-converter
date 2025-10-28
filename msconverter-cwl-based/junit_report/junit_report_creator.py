import xml.etree.ElementTree as ET
import os

os.path.dirname(os.getcwd())
main_path = os.getcwd()
os.chdir(main_path)


class junit_report:
    def __init__(self):
        self.root = None
        self.i = 0

    def write_root(self):
        root = ET.Element('testsuites')
        return root

    def conversion_write_report(self):
        root = self.write_root()
        testsuite = ET.SubElement(root, 'testsuite', name='RAWFileConversion')
        directory = 'example_file/mzml_conversion'
        content = None
        i = 0
        for file in os.listdir(directory):
            if "_mzML_conversion_op.txt" in file:
                filename = file.split("_mzML_conversion_op.txt")[0]
                #print(filename)
                base_filename = filename.split(".")[0]
                with open(os.path.join(directory, file), 'r') as f:
                    content = f.readlines()
                if content[1].strip() == "success":
                    temp_name = "testcase_"+str(i)
                    globals()['testcase_%s' % i] = ET.SubElement(testsuite, 'testcase', name=content[0].strip(),
                                                                 classname='RAWFileConversion',
                                                                 time=content[2].strip())
                    print('testcase_%s' % i)
                else:
                    #print(f'{content}')
                    failed_file = base_filename + "_stderr_report.txt"
                    failed_file_path = os.path.join(directory, failed_file)
                    temp_name = "testcase_" + str(i)
                    globals()['testcase_%s' % i] = ET.SubElement(testsuite, 'testcase', name=content[0].strip(),
                                                                 classname='RAWFileConversion',
                                                                 time=content[2].strip())
                    if os.path.exists(failed_file_path):
                        with open(failed_file_path, 'r') as f:
                            failed_message = f.readlines()
                        globals()['testcase_a_%s' % i] = ET.SubElement(globals()['testcase_%s' % i], 'failure',
                                                                       message=self.preetify_message(str(failed_message)),
                                                                       type="File Format not correct")
                    else:
                        globals()['testcase_a_%s' % i] = ET.SubElement(globals()['testcase_%s' % i], 'failure', message="error404",
                                                                   type="File Format not correct",
                                                                   time=content[2].strip())

            else:
                print(f"the file: {file} cannot be converted")

            i += 1
        #print(testcase_2)
        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write('python_conversion.xml', encoding="UTF-8", xml_declaration=True)
        print("junit report for conversion: Completed!!")

    def validation_write_report(self):
        root = self.write_root()
        testsuite = ET.SubElement(root, 'testsuite', name='ValidationTesting')
        directory = 'example_file/mzml_validation'
        content = None
        i = 0
        for file in os.listdir(directory):
            if "_mzML_validation_op.txt" in file:
                filename = file.split("_mzML_validation_op.txt")[0]
                #print(filename)
                with open(os.path.join(directory, file), 'r') as f:
                    content = f.readlines()
                if len(content) > 1 and content[1].strip() == "success":
                    temp_name = "testcase_" + str(i)
                    file1 = filename+"_validation_result.txt"
                    temp_folder_path= "example_file/" + filename
                    failed_file_path = os.path.join(temp_folder_path, file1)
                    if os.path.exists(failed_file_path):
                        with open(failed_file_path, 'r') as f:
                            content_path = f.read()
                            if "Failed" in content_path:
                                globals()['testcase_%s' % i] = ET.SubElement(testsuite, 'testcase', name=content[0].strip(),
                                                                 classname='RAWFileConversion',time=content[2].strip())
                                globals()['testcase_a_%s' % i] = ET.SubElement(globals()['testcase_%s' % i], 'failure',
                                                                               message=self.preetify_message(str(failed_message)),
                                                                               type="Validation Error")
                            else:
                                globals()['testcase_%s' % i] = ET.SubElement(testsuite, 'testcase', name=content[0].strip(),
                                                                 classname='RAWFileConversion',time=content[2].strip())

                    else:
                        globals()['testcase_%s' % i] = ET.SubElement(testsuite, 'testcase', name=content[0].strip(),
                                                                 classname='RAWFileConversion',time=content[2].strip())
                    #print('testcase_%s' % i)
                else:
                    #print(f'{content}')
                    temp_name = "testcase_" + str(i)
                    globals()['testcase_%s' % i] = ET.SubElement(testsuite, 'testcase', name=content[0].strip(),
                                                                 classname='RAWFileConversion', time="0")
                    globals()['testcase_a_%s' % i] = ET.SubElement(globals()['testcase_%s' % i], 'failure',
                                                                   message="Failed - errors! mzML conversion not successful in earlier step",
                                                                   type="Validation part Skipped")

            else:
                print(f"the file: {file} cannot be converted")

            i += 1
        #print(testcase_1)
        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write('python_validation.xml', encoding="UTF-8", xml_declaration=True)
        print("junit report for validation: Completed!!")

    def preetify_message(self,message):
        message = message.replace("\\n", "").replace("\\\\\n", "").replace("\n", "").replace("\\\\","")
        return message