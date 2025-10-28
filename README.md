# Mass Spectroscopy File Converter

## Introduction:

The integration of the latest machines and technologies, combined with a diverse array of existing systems, expands the range of data formats and types, thereby introducing new challenges. To effectively navigate these complexities, it is crucial to implement robust governance mechanisms that ensure seamless conversion of diverse data formats into standardized forms.<br /> <br />
The converter service is built on the Common Workflow Language (CWL), selected for its exceptional interoperability, portability, and reproducibility. The source code is housed in a GitLab repository, complete with a CI/CD pipeline that not only automates the generation of conversion and validation summary reports but also fosters community collaboration. These reports offer a detailed overview of the conversion and validation process, ensuring transparency and efficiency across various file formats.<br /> <br />
The repository includes all the necessary code to run a converter, which is built on Flask, adheres to the OpenAPI specification, and provides a REST API for seamless integration with other NFDI4Chem services. The entire system is also packaged in a Docker image for easy deployment, and with a Helm chart available to streamline deployment in Kubernetes environments. <br /> <br />
This repository is specifically designed to facilitate the conversion of mass spectrometry files from various formats into the mzML format.
<br />

## Contents:

This repository provides three distinct methods for installing the MS Converter. Each method is organized in its own folder, with installation instructions provided in the corresponding location.

## Acknowledgement:
Funded by the Deutsche Forschungsgesellschaft (DFG, German Research Foundation) under the National Resaerch Data Infrastructure – NFDI/1 – Project number 441958208