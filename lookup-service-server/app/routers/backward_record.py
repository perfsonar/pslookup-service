from fastapi import APIRouter
from ..validate_record import RecordValidation
import logging
from ..backward_compatibility.json_register_request import JsonRegisterRequest
from ..backward_compatibility.lookup_service import LookupService
import uuid
from ..backward_compatibility.reserved_keys import ReservedKeys
from ..backward_compatibility.reserved_values import ReservedValues
from ..backward_compatibility.message import Message
from ..backward_compatibility.database.service_elastic_search import ServiceElasticSearch
from ..backward_compatibility.lease_manager import request_lease

router = APIRouter()
validation = RecordValidation()
logger = logging.getLogger(__name__)

@router.post("/{lookup}/records")
def register_v1_record(message: dict):
    logger.info(" Processing register service.")
    logger.info(" Received message: " + str(message))

    request = JsonRegisterRequest(message)

    if is_valid(request):
        # Request Lease
        got_lease = request_lease(request)
        if got_lease:
            record_type = request.get_record_type()
            uri = new_uri(record_type)
            request.add(ReservedKeys.RECORD_URI, uri)

            # Add the state
            request.add(ReservedKeys.RECORD_STATE, ReservedValues.RECORD_VALUE_STATE_REGISTER)

            # Build the matching query requestURl that must fail for the service to be published
            query = Message()
            operators = Message()
            operators.add(ReservedKeys.RECORD_OPERATOR, ReservedValues.RECORD_OPERATOR_ALL)

            key_values = request.get_map()

            for key in key_values:
                if not is_ignore_key(key):
                    logger.debug("key-value pair:" + key + "=" + str(key_values.get(key)))
                    operators.add(key, ReservedValues.RECORD_OPERATOR_ALL)
                    query.add(key, key_values.get(key))

            db = ServiceElasticSearch()
            try:
                response = db.query_and_publish_service(request, query, operators)
            except Exception as e:
                logger.error("Error registerting the record {}".format(str(request.get_map())))
                raise Exception(e)

            return response

        else:
            logger.critical("Failed to secure lease for the registration record")
            logger.info("Register status: FAILED; exiting")
    else:
        logger.error("Invalid request")
        logger.info("Register status: FAILED due to Invalid Request; exiting")

def is_valid(request):
    if request.get_record_type():
        return True

def new_uri(record_type: str):
    try:
        return LookupService.SERVICE_URI_PREFIX + "/" + record_type + "/" + str(uuid.uuid4())
    except Exception as e:
        logger.error("Error creating URI: Record Type not found")
        logger.error(e)

def is_ignore_key(key: str):
    if key in [ReservedKeys.RECORD_TTL, ReservedKeys.RECORD_EXPIRES, ReservedKeys.RECORD_URI, ReservedKeys.RECORD_STATE]:
        return True
    else:
        return False