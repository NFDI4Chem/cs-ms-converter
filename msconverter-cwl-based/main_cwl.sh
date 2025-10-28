#!bin/bash

echo "The current directory is: "
main_location=$PWD

ARGUMENT=$1

config_file=$2
config=$(cat $config_file)

echo "The configuration set is: "
echo $config
echo "-------------------------------"
echo "Checking the Input"
echo "-------------------------------"
if [[ $ARGUMENT == *.tar ]]; then
    echo "$ARGUMENT is  a tar file"
    tar_name=$(basename "$ARGUMENT")
    location="${ARGUMENT%/*}"
    folder_name=${tar_name%.*}
    folder_path=$location
    main_file=$folder_name
    #echo "we are at this foler: $PWD"
    #echo "Before the tar: " && echo ""
    #ls -la $folder_path
    tar -xvf $ARGUMENT
    #echo "we are at this foler: $PWD"
    #echo "After the tar:" && echo ""
    if [ -d $PWD/$folder_name ]; then
      for file in $PWD/$folder_name/*;do
        if [[ "$file" =~ \.(wiff|WIFF|Wiff)$ ]]; then
          echo "Found the folder containing .wiff file"
          main_file=$file
        fi
      done
    else
      for file in $PWD/*; do
        if [[ "$file" =~ \.(wiff|WIFF|Wiff)$ ]]; then
          echo "Found  .wiff file"
          main_file=$file
        fi
      done 
    fi

elif [[ $ARGUMENT =~ \.(raw|RAW|Raw)$ ]]; then
    echo "Raw file found"
    cp $ARGUMENT $PWD
    tar_name=$(basename "$ARGUMENT")
    main_file=$tar_name
else
    cp $ARGUMENT $PWD
    tar_name=$(basename "$ARGUMENT")
    main_file=$tar_name
fi

wine64_anyuser msconvert $main_file $config

if ls "$PWD"/*.mzML >/dev/null 2>&1; then
    rm -rf $main_file
    rm -rf $folder_name
    rm -rf *.scan
    ls -la 
else
    echo "No mzML files found!!"
fi