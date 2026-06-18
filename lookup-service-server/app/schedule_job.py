from backward_compatibility.database.service_elastic_search import ServiceElasticSearch
from backward_compatibility.message import Message
from backward_compatibility.reserved_keys import ReservedKeys
from backward_compatibility.reserved_values import ReservedValues
import requests
import logging
import time
import os
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_dir = os.environ.get('V1_LOG_DIR', '/var/log/perfsonar')
file_handler = logging.FileHandler(os.path.join(log_dir, 'pslookup-backward-compatibility-agent.log'))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

def interface_builder(interface_record):
    new_interface_record = {}

    # Ignore the expires since they are defaulted to 1 day
    if interface_record.get('interface-capacity', [None])[0] is not None:
        try:
            new_interface_record['capacity'] = int(interface_record.get('interface-capacity', [None])[0])
        except (ValueError, TypeError):
            new_interface_record.setdefault('meta', {})['capacity'] = interface_record.get('interface-capacity', [None])[0]
    if interface_record.get('interface-name', [None])[0] is not None:
        new_interface_record['name'] = interface_record.get('interface-name', [None])[0]

    if interface_record.get('interface-addresses') is not None:
        new_interface_record['addresses'] = interface_record.get('interface-addresses', [None])
    if interface_record.get('pscheduler-tests') is not None:
        new_interface_record['pscheduler_tests'] = interface_record.get('pscheduler-tests', [None])
    if interface_record.get('interface-mtu', [None])[0] is not None:
        try:
            new_interface_record['mtu'] = int(interface_record.get('interface-mtu', [None])[0])
        except (ValueError, TypeError):
            new_interface_record.setdefault('meta', {})['mtu'] = interface_record.get('interface-mtu', [None])[0]
    if interface_record.get('interface-mac', [None])[0] is not None:
        new_interface_record['mac'] = interface_record.get('interface-mac', [None])[0]
    # Add everything else to meta for debugging
    new_interface_record['meta'] = new_interface_record.get('meta', {})
    if interface_record.get('expires') is not None:
        new_interface_record['meta']['expires'] = interface_record.get('expires')
    if interface_record.get('type', [None])[0] is not None:
        new_interface_record['meta']['record_type'] = interface_record.get('type', [None])[0]
    if interface_record.get('uri') is not None:
        new_interface_record['meta']['record_uri'] = interface_record.get('uri')
    if interface_record.get('ttl', [None])[0] is not None:
        new_interface_record['meta']['record_ttl'] = interface_record.get('ttl', [None])[0]
    if interface_record.get('client-uuid', [None])[0] is not None:
        new_interface_record['meta']['record_client_uuid'] = interface_record.get('client-uuid', [None])[0]
    if interface_record.get('group-domains') is not None:
        new_interface_record['meta']['record_group_domains'] = interface_record.get('group-domains', [None])
    if interface_record.get('state') is not None:
        new_interface_record['meta']['record_state'] = interface_record.get('state')
    if interface_record.get('psinterface-type', [None])[0] is not None:
        new_interface_record['meta']['record_interface_type'] = interface_record.get('psinterface-type', [None])[0]

    return new_interface_record
    

