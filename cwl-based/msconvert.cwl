#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
label: Uses Proteowizard MSConvert to convert vendor files into mzML

baseCommand: ["bash"]

requirements:
  - class: DockerRequirement
    dockerPull: chambm/pwiz-skyline-i-agree-to-the-vendor-licenses 
  - class: InlineJavascriptRequirement

inputs:
  in_file1:
    type: File
    inputBinding:
      position: 1

  in_file:
    type: File
    inputBinding:
      position: 2
  
  in_file2:
    type: File
    inputBinding:
      position: 3

  in_dir:
    type: string

outputs:
  #outfile:
   # type: File
    #label: mzML file
    #format: edam:format_3245
    #outputBinding:
     # glob: $(inputs.in_test).mzML
  
  output_dir:
    type: Directory
    outputBinding:
      glob: .
      outputEval: |
        ${
         self[0].basename = inputs.in_dir;
         return self[0];
         }


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