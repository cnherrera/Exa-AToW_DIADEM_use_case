cwlVersion: v1.2
class: CommandLineTool

label: "Access Database and Get Data"
doc: >
  This process accesses a DIAMOND database using the rover_diamond library. It allows users to extract
  all attributes or a specified subset, saving the result in a CSV file.

# Instead of calling Singularity manually, let CWL handle it correctly
baseCommand: python

arguments:
  - access_database.py

requirements:
  - class: DockerRequirement
    dockerImageId: "./python3.10_pd_ny_rm_rover.sif"  # Use Singularity image

  - class: EnvVarRequirement
    envDef:
      SINGULARITY_BIND: "/etc/resolv.conf:/etc/resolv.conf"

  - class: InitialWorkDirRequirement
    listing:
      - class: File
        location: ./access_database.py  # Ensure this script is included in the working directory

  - class: NetworkAccess  # <== Enables networking
    networkAccess: true
#
# Inline JavaScript requirement (if needed)
#  - class: InlineJavascriptRequirement



inputs:
  database_name:
    type: string
    label: "DIADEM/DIAMOND Database filename"
    doc: >
      Name of the DIADEM/DIAMOND database to connect to.
    inputBinding:
      position: 1

  attributes_to_extract:
    type: string[]?
    label: "List of Attributes to Extract"
    doc: >
      A list of attributes (as strings) that the user wants to extract from the database.
      If not specified, all attributes are extracted by default.
    inputBinding:
      position: 2
      prefix: "--attributes"

  output_file:
    type: string?
    label: "Output CSV file"
    doc: >
      Name of the CSV file to save the extracted data. Defaults to 'data_from_database.csv' if not specified.
    inputBinding:
      position: 3
      prefix: "--output"

outputs:
  database_content:
    type: File
    label: "Extracted data as CSV"
    doc: >
      The output is a CSV file containing the extracted attributes from the DIAMOND database.
    outputBinding:
      glob: "*database*.csv"


