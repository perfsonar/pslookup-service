import os

IPV4_1 = '203.0.113.1'
IPV4_2 = '203.0.113.2'
IPV6_1 = '2001:db8::1'
CLIENT_UUID = 'test-uuid-1234'


class TestInterfaceBuilder:
    def test_maps_basic_fields(self):
        from app.schedule_job import interface_builder
        record = {
            'interface-name': ['eth0'],
            'interface-addresses': [IPV4_1, IPV6_1],
            'interface-capacity': ['1000'],
            'interface-mtu': ['1500'],
            'interface-mac': ['AA:BB:CC:DD:EE:FF'],
        }
        result = interface_builder(record)
        assert result['name'] == 'eth0'
        assert result['addresses'] == [IPV4_1, IPV6_1]
        assert result['capacity'] == 1000
        assert result['mtu'] == 1500
        assert result['mac'] == 'AA:BB:CC:DD:EE:FF'

    def test_missing_optional_fields_are_omitted(self):
        from app.schedule_job import interface_builder
        record = {'interface-addresses': [IPV4_1]}
        result = interface_builder(record)
        assert 'name' not in result
        assert 'capacity' not in result
        assert 'mtu' not in result

    def test_meta_expires_set(self):
        from app.schedule_job import interface_builder
        record = {'expires': '2099-01-01T00:00:00Z'}
        result = interface_builder(record)
        assert result['meta']['expires'] == '2099-01-01T00:00:00Z'

    def test_pscheduler_tests_mapped(self):
        from app.schedule_job import interface_builder
        record = {'pscheduler-tests': ['throughput', 'latency']}
        result = interface_builder(record)
        assert result['pscheduler_tests'] == ['throughput', 'latency']


class TestHostBuilder:
    def _make_host_record(self, **overrides):
        base = {
            'host-name': ['testhost.example.com'],
            'client-uuid': [CLIENT_UUID],
            'host-net-interfaces': ['lookup/interface/abc-123'],
            'host-administrators': ['lookup/person/xyz-456'],
        }
        base.update(overrides)
        return base

    def test_maps_basic_fields(self):
        from app.schedule_job import host_builder
        record = self._make_host_record(**{
            'host-os-name': ['Linux'],
            'host-os-version': ['5.15'],
            'host-os-kernel': ['5.15.0'],
        })
        host, interface_uris, admin_uris = host_builder(record)
        assert host['os_name'] == 'Linux'
        assert host['os_version'] == '5.15'
        assert host['os_kernel'] == '5.15.0'
        assert host['client_uuid'] == CLIENT_UUID

    def test_returns_interface_and_admin_uris(self):
        from app.schedule_job import host_builder
        record = self._make_host_record()
        host, interface_uris, admin_uris = host_builder(record)
        assert interface_uris == ['lookup/interface/abc-123']
        assert admin_uris == ['lookup/person/xyz-456']

    def test_missing_interfaces_returns_empty_list(self):
        from app.schedule_job import host_builder
        record = self._make_host_record()
        del record['host-net-interfaces']
        host, interface_uris, admin_uris = host_builder(record)
        assert interface_uris == []

    def test_missing_admins_returns_empty_list(self):
        from app.schedule_job import host_builder
        record = self._make_host_record()
        del record['host-administrators']
        host, interface_uris, admin_uris = host_builder(record)
        assert admin_uris == []

    def test_location_fields_mapped(self):
        from app.schedule_job import host_builder
        record = self._make_host_record(**{
            'location-city': ['Springfield'],
            'location-country': ['US'],
            'location-latitude': ['123.0'],
            'location-longitude': ['-123.0'],
        })
        host, interface_uris, admin_uris = host_builder(record)
        assert host['location']['city'] == 'Springfield'
        assert host['location']['country'] == 'US'
        assert host['location']['latitude'] == 123.0
        assert host['location']['longitude'] == -123.0

    def test_vm_field_parsed_as_bool(self):
        from app.schedule_job import host_builder
        record = self._make_host_record(**{'host-vm': ['1']})
        host, interface_uris, admin_uris = host_builder(record)
        assert host['vm'] is True

    def test_memory_bytes_parsed_as_int(self):
        from app.schedule_job import host_builder
        record = self._make_host_record(**{'host-hardware-memory': ['8589934592']})
        host, interface_uris, admin_uris = host_builder(record)
        assert host['memory_bytes'] == 8589934592


class TestAdminBuilder:
    def test_maps_emails(self):
        from app.schedule_job import admin_builder
        record = {'person-emails': ['admin@example.com']}
        result = admin_builder(record)
        assert result['emails'] == ['admin@example.com']

    def test_missing_emails_omitted(self):
        from app.schedule_job import admin_builder
        result = admin_builder({})
        assert 'emails' not in result

    def test_meta_populated(self):
        from app.schedule_job import admin_builder
        record = {
            'person-organization': ['Example Org'],
            'location-city': ['Springfield'],
        }
        result = admin_builder(record)
        assert result['meta']['person_organization'] == 'Example Org'
        assert result['meta']['location_city'] == 'Springfield'


class TestServiceBuilder:
    def test_ignores_unknown_service_type(self):
        from app.schedule_job import service_builder
        record = {'service-type': ['unknown']}
        assert service_builder(record) is None

    def test_ignores_missing_service_type(self):
        from app.schedule_job import service_builder
        assert service_builder({}) is None

    def test_maps_pscheduler_service(self):
        from app.schedule_job import service_builder
        record = {
            'service-type': ['pscheduler'],
            'service-locator': ['https://203.0.113.1/pscheduler'],
            'pscheduler-tools': ['iperf3'],
            'pscheduler-tests': ['throughput'],
        }
        result = service_builder(record)
        assert result is not None
        assert result['urls'] == ['https://203.0.113.1/pscheduler']
        assert result['tools'] == ['iperf3']
        assert result['tests'] == ['throughput']
        assert result['meta']['service_type'] == 'pscheduler'

    def test_maps_ma_service(self):
        from app.schedule_job import service_builder
        record = {
            'service-type': ['ma'],
            'service-locator': ['https://203.0.113.1/archiver'],
        }
        result = service_builder(record)
        assert result is not None
        assert result['urls'] == ['https://203.0.113.1/archiver']
        assert result['meta']['service_type'] == 'ma'