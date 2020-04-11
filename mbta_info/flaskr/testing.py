import os

import schemas

file_name = 'lines.csv'
model_name = os.path.splitext(file_name)[0].rstrip('s')  # data file name may be pluralized
model_schema = getattr(schemas, model_name.title() + 'Schema')
print("MODEL SCHEMA", model_schema)
