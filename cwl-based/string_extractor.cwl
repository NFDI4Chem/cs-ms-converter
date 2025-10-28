#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: ExpressionTool
label: Extract the location/path of a file

requirements:
  InlineJavascriptRequirement: {}

inputs:
  input_file:
    type: File

outputs:
  output:
    type: string
  output2:
    type: string
  output3:
    type: string
  output4:
    type: string
  output5:
    type: string

expression: |
  ${
  var ipFilePath= inputs.input_file.location.replace('file://','');
  var baseFolderPath= ipFilePath.substr(0,ipFilePath.lastIndexOf("/"));
  var fileBaseName= ipFilePath.substr(ipFilePath.lastIndexOf("/")+1);
  fileBaseName= fileBaseName.substr(0,fileBaseName.lastIndexOf('.'));
  if (fileBaseName.endsWith(".D") || fileBaseName.endsWith(".d") || fileBaseName.endsWith(".Wiff") ||fileBaseName.endsWith(".wiff") || fileBaseName.endsWith(".WIFF")){
    fileBaseName= fileBaseName.substr(0,fileBaseName.lastIndexOf('.'));
  }
  var opFileName= fileBaseName + "_FileConverter_op.mzML"
  var intermediateFilePath= baseFolderPath.substr(0,baseFolderPath.lastIndexOf("/"))+"/fileconverter_cwl.sh";
  return {"output": ipFilePath, "output2": baseFolderPath, "output3": fileBaseName, "output4": opFileName, "output5": intermediateFilePath}; }



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