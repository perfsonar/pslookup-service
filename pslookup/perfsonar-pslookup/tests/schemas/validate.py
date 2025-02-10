from jsonschema import validate
import json
with open('schema.json') as file:
    schema = json.load(file)

#test data
with open('tests/schema_test.json') as file:
    record = json.load(file)

#validate
try:
    validate(instance=record, schema=schema)
    print('Validated')
except Exception as e:
    print(e.message)


with open('tests/helper_subschemas/pscheduler_service_subschema.json') as file:
    pscheduler_service_subschema = json.load(file)

#test data
with open('tests/pscheduler_service_subschema_test.json') as file:
    record = json.load(file)

#validate
try:
    validate(instance=record, schema=pscheduler_service_subschema)
    print('Validated')
except Exception as e:
    print(e)
