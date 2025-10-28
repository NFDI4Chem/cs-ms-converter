# msconvert_v3_s3

This is the alternate version of [msconvert_v2](https://git.rwth-aachen.de/linsherpa/msconverter_v2) with s3-storage compatibility extention



##  🛠️  Initial Step

It is recommended to build three Docker images on your hosted machine for proper functionality.

Inside the docker_instance directory, you will find three subfolders:

- `main_workflow_docker` – orchestrates the other microservices

- `msconvert_docker` – handles MS file conversion

- `validation_docker` – performs data validation and file convert

1. To build the main workflow image, navigate inside main_workflow_docker directory and run the following command 
(replace `main_api` with your desired image name if needed):

<pre>
docker build -t main_api  .
</pre>

2. To build the msconvert image, navigate inside the msconvert_docker directory and execute the following command:

<pre>
docker build -t msconvert_image  .
</pre>

3. To build the validation image, navigate inside the msconvert_docker directory and run the following command:

<pre>
docker build -t validation_image  .
</pre>


## ![Docker](https://img.icons8.com/fluent/16/docker.png) Docker Setup

Once the Docker images have been successfully built, the next step is to launch containers for each service. 
Before doing so, it is recommended to create a dedicated Docker network to enable seamless communication between these containers.

### 🌐 Create a Docker Network
Use the command below to create a custom network named `my_network`:

<pre>
docker network create my_network
</pre>

### 🐳 Creating Docker Containers:

#### Step 1: Creating the main workflow container:
The `main_workflow` container functions as the central orchestrator for the microservices. 
The command line is used to create a container called `nfdi4chem-ms-main-workflow` with conditions mentioned above.
<pre>
docker run -d -ti -p 5000:5000 --name nfdi4chem-ms-main-workflow --network my_network main_api
</pre>

#### Step 2: Creating msconvert container
The `msconvert` service is built upon the [ProteWizard container](https://github.com/ProteoWizard/container), enhanced with added additional API endpoints to enable automated data conversion. It executes the standard msconvert command and accepts parameters as specified in the [official documentation](https://proteowizard.sourceforge.io/tools/msconvert.html).

Like the main workflow container, this service should be connected to a shared host directory and the `my_network` Docker network to enable file exchange and inter-container communication. ✅ It is recommended to name the container `nfdi4chem-ms-msconvert` for consistent communication across the conatiner environment.

Launch the container with the following command:

<pre>
docker run -d -ti -p 4000:4000  --name nfdi4chem-ms-msconvert --network my_network msconvert_image
</pre>

#### Step 3:Creating validation container
The `validation` microservice is based on the official [OpenMS container](https://hub.docker.com/r/biocontainers/openms), and has been extended with custom API endpoints to support validation of `mzML` files, as described in the [FileInfo documentation](https://openms.de/doxygen/release/2.5.0/html/TOPP_FileInfo.html). Additionally, it incorporates functionality to correct or reprocess `mzML` files using [FileConverter](https://openms.de/documentation/html/TOPP_FileConverter.html). 

🚨 For consistency and interoperability, it is recommended to name this container `nfdi4chem-ms-validation`.

Following the same volume and network setup as in Steps 1 and 2, the container can be launched using the command below

<pre>
docker run -d -ti -p 3000:3000  --name nfdi4chem-ms-validation --network my_network validation_image
</pre>


## <img src="https://cdn-icons-png.flaticon.com/512/2163/2163205.png" alt="Acknowledgement" width="40"/> Acknowledgement:
Funded by the Deutsche Forschungsgesellschaft (DFG, German Research Foundation) under the National Research Data Infrastructure – NFDI/1 – Project number 441958208