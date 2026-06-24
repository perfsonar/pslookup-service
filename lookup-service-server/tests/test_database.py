import os
from datetime import datetime, timezone, timedelta

IPV4_1 = '203.0.113.1'
IPV4_2 = '203.0.113.2'
IPV6_1 = '2001:db8::1'
IPV6_2 = '2001:db8::2'
CLIENT_UUID = 'test-uuid-1234'


def make_record(**overrides):
    base = {
        'addresses': [IPV4_1, IPV6_1],
        'host': {
            'client_uuid': CLIENT_UUID,
        },
    }
    base.update(overrides)
    return base


class TestMapDbspec:
    def test_sets_ipv4_and_ipv6_versions(self):
        from app.database import map_dbspec
        result = map_dbspec(make_record())
        assert set(result['ip_versions']) == {4, 6}

    def test_sets_only_ipv4(self):
        from app.database import map_dbspec
        result = map_dbspec(make_record(addresses=[IPV4_1, IPV4_2]))
        assert set(result['ip_versions']) == {4}

    def test_sets_only_ipv6(self):
        from app.database import map_dbspec
        result = map_dbspec(make_record(addresses=[IPV6_1, IPV6_2]))
        assert set(result['ip_versions']) == {6}

    def test_sets_timestamp(self):
        from app.database import map_dbspec
        before = datetime.now(timezone.utc)
        result = map_dbspec(make_record())
        after = datetime.now(timezone.utc)
        assert before <= result['@timestamp'] <= after

    def test_expires_defaults_to_24h(self):
        from app.database import map_dbspec
        result = map_dbspec(make_record())
        assert result['expires'] == result['@timestamp'] + timedelta(hours=24)

    def test_expires_uses_meta_value_when_present(self):
        from app.database import map_dbspec
        custom_expiry = '2099-01-01T00:00:00Z'
        result = map_dbspec(make_record(meta={'expires': custom_expiry}))
        assert result['expires'] == custom_expiry

    def test_expires_defaults_when_meta_expires_is_none(self):
        from app.database import map_dbspec
        result = map_dbspec(make_record(meta={'expires': None}))
        assert result['expires'] == result['@timestamp'] + timedelta(hours=24)


class TestMapRecordId:
    def test_basic_id_construction(self):
        from app.database import map_record_id
        record = make_record(addresses=[IPV4_1, IPV4_2])
        assert map_record_id(record) == f'{CLIENT_UUID}-{IPV4_1}-{IPV4_2}'

    def test_addresses_are_sorted(self):
        from app.database import map_record_id
        record = make_record(addresses=[IPV4_2, IPV4_1])  # reversed input
        assert map_record_id(record) == f'{CLIENT_UUID}-{IPV4_1}-{IPV4_2}'  # sorted output

    def test_single_address(self):
        from app.database import map_record_id
        record = make_record(addresses=[IPV4_1])
        assert map_record_id(record) == f'{CLIENT_UUID}-{IPV4_1}'