def host_builder(host_record):
    new_host_record = {}

    if host_record.get('host-vm', [None])[0] is not None:
        try:
            new_host_record['vm'] = bool(int(host_record.get('host-vm')[0]))
        except (ValueError, TypeError):
            new_host_record.setdefault('meta', {})['vm'] = host_record.get('host-vm', [None])[0]
    
    # location
    new_host_record['location'] = new_host_record.get('location', {})
    if host_record.get('location-state', [None])[0] is not None:
        new_host_record['location']['state_province_region'] = host_record.get('location-state', [None])[0]
    if host_record.get('location-city', [None])[0] is not None:
        new_host_record['location']['city'] = host_record.get('location-city', [None])[0]
    if host_record.get('location-code', [None])[0] is not None:
        new_host_record['location']['zipcode/ postal code'] = host_record.get('location-code', [None])[0]
    if host_record.get('location-country', [None])[0] is not None:
        new_host_record['location']['country'] = host_record.get('location-country', [None])[0]
    if host_record.get('location-latitude', [None])[0] is not None:
        try:
            new_host_record['location']['latitude'] = float(host_record.get('location-latitude')[0])
        except (ValueError, TypeError):
            new_host_record.setdefault('meta', {})['location-latitude'] = host_record.get('location-latitude', [None])[0]
    if host_record.get('location-longitude', [None])[0] is not None:
        try:
            new_host_record['location']['longitude'] = float(host_record.get('location-longitude')[0])
        except (ValueError, TypeError):
            new_host_record.setdefault('meta', {})['location-longitude'] = host_record.get('location-longitude', [None])[0]
    if host_record.get('location-sitename', [None])[0] is not None:
        new_host_record['location']['sitename'] = host_record.get('location-sitename', [None])[0]

    # Meta
    new_host_record['meta'] = new_host_record.get('meta', {})
    if host_record.get('expires') is not None:
        new_host_record['meta']['expires'] = host_record.get('expires')
    if host_record.get('pshost-install-method', [None])[0] is not None:
        new_host_record['meta']['pshost_install_method'] = host_record.get('pshost-install-method', [None])[0]
    if host_record.get('_lastUpdated') is not None:
        new_host_record['meta']['_lastUpdated'] = host_record.get('_lastUpdated')
    if host_record.get('type', [None])[0] is not None:
        new_host_record['meta']['record_type'] = host_record.get('type', [None])[0]
    if host_record.get('state') is not None:
        new_host_record['meta']['record_state'] = host_record.get('state')
    if host_record.get('host-net-tcp-autotunemaxbuffer-send', [None])[0] is not None:
        new_host_record['meta']['host_net_tcp_autotunemaxbuffer_send'] = host_record.get('host-net-tcp-autotunemaxbuffer-send', [None])[0]
    if host_record.get('host-net-tcp-maxbuffer-recv', [None])[0] is not None:
        new_host_record['meta']['host_net_tcp_maxbuffer_recv'] = host_record.get('host-net-tcp-maxbuffer-recv', [None])[0]
    if host_record.get('host-hardware-cpuid', [None])[0] is not None:
        new_host_record['meta']['host_hardware_cpuid'] = host_record.get('host-hardware-cpuid', [None])[0]
    if host_record.get('uri') is not None:
        new_host_record['meta']['uri'] = host_record.get('uri')
    if host_record.get('ttl', [None])[0] is not None:
        new_host_record['meta']['ttl'] = host_record.get('ttl', [None])[0]
    if host_record.get('host-net-tcp-autotunemaxbuffer-recv', [None])[0] is not None:
        new_host_record['meta']['host_net_tcp_autotunemaxbuffer_recv'] = host_record.get('host-net-tcp-autotunemaxbuffer-recv', [None])[0]
    if host_record.get('host-net-tcp-maxbuffer-send', [None])[0] is not None:
        new_host_record['meta']['host_net_tcp_maxbuffer_send'] = host_record.get('host-net-tcp-maxbuffer-send', [None])[0]
    if host_record.get('host-net-ipv6-enabled', [None])[0] is not None:
        new_host_record['meta']['host_net_ipv6_enabled'] = host_record.get('host-net-ipv6-enabled', [None])[0]
    
    
    
    if host_record.get('host-hardware-processorcore', [None])[0] is not None:
        new_host_record['meta']['host_hardware_processorcore'] = host_record.get('host-hardware-processorcore')[0]
    
    if host_record.get('host-os-kernel', [None])[0] is not None:
        new_host_record['os_kernel'] = host_record.get('host-os-kernel', [None])[0]
    if host_record.get('host-os-name', [None])[0] is not None:
        new_host_record['os_name'] = host_record.get('host-os-name', [None])[0]
    if host_record.get('host-hardware-processorspeed') is not None:
        new_host_record['processor_speed'] = host_record.get('host-hardware-processorspeed')
    if host_record.get('host-os-version', [None])[0] is not None:
        new_host_record['os_version'] = host_record.get('host-os-version', [None])[0]
    if host_record.get('host-productname', [None])[0] is not None:
        new_host_record['product_name'] = host_record.get('host-productname', [None])[0]
    if host_record.get('client-uuid', [None])[0] is not None:
        new_host_record['client_uuid'] = host_record.get('client-uuid', [None])[0]
    if host_record.get('pshost-access-policy', [None])[0] is not None:
        new_host_record['access_policy'] = host_record.get('pshost-access-policy', [None])[0]
    if host_record.get('pshost-bundle', [None])[0] is not None:
        new_host_record['perfsonar_bundle'] = host_record.get('pshost-bundle', [None])[0]
    if host_record.get('pshost-bundle', [None])[0] is not None:
        new_host_record['perfsonar_bundle'] = host_record.get('pshost-bundle', [None])[0]


    # Bundle version in two places. Populate using one and place the other to meta
    if host_record.get('pshost-bundle-version', [None])[0] is not None:
        new_host_record['perfsonar_version'] = host_record.get('pshost-bundle-version')[0]
        # Add the other version from host_record to meta
        if host_record.get('pshost-toolkitversion', [None])[0] is not None:
            new_host_record['meta']['pshost_toolkitversion'] = host_record.get('pshost-toolkitversion')[0]
    elif host_record.get('pshost_toolkitversion', [None])[0] is not None:
        new_host_record['perfsonar_version'] = host_record.get('pshost_toolkitversion')[0]

    if host_record.get('host-manufacturer', [None])[0] is not None:
        new_host_record['manufacturer'] = host_record.get('host-manufacturer', [None])[0]
    if host_record.get('host-hardware-processorcount', [None])[0] is not None:
        try:
            new_host_record['processor_core_count'] = int(host_record.get('host-hardware-processorcount', [None])[0])
        except (ValueError, TypeError):
            new_host_record.setdefault('meta', {})['processor_core_count'] = host_record.get('host-hardware-processorcount', [None])[0]

    if host_record.get('host-net-tcp-congestionalgorithm', [None])[0] is not None:
        new_host_record['net_ipv4_tcp_congestion_control'] = host_record.get('host-net-tcp-congestionalgorithm', [None])[0]
    if host_record.get('host-os-architecture', [None])[0] is not None:
        new_host_record['os_architecture'] = host_record.get('host-os-architecture', [None])[0]
    if host_record.get('host-name') is not None:
        new_host_record['name'] = host_record.get('host-name', [None])
    if host_record.get('group-domains') is not None:
        new_host_record['group_domains'] = host_record.get('group-domains', [None])
    if host_record.get('host-hardware-memory', [None])[0] is not None:
        try:
            new_host_record['memory_bytes'] = int(host_record.get('host-hardware-memory', [None])[0])
        except Exception as e:
            # Push it to meta
            new_host_record['meta']['memory_bytes'] = host_record.get('host-hardware-memory', [None])[0]
    if host_record.get('pshost-role', [None])[0] is not None:
        new_host_record['role'] = host_record.get('pshost-role', [None])[0]
    if host_record.get('group-communities') is not None:
        new_host_record['group_communities'] = host_record.get('group-communities', [None])
    if host_record.get('pshost-access-notes', [None])[0] is not None:
        new_host_record['access_notes'] = host_record.get('pshost-access-notes', [None])[0]


    # return the host record, interfaces and admin details to continue record construction
    return new_host_record, host_record.get('host-net-interfaces', []), host_record.get('host-administrators', [])


