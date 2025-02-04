cwltool --singularity  access_database.cwl  --database_name "Atomistic_Numerical_Simulations" --output "mydatabase.csv"

cwltool --singularity  --debug filtering_tool.cwl --file_path from_database.csv  --conditions conditions.json


