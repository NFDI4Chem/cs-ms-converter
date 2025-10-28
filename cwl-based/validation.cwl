#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
label: Test of msconvert output

baseCommand: ["FileInfo_anyuser", "-v"]
requirements:
  InlineJavascriptRequirement: {}
hints:
  DockerRequirement:
    dockerPull: biocontainers/openms:2.2.0_cv6

inputs:
  in_file:
    type: File
    inputBinding:
      prefix: -in

  in_dir:
    type: string

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.in_file.nameroot)_validation_result.txt

  output_dir:
    type: Directory
    outputBinding:
      glob: .
      outputEval: |
        ${
          self[0].basename = inputs.in_dir;
          return self[0]
        }

stdout: $(inputs.in_file.nameroot)_validation_result.txt

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