def admin_builder(admin_record):
    new_admin_record = {}

    if admin_record.get('person-emails') is not None:
        new_admin_record['emails'] = admin_record.get('person-emails')

    new_admin_record['meta'] = {}

    if admin_record.get('location-city', [None])[0] is not None:
        new_admin_record['meta']['location_city'] = admin_record.get('location-city', [None])[0]

    if admin_record.get('expires') is not None:
        new_admin_record['meta']['expires'] = admin_record.get('expires')

    if admin_record.get('location-code', [None])[0] is not None:
        new_admin_record['meta']['location_code'] = admin_record.get('location-code', [None])[0]

    if admin_record.get('_lastUpdated') is not None:
        new_admin_record['meta']['_lastUpdated'] = admin_record.get('_lastUpdated')

    if admin_record.get('person-organization', [None])[0] is not None:
        new_admin_record['meta']['person_organization'] = admin_record.get('person-organization', [None])[0]

    if admin_record.get('type', [None])[0] is not None:
        new_admin_record['meta']['record_type'] = admin_record.get('type', [None])[0]

    if admin_record.get('uri') is not None:
        new_admin_record['meta']['record_uri'] = admin_record.get('uri')

    if admin_record.get('ttl', [None])[0] is not None:
        new_admin_record['meta']['record_ttl'] = admin_record.get('ttl', [None])[0]

    if admin_record.get('location-country', [None])[0] is not None:
        new_admin_record['meta']['location_country'] = admin_record.get('location-country', [None])[0]

    if admin_record.get('location-latitude', [None])[0] is not None:
        new_admin_record['meta']['location_latitude'] = admin_record.get('location-latitude', [None])[0]

    if admin_record.get('location-longitude', [None])[0] is not None:
        new_admin_record['meta']['location_longitude'] = admin_record.get('location-longitude', [None])[0]

    if admin_record.get('client-uuid', [None])[0] is not None:
        new_admin_record['meta']['client_uuid'] = admin_record.get('client-uuid', [None])[0]

    if admin_record.get('location-sitename', [None])[0] is not None:
        new_admin_record['meta']['location_sitename'] = admin_record.get('location-sitename', [None])[0]

    if admin_record.get('state') is not None:
        new_admin_record['meta']['state'] = admin_record.get('state')

    if admin_record.get('person-name', [None])[0] is not None:
        new_admin_record['meta']['person_name'] = admin_record.get('person-name', [None])[0]

    if admin_record.get('location-state', [None])[0] is not None:
        new_admin_record['meta']['location_state'] = admin_record.get('location-state', [None])[0]

    return new_admin_record


