import os
import pytest
from datetime import datetime, timezone, timedelta

os.environ.setdefault('DATABASE', '')


def make_message(ttl=None):
    from app.backward_compatibility.message import Message
    from app.backward_compatibility.reserved_keys import ReservedKeys
    msg = Message({'type': 'host'})
    if ttl:
        msg.add(ReservedKeys.RECORD_TTL, ttl)
    return msg


class TestRequestLease:
    def test_always_returns_true(self):
        from app.backward_compatibility.lease_manager import request_lease
        msg = make_message()
        assert request_lease(msg) is True

    def test_uses_provided_ttl(self):
        from app.backward_compatibility.lease_manager import request_lease, DEFAULT_LEASE
        from app.backward_compatibility.reserved_keys import ReservedKeys
        msg = make_message(ttl='PT1H')  # 1 hour in ISO 8601
        before = datetime.now(timezone.utc)
        request_lease(msg)
        expires_str = msg.get_key(ReservedKeys.RECORD_EXPIRES)
        expires = datetime.fromisoformat(expires_str)
        expected = before + timedelta(hours=1)
        assert abs((expires - expected).total_seconds()) < 5

    def test_ttl_below_minimum_uses_default(self):
        from app.backward_compatibility.lease_manager import request_lease, DEFAULT_LEASE
        from app.backward_compatibility.reserved_keys import ReservedKeys
        msg = make_message(ttl='PT1S')  # 1 second — below MIN_LEASE
        before = datetime.now(timezone.utc)
        request_lease(msg)
        expires_str = msg.get_key(ReservedKeys.RECORD_EXPIRES)
        expires = datetime.fromisoformat(expires_str)
        expected = before + timedelta(seconds=DEFAULT_LEASE)
        assert abs((expires - expected).total_seconds()) < 5

    def test_ttl_above_maximum_uses_default(self):
        from app.backward_compatibility.lease_manager import request_lease, DEFAULT_LEASE, MAX_LEASE
        from app.backward_compatibility.reserved_keys import ReservedKeys
        msg = make_message(ttl='P365D')  # 1 year — above MAX_LEASE
        before = datetime.now(timezone.utc)
        request_lease(msg)
        expires_str = msg.get_key(ReservedKeys.RECORD_EXPIRES)
        expires = datetime.fromisoformat(expires_str)
        expected = before + timedelta(seconds=DEFAULT_LEASE)
        assert abs((expires - expected).total_seconds()) < 5

    def test_no_ttl_uses_default(self):
        from app.backward_compatibility.lease_manager import request_lease, DEFAULT_LEASE
        from app.backward_compatibility.reserved_keys import ReservedKeys
        msg = make_message()
        before = datetime.now(timezone.utc)
        request_lease(msg)
        expires_str = msg.get_key(ReservedKeys.RECORD_EXPIRES)
        expires = datetime.fromisoformat(expires_str)
        expected = before + timedelta(seconds=DEFAULT_LEASE)
        assert abs((expires - expected).total_seconds()) < 5