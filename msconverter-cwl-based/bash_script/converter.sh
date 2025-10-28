#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Error: Please provide your input and output path in following fashion."
    echo "Expected Command: bash converter.sh <input_path> <output_path>"
    exit 1
fi


# INPUT PARAMETERS
MAIN_FOLDER=$1
CONVERTED_FILE_PATH=$2
URL="https://nfdi4chem-msconverter.zih.tu-dresden.de/msconvert_convert"


# TO KEEP TRACK OF FILE NUMBERS
NUMBER=1
echo "The Main path is : $MAIN_FOLDER"

#ls -la $MAIN_FOLDER

echo "-----------------------"
# Checking if the folder is empty of not
if [ "$(ls -A "$MAIN_FOLDER")" ]; then
  echo "Starting Conversion process on folder:"
  echo "${MAIN_FOLDER}"
  echo "The Folder is non-empty"
  # Looping to each and every files
  for item in "$MAIN_FOLDER"/*; do
  # Converstion process For masshunter.d files
    if [ -d "$item" ]; then
      echo "Conversion Process Number:${NUMBER}"
      NUMBER=$((NUMBER+1))
      echo "Folder name: $(basename "$item")"
      if [[ "$(basename "$item")" =~ \.(d|D)$ ]]; then
        echo "-----------------------"
        echo ""
        echo "Compressing the folder: $(basename "$item") to tar"
        cd $MAIN_FOLDER
        base_FILE=$(echo "$(basename "$item")" | sed -E 's/\.[Dd]$//')
        tar -cvf $MAIN_FOLDER/$(basename "$item").tar $(basename "$item")
        curl -X 'POST'  ${URL} -H 'accept: application/json' -H 'Content-Type: multipart/form-data' -F "main_file=@$(basename "$item").tar" -F 'parameters= ' -o ${CONVERTED_FILE_PATH}/${base_FILE}.mzML 2>&1
        rm $MAIN_FOLDER/$(basename "$item").tar 
        cd ..
        echo "-----------------------"
      fi
    elif [ -f "$item" ]; then
    # Conversion process for wiff files
      if [[ "$(basename "$item")" =~ \.(wiff|Wiff|WIFF)$ ]]; then
         echo "-----------------------"
        echo "Conversion Process Number:${NUMBER}"
        NUMBER=$((NUMBER+1))
        echo "Filename: $(basename "$item")"
        temp_file="$(basename "${item}").scan"
        #echo "the temp file is $temp_file"
        if [ -e "$MAIN_FOLDER/$temp_file" ]; then
          echo "-----------------------" 
          echo "Found the .scan file as well." 
          echo "Now compressing the file to tar"
          cd $MAIN_FOLDER
          base_FILE=$(echo "$(basename "$item")" | sed -E 's/\.[Ww][Ii][Ff][Ff]$//')
          tar -cvf $MAIN_FOLDER/$(basename "$item").tar $(basename "$item") $temp_file
          curl -X 'POST'  ${URL} -H 'accept: application/json' -H 'Content-Type: multipart/form-data' -F "main_file=@$(basename "$item").tar" -F 'parameters= '  -o ${CONVERTED_FILE_PATH}/${base_FILE}.mzML  2>&1 
          rm $MAIN_FOLDER/$(basename "$item").tar
          cd ..
          echo "-----------------------"
        else
          echo "missing the .scan file "
        fi
      elif [[ "$(basename "$item")" =~ \.(scan|SCAN|Scan)$ ]]; then
        echo "-----------------------"
        echo "Skipping the file: $(basename "$item")"
        echo "-----------------------"
      # Conversion process for RAW files
      elif [[ "$(basename "$item")" =~ \.(raw|RAW|Raw)$ ]]; then
        echo "-----------------------"
        echo "Conversion Process Number:${NUMBER}"
        NUMBER=$((NUMBER+1))
        echo "RAW file found: $(basename "$item")"
        FILE="${MAIN_FOLDER}/$(basename "$item")"
        base_FILE=$(echo "$(basename "$item")" | sed -E 's/\.[Rr][Aa][Ww]$//')
        #echo "$base_FILE"
        curl -X 'POST'  ${URL} -H 'accept: application/json' -H 'Content-Type: multipart/form-data' -F "main_file=@${FILE}" -F 'parameters= ' -o ${CONVERTED_FILE_PATH}/${base_FILE}.mzML 2>&1
        echo "-----------------------"
      else
        echo "-----------------------"
        echo "skipping the file: $(basename "$item")"
        echo "-----------------------"
      fi
    fi
  done
else
  echo "The Folder contains no files"

fi
echo "-----------------------"
echo "TOTAL FILE Undergone Conversion: $((NUMBER-1))"
echo "-----------------------"
echo "-----------------------"
