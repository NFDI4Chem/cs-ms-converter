#!bin/bash

echo "The current directory is: "
main_location=$PWD

ARGUMENT=$1
echo "-------------------------------"
echo "Using the Fileconvert to change the file"
echo "-------------------------------"

cp $ARGUMENT $PWD
filename=$(basename "$ARGUMENT")
file_base_name=${filename%.*}
file_output=$file_base_name"_FileConverter_output.mzML"
result_output=$file_base_name"_FileConverter_output_validation_result.txt"
validation_output=$file_base_name"_validation_result.txt"

echo "-------------------------------"
echo "Validation of mzML File"
echo "-------------------------------"

FileInfo_anyuser -v -in $filename -out $validation_output


echo "-------------------------------"
echo "FileConverter of the mzML File"
echo "-------------------------------"

FileConverter_anyuser -write_scan_index true -in $filename -out $file_output


if ls "$PWD"/*_FileConverter_output.mzML >/dev/null 2>&1; then
  echo "-------------------------------"
  echo"Validating the Converted File"
  echo "-------------------------------"
  FileInfo_anyuser -v -in $file_output -out $result_output
  rm -rf $filename
  ls -la
else
    echo "Problem in FileConverter_anyuser found!!"
fi