def service_builder(service_record):

    new_service_record = {}
    
    service_type =  service_record.get('service-type', [None])[0]

    if (not service_type) or (not(service_type.lower() == "ma" or service_type.lower() == "pscheduler")):
        return None
    
    if service_record.get('service-locator') is not None:
        new_service_record['urls'] = service_record.get('service-locator')

    if service_record.get('service-version', [None])[0] is not None:
        new_service_record['version'] = service_record.get('service-version', [None])[0]

    if service_type.lower() == "ma":
        if service_record.get('service-version', [None])[0] is not None:
            new_service_record['archiver_type'] = service_record.get('service-version', [None])[0]

    if service_type.lower() == "pscheduler":

        if service_record.get('pscheduler-tools') is not None:
            new_service_record['tools'] = service_record.get('pscheduler-tools')

        if service_record.get('pscheduler-tests') is not None:
            new_service_record['tests'] = service_record.get('pscheduler-tests')

    new_service_record['meta'] = {}

    if service_record.get('expires') is not None:
        new_service_record['meta']['expires'] = service_record.get('expires')

    if service_record.get('service-type', [None])[0] is not None:
        new_service_record['meta']['service_type'] = service_record.get('service-type', [None])[0]

    if service_record.get('_lastUpdated') is not None:
        new_service_record['meta']['_lastUpdated'] = service_record.get('_lastUpdated')

    if service_record.get('type', [None])[0] is not None:
        new_service_record['meta']['type'] = service_record.get('type', [None])[0]

    if service_record.get('uri') is not None:
        new_service_record['meta']['uri'] = service_record.get('uri')

    if service_record.get('ttl', [None])[0] is not None:
        new_service_record['meta']['ttl'] = service_record.get('ttl', [None])[0]

    if service_record.get('service-host', [None])[0] is not None:
        new_service_record['meta']['service_host'] = service_record.get('service-host', [None])[0]

    if service_record.get('service-name', [None])[0] is not None:
        new_service_record['meta']['service_name'] = service_record.get('service-name', [None])[0]

    if service_record.get('client-uuid', [None])[0] is not None:
        new_service_record['meta']['client_uuid'] = service_record.get('client-uuid', [None])[0]

    if service_record.get('group-domains') is not None:
        new_service_record['meta']['group_domains'] = service_record.get('group-domains')

    if service_record.get('state', [None])[0] is not None:
        new_service_record['meta']['state'] = service_record.get('state', [None])[0]

    if service_record.get('service-administrators') is not None:
        new_service_record['meta']['service_administrators'] = service_record.get('service-administrators')

    if service_record.get('psservice-eventtypes') is not None:
        new_service_record['meta']['psservice_eventtypes'] = service_record.get('psservice-eventtypes')

    if service_record.get('location-country', [None])[0] is not None:
        new_service_record['meta']['location_country'] = service_record.get('location-country', [None])[0]

    if service_record.get('location-latitude', [None])[0] is not None:
        new_service_record['meta']['location_latitude'] = service_record.get('location-latitude', [None])[0]

    if service_record.get('location-longitude', [None])[0] is not None:
        new_service_record['meta']['location_longitude'] = service_record.get('location-longitude', [None])[0]

    if service_record.get('location-sitename', [None])[0] is not None:
        new_service_record['meta']['location_sitename'] = service_record.get('location-sitename', [None])[0]

    if service_record.get('location-state', [None])[0] is not None:
        new_service_record['meta']['location_state'] = service_record.get('location-state', [None])[0]

    if service_record.get('location-city', [None])[0] is not None:
        new_service_record['meta']['location_city'] = service_record.get('location-city', [None])[0]

    if service_record.get('location-code', [None])[0] is not None:
        new_service_record['meta']['location_code'] = service_record.get('location-code', [None])[0]

    if service_record.get('group-communities') is not None:
        new_service_record['meta']['group_communities'] = service_record.get('group-communities')

    if service_record.get('bwctl-tools') is not None:
        new_service_record['meta']['bwctl_tools'] = service_record.get('bwctl-tools')

    if service_record.get('ma-type', [None])[0] is not None:
        new_service_record['meta']['ma_type'] = service_record.get('ma-type', [None])[0]

    if service_record.get('ma-tests') is not None:
        new_service_record['meta']['ma_tests'] = service_record.get('ma-tests')

    
    return new_service_record

