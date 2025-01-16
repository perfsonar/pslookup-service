from jsonschema import validate
import json
from pathlib import Path
import pkg_resources

class RecordValidation(object):

    def __init__(self):
        schema_file = pkg_resources.resource_filename('lookup_service', 'schema/schema.json')
        with open(schema_file) as file:
            self.schema = json.load(file)
    
    def validate_record(self, record={}):
        #validate
        try:
            validate(instance=record, schema=self.schema)
            validated = True
            error = None
            
        except Exception as e:
            validated = False
            error = e

        return {'validated': validated, 'error': error, 'record': record}
