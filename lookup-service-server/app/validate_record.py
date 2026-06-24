from jsonschema import validate
import json

class RecordValidation(object):

    def __init__(self):
        with open('schema/schema.json') as file:
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
