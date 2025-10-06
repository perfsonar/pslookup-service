from fastapi import APIRouter, Request, Response, HTTPException
from ..validate_record import RecordValidation
from ..database import map_dbspec, post_to_elastic, post_to_opensearch
import os

router = APIRouter()
validation = RecordValidation()

@router.post("/lookup/records/")
def register_v1_record(request: Request, response: Response, registration_record: dict):
    print(f"Request: {request.method} {request.url}")
    try : 
        print("request json         : {}".format(request.json()))
    except Exception as err:
        # could not parse json
        print("request body         : {}".format(request.body()))
    return request