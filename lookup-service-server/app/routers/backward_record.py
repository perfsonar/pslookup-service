from fastapi import APIRouter, Request, Response, HTTPException
from ..validate_record import RecordValidation
from ..database import map_dbspec, post_to_elastic, post_to_opensearch
import os

router = APIRouter()
validation = RecordValidation()

@router.post("/lookup/records/")
def register_v1_record(message):
    print(message)
    return