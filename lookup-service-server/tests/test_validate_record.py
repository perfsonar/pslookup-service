import os
import pytest

os.environ.setdefault('DATABASE', '')

IPV4_1 = '203.0.113.1'
CLIENT_UUID = 'test-uuid-1234'


def make_valid_record(**overrides):
    base = {
        'name': 'lo',
        'addresses': [IPV4_1],
        'host': {
            'client_uuid': CLIENT_UUID,
            'name': ['testhost.example.com'],
        },
    }
    base.update(overrides)
    return base


class TestRecordValidation:
    def setup_method(self):
        from app.validate_record import RecordValidation
        self.validation = RecordValidation()

    def test_valid_record_passes(self):
        result = self.validation.validate_record(make_valid_record())
        assert result['validated'] is True
        assert result['error'] is None

    def test_missing_required_field_fails(self):
        record = make_valid_record()
        del record['addresses']
        result = self.validation.validate_record(record)
        assert result['validated'] is False
        assert result['error'] is not None

    def test_missing_host_fails(self):
        record = make_valid_record()
        del record['host']
        result = self.validation.validate_record(record)
        assert result['validated'] is False

    def test_empty_record_fails(self):
        result = self.validation.validate_record({})
        assert result['validated'] is False

    def test_record_is_returned_unchanged(self):
        record = make_valid_record()
        result = self.validation.validate_record(record)
        assert result['record'] is record
