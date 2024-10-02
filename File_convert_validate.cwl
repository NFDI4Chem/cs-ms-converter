#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
label: Test of msconvert output

baseCommand: ["bash"]
requirements:
  InlineJavascriptRequirement: {}
hints:
  DockerRequirement:
    dockerPull: biocontainers/openms:2.2.0_cv6

inputs:
  in_file1:
    type: File
    inputBinding:
      position: 1

  in_file:
    type: File
    inputBinding:
      position: 2

  in_dir:
    type: string

outputs:
  #output:
    #type: File
    #outputBinding:
      #glob: $(inputs.in_file.nameroot)_validation_result.txt

  output_dir:
    type: Directory
    outputBinding:
      glob: .
      outputEval: |
        ${
          self[0].basename = inputs.in_dir;
          return self[0]
        }

#stdout: $(inputs.in_file.nameroot)_validation_result.txt