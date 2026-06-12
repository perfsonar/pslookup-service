from fastapi import APIRouter, Request, HTTPException
from ..validate_record import RecordValidation
from ..database import map_dbspec, post_to_elastic, post_to_opensearch
import os

router = APIRouter()
validation = RecordValidation()

@router.post("/record/")
def register_record(request: Request, registration_record: dict):

    registration_record = validation.validate_record(registration_record)

    if not registration_record['validated']:
        raise HTTPException(status_code=422, 
                            detail="Registration record Validation failed. {}".format(registration_record['error'].message))
    
    registration_record = registration_record['record']
    registration_record = map_dbspec(registration_record)
    if str(os.environ.get('DATABASE')).startswith('elastic'):
        response = post_to_elastic(registration_record)
    elif str(os.environ.get('DATABASE')).startswith('opensearch'):
        response = post_to_opensearch(registration_record)
    else:
        raise HTTPException(status_code=500, detail="DATABASE environment variable not configured. Must be 'elasticsearch' or 'opensearch'.")

    return response