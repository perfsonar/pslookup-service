from datetime import datetime, timedelta
import isodate
import logging
from .reserved_keys import ReservedKeys

logger = logging.getLogger(__name__)

DEFAULT_LEASE = 2 * 60 * 60
# 30 Days
MAX_LEASE = 2592000
MIN_LEASE = 240

def request_lease(message):

    requested_TTL = message.get_TTL()

    ttl = 0

    if requested_TTL:
        duration_timedelta = isodate.parse_duration(requested_TTL)
        ttl = duration_timedelta.total_seconds()
    
    if (not requested_TTL) or (ttl == 0) or (ttl > MAX_LEASE) or (ttl < MIN_LEASE):
        ttl = DEFAULT_LEASE
    
    new_expires = datetime.now() + timedelta(seconds=ttl)
    logger.info("Lease granted. ttl value: " + str(ttl))
    message.add(ReservedKeys.RECORD_EXPIRES, new_expires.isoformat())
    logger.info("Lease granted. expires value: " + str(new_expires.isoformat()))

    return True







    