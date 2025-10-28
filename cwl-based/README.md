# Mass Spectroscopy File Converter

## Introduction:

The integration of the latest machines and technologies, combined with a diverse array of existing systems, expands the range of data formats and types, thereby introducing new challenges. To effectively navigate these complexities, it is crucial to implement robust governance mechanisms that ensure seamless conversion of diverse data formats into standardized forms.<br /> <br />
The converter service is built on the Common Workflow Language (CWL), selected for its exceptional interoperability, portability, and reproducibility. The source code is housed in a GitLab repository, complete with a CI/CD pipeline that not only automates the generation of conversion and validation summary reports but also fosters community collaboration. These reports offer a detailed overview of the conversion and validation process, ensuring transparency and efficiency across various file formats.<br /> <br />
The repository includes all the necessary code to run a converter, which is built on Flask, adheres to the OpenAPI specification, and provides a REST API for seamless integration with other NFDI4Chem services. The entire system is also packaged in a Docker image for easy deployment, and with a Helm chart available to streamline deployment in Kubernetes environments. <br /> <br />
This repository is specifically designed to facilitate the conversion of mass spectrometry files from various formats into the mzML format.
<br />

## Requirements:
- Python version 3.9 or higher 
- docker [Instructions to install docker](https://docs.docker.com/engine/install/)
- cwltool [Instructions to install cwltool](https://github.com/common-workflow-language/cwltool)

<br />
There are three methods for using the converter:<br />

- [Local Installation](#local_installation)
- [Docker Usage](#docker_usage)
- [Kubernetes Deployment](#k8es_deployment)

## Overview

<details>
  <summary>Tab 1: Local Installation</summary>

1. Prerequisites: `python 3.9 or higher`
1. Clone the repository `git clone https://git.rwth-aachen.de/linsherpa/ms_converter.git`
1. Create a python virtual environment and activate it. [Tips to create a python vitrual environment](https://docs.python.org/3/library/venv.html)
1. Install necessary requirements `pip install -r requirements.txt`
1. Run the main file `rest_api.py` :
```python
python rest_api.py
```
or
```python
 flask --app rest_api.py run
```
1. The URL will be available on `http://localhost:5000/api-docs#` 

</details>

<details>
  <summary>Tab 2: Docker Usage</summary>

  1. Pulling the docker image:
    ```docker pull docker pull lincoln1010/mass_spectrometry_file_converter:v1```

1. Running the container:
    ```docker run --privileged -d -ti --name < name of the container > -p 5000:5000 lincoln1010/mass_spectrometry_file_converter:v1.0```

1. Enabling the docker in docker (which is necessary):
    ```docker exec < name of the container > dockerd >/tmp/docker.stdout 2>/tmp/docker.stderr &```

1. Copy extra parameters on config.txt file:
    - a : create a config.txt file with content , for example, --mzXML  (without any indentation)
    - b : ```docker cp < path to your config.txt file > < name of the container >:/app/config.txt```
      (copying the config.txt file to /app/config.txt inside the container)

1. The URL will be available on `http://localhost:5000/api-docs#` with RESTAPI

</details>

<details>
  <summary>Tab 3: Kubernetes Deployment</summary>
The deployment of Kubernetes instance is done via [Helm chart](https://helm.sh/)

1. For deployment of helm chart of ms converter, please follow guidelines of [Msconverter Helm Chart](https://git.rwth-aachen.de/linsherpa/msconverter-helmchart)

</details>

<!--
::Tabs

:::TabTitle Local Machine



:::TabTitle Docker Installation


:::TabTitle Kubernetes Deployment



::EndTabs -->

<!-- ## For docker-installation

- [Pulling the docker image]
    - Step1: docker pull docker pull lincoln1010/mass_spectrometry_file_converter:v1

- [Running the container]
    - Step2: docker run --privileged -d -ti --name \< name of the container \> -p 5000:5000 lincoln1010/mass_spectrometry_file_converter:v1.0

- [Enabling the docker in docker (which is necessary)]
    - Step 3: docker exec \< name of the container \> dockerd >/tmp/docker.stdout 2>/tmp/docker.stderr &

- [Copy extra parameters on config.txt file]
    - Step 4a : create a config.txt file with content , for example, --mzXML  (without any indentation)
    - Step 4b : docker cp  \< path to your config.txt file \> \< name of the container \>:/app/config.txt
      (copying the config.txt file to /app/config.txt inside the container)

- The URL will be available on http://localhost:5000/api-docs# with RESTAPI


## Installation of MS_File_Converter on local machine:
- Step1:Git clone the repository
- Step2: create a virtual environment at a certain directory (example test-folder).
    - Command: python -m venv <path to test-folder>
    - source <path to the test-folder>/bin/activate
- step3: install the required libraries from Requirements.txt in your virtual environment.
    - Command: pip install -r requirements.txt

- Run the API
    - Go iside the test_converter_service folder
    - Command:flask --app rest_api.py run    or  python3 rest_api.py


The api will be on localhost:5000/api-docs#  


## For usage of files on local PC

modify the .yml file (eg msconvert_yml_file.yml)

>in_file1: <br />  
>class: File <br />
>path: main_cwl.sh <br />
>in_file: <br />
>class: File <br />
>path: test_files/MS_EI-MS_Linderazulen_03.D.tar # Add your file location <br />
>format: http://edamontology.org/format_3245 <br />

Command Used: cwltool --no-read-only msconvert_workflow_main.cwl msconvert_yml_file.yml -->


## MS-Converter Server:
If the server has been deployed correctly following the instructions, then the following image would be seen.

[Mass Spectrometry File Converter](images/msconverter_open_api_specification.png)

It consists of three functions:

#### a. msconvert:Conversion
The aim of conversion is to convert a format (in this case a Mass Spectrometry File) into a standardized (mzML) format. <br />
The converter is based on [proteowizard image](https://github.com/ProteoWizard/container) <br />
Input Files:
It works for three types of input.
1. Folder with `.D` or `.d` extention: <br /> 
The folder needs to be converted to `.tar` extention with maintaining the name `< name of folder >.d.tar` <br /> 
2. File with `.RAW` or `.raw` extention: <br />
The File can be directly used  for conversion. <br /> 
3. File that requires another secondary file i.e. `.wiff and .wiff.scan` extention.<br />
Both of the files need to be compressed together into `.tar` extention. <br /> 

#### b. FileInfo:Validation
 The input file for it is file with extention `.mzML`. 
 The validation is based on [FileInfo command from Openms](https://www.openms.org/documentation/html/TOPP_FileInfo.html)
 The image used for validation is [biocontainers/openms](https://hub.docker.com/r/biocontainers/openms/tags) <br />


#### c. FileConvert:Conversion
The input file for it is file with extention `.mzML`. 
The main use of this tool is to convert data from external sources to the formats used by OpenMS/TOPP.
The validation is based on [Fileconverter command from Openms](https://www.openms.org/documentation/html/TOPP_FileConverter.html).
The image used for validation is the same [biocontainers/openms](https://hub.docker.com/r/biocontainers/openms/tags) <br />

## Acknowledgement:
Funded by the Deutsche Forschungsgesellschaft (DFG, German Research Foundation) under the National Resaerch Data Infrastructure – NFDI/1 – Project number 441958208