def build_register():
    query = Message()
    operators = Message()
    operators.add(ReservedKeys.RECORD_OPERATOR, ReservedValues.RECORD_OPERATOR_ALL)


    # Query all host records
    operators.add("type", ReservedValues.RECORD_OPERATOR_ALL)
    query.add("type", "host")
    operators.add("expires", ReservedValues.RECORD_OPERATOR_GREATER_THAN)
    query.add("expires", "now")
    operators.add("host-net-interfaces", ReservedValues.RECORD_OPERATOR_EXISTS)
    query.add('host-net-interfaces', 'exists')

    db = ServiceElasticSearch()
    try:
        num_hits, host_records = db.query(query, operators)
    except Exception as e:
        logger.error("Error querying service record type {}".format(str(query.get_map())))
        raise Exception(e)
    
    # For each service record build the entire lookup record matching the new mapping
    for host_record in host_records:
        host_part_record, interface_uris, admin_uris = host_builder(host_record.get('_source',{}))

        # Gather the admin info
        administrators = []
        for admin_uri in admin_uris:
            query = Message()
            operators = Message()
            operators.add(ReservedKeys.RECORD_OPERATOR, ReservedValues.RECORD_OPERATOR_ALL)

            operators.add("type", ReservedValues.RECORD_OPERATOR_ALL)
            query.add("type", "person")
            operators.add("expires", ReservedValues.RECORD_OPERATOR_GREATER_THAN)
            query.add("expires", "now")
            operators.add("uri", ReservedValues.RECORD_OPERATOR_ALL)
            query.add("uri", admin_uri)

            num_hits, admin_records = db.query(query, operators)

            for admin_record in admin_records:
                admin_part_record = admin_builder(admin_record=admin_record.get('_source',{}))
                if admin_part_record:
                    administrators.append(admin_part_record)
        
        # Add administrators to host
        if administrators:
            host_part_record["administrators"] = administrators

        # Gather services
        host_uri = host_part_record.get('meta', {}).get('uri')
        if host_uri:
            query = Message()
            operators = Message()
            operators.add(ReservedKeys.RECORD_OPERATOR, ReservedValues.RECORD_OPERATOR_ALL)

            operators.add("type", ReservedValues.RECORD_OPERATOR_ALL)
            query.add("type", "service")
            operators.add("expires", ReservedValues.RECORD_OPERATOR_GREATER_THAN)
            query.add("expires", "now")
            operators.add("service-host", ReservedValues.RECORD_OPERATOR_ALL)
            query.add("service-host", host_uri)

            num_hits, service_records = db.query(query, operators)

            archive_services = []
            pscheduler_services = []

            for service_record in service_records:
                service_part_record = service_builder(service_record.get('_source', {}))
                # service_part_record is None if the service type is not ma or pscheduler
                if service_part_record:
                    service_type = service_part_record.get('meta', {}).get('service_type', None)
                    if service_type == "ma":
                        archive_services.append(service_part_record)
                    elif service_type == "pscheduler":
                        pscheduler_services.append(service_part_record)
            
            # Add services to host record
            # The original Ls registration client sends registers each service multiple times.
            # Just get the first one since only one ma and pscheduler service per host
            if pscheduler_services:
                host_part_record['pscheduler_service'] = pscheduler_services[0]
            if archive_services:
                host_part_record['archive_service'] = archive_services[0]


        # Query for Interfaces
        for interface_uri in interface_uris:
            query = Message()
            operators = Message()
            operators.add(ReservedKeys.RECORD_OPERATOR, ReservedValues.RECORD_OPERATOR_ALL)

            operators.add("type", ReservedValues.RECORD_OPERATOR_ALL)
            query.add("type", "interface")
            operators.add("expires", ReservedValues.RECORD_OPERATOR_GREATER_THAN)
            query.add("expires", "now")
            operators.add("uri", ReservedValues.RECORD_OPERATOR_ALL)
            query.add("uri", interface_uri)

            num_hits, interface_records = db.query(query, operators)

            for interface_record in interface_records:

                built_record = interface_builder(interface_record.get('_source', {}))

                built_record["host"] = host_part_record

                # Make a call to new server with the built record
                url = os.environ.get('LOOKUP_SERVER_URL', 'http://ls.perfsonar.net/record/')
                for attempt in range(3):
                    try:
                        register_response = requests.post(url, json=built_record, timeout=30)
                        if register_response.ok:
                            logger.info("Successfully registered record: {}".format(register_response.json()))
                            break
                        else:
                            logger.error("Failed to register record (attempt {}): {} {}".format(attempt + 1, register_response.status_code, register_response.text))
                    except requests.exceptions.RequestException as e:
                        logger.error("Request error registering record (attempt {}): {}".format(attempt + 1, str(e)))
                    if attempt < 2:
                        # On failure it waits 1s, then 2s between attempts (backoff of 2^0, 2^1),
                        # logs each failure with the attempt number, and stops retrying on success.
                        time.sleep(2 ** attempt)


if __name__ == "__main__":
    while True:
        build_register()
        # Sleep for 8 minutes
        time.sleep(480)
