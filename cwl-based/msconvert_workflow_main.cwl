#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
label: For conversion purpose

inputs:
  in_file:
    type: File
    label: mzXML or vendor file format
    format: edam:format_3245
  
  in_file1:
    type: File
  
  in_file2:
    type: File

 # parameters:
  #  type: string[]
   # default: [mzML]

steps:
  1.Metadata_Extraction:
    run: string_extractor.cwl
    in:
      input_file: in_file
    out: [output, output2, output3, output4, output5]

  2.Conversion_Process:
    run: msconvert.cwl
    in:
      in_file1: in_file1
      in_file: in_file
      in_file2: in_file2
      in_dir: 1.Metadata_Extraction/output2
    out: [output_dir]
  
  3.Post_processing:
    run: validation_file_creation.cwl
    in:
      input: 1.Metadata_Extraction/output3
      in_dir: 1.Metadata_Extraction/output2
      input2: 1.Metadata_Extraction/output5
    out: [output_dir]


outputs:
  inputFilePath:
    type: string
    outputSource: 1.Metadata_Extraction/output

  outputFileName:
    type: string
    outputSource: 1.Metadata_Extraction/output4

  ConversionOutput:
    type: Directory
    outputSource: 2.Conversion_Process/output_dir

  PostProcessing:
    type: Directory
    outputSource: 3.Post_processing/output_dir


s:author:
  - class: s:Person
    s:identifier: https://orcid.org/0009-0000-3287-0295
    s:email: mailto:lincoln.sherpa@tu-dresden.de
    s:name: Lincoln Sherpa

s:contributor:
  - class: s:Person
    s:identifier: https://orcid.org/0000-0002-7899-7192
    s:email: mailto:sneumann@ipb-halle.de
    s:name: Steffen Neumann

s:citation: https://doi.org/10.5281/zenodo.14923739
s:codeRepository: https://github.com/NFDI4Chem/cs-ms-converter
s:dateCreated: "2024-11-01"
s:license: https://mit-license.org/


$namespaces:
  s: https://schema.org/
  edam: http://edamontology.org/

$schemas:
  - https://schema.org/version/latest/schemaorg-current-https.rdf
  - http://edamontology.org/EDAM_1.18.owl