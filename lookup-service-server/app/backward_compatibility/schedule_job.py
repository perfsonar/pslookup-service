from ..backward_compatibility.database.service_elastic_search import ServiceElasticSearch
from ..backward_compatibility.message import Message
from ..backward_compatibility.reserved_keys import ReservedKeys
from ..backward_compatibility.reserved_values import ReservedValues
import requests
import logging
import time
logger = logging.getLogger(__name__)


def interface_builder(interface_record):
    new_interface_record = {}

    # Ignore the expires since they are defaulted to 1 day
    if interface_record.get('interface-capacity', [None])[0]:
        new_interface_record['capacity'] = interface_record.get('interface-capacity', [None])[0]
    if interface_record.get('interface-name', [None])[0]:
        new_interface_record['name'] = interface_record.get('interface-name', [None])[0]

    if interface_record.get('interface-addresses'):
        new_interface_record['addresses'] = interface_record.get('interface-addresses', [None])
    if interface_record.get('pscheduler-tests'):
        new_interface_record['pscheduler_tests'] = interface_record.get('pscheduler-tests', [None])
    if interface_record.get('interface-mtu', [None])[0]:
        new_interface_record['mtu'] = interface_record.get('interface-mtu', [None])[0]
    if interface_record.get('interface-mac', [None])[0]:
        new_interface_record['mac'] = interface_record.get('interface-mac', [None])[0]
    # Add everything else to meta for debugging
    new_interface_record['meta'] = new_interface_record.get('meta', {})
    if interface_record.get('expires', None):
        new_interface_record['meta']['expires'] = interface_record.get('expires', None)
    if interface_record.get('type', [None])[0]:
        new_interface_record['meta']['record_type'] = interface_record.get('type', [None])[0]
    if interface_record.get('uri', None):
        new_interface_record['meta']['record_uri'] = interface_record.get('uri', None)
    if interface_record.get('ttl', [None])[0]:
        new_interface_record['meta']['record_ttl'] = interface_record.get('ttl', [None])[0]
    if interface_record.get('client-uuid', [None])[0]:
        new_interface_record['meta']['record_client_uuid'] = interface_record.get('client-uuid', [None])[0]
    if interface_record.get('group-domains'):
        new_interface_record['meta']['record_group_domains'] = interface_record.get('group-domains', [None])
    if interface_record.get('state', None):
        new_interface_record['meta']['record_state'] = interface_record.get('state', None)
    if interface_record.get('psinterface-type', [None])[0]:
        new_interface_record['meta']['record_interface_type'] = interface_record.get('psinterface-type', [None])[0]

    return new_interface_record
    

def host_builder(host_record):
    new_host_record = {}

    if host_record.get('host-vm', [None])[0]:
        new_host_record['vm'] = bool(int(host_record.get('host-vm')[0]))
    
    # location
    new_host_record['location'] = new_host_record.get('location', {})
    if host_record.get('location-state', [None])[0]:
        new_host_record['location']['state_province_region'] = host_record.get('location-state', [None])[0]
    if host_record.get('location-city', [None])[0]:
        new_host_record['location']['city'] = host_record.get('location-city', [None])[0]
    if host_record.get('location-code', [None])[0]:
        new_host_record['location']['zipcode/ postal code'] = host_record.get('location-code', [None])[0]
    if host_record.get('location-country', [None])[0]:
        new_host_record['location']['country'] = host_record.get('location-country', [None])[0]
    if host_record.get('location-latitude', [None])[0]:
        new_host_record['location']['latitude'] = float(host_record.get('location-latitude')[0])
    if host_record.get('location-longitude', [None])[0]:
        new_host_record['location']['longitude'] = float(host_record.get('location-longitude')[0])
    if host_record.get('location-sitename', [None])[0]:
        new_host_record['location']['sitename'] = host_record.get('location-sitename', [None])[0]

    # Meta
    new_host_record['meta'] = new_host_record.get('meta', {})
    if host_record.get('expires', None):
        new_host_record['meta']['expires'] = host_record.get('expires', None)
    if host_record.get('pshost-install-method', [None])[0]:
        new_host_record['meta']['pshost_install_method'] = host_record.get('pshost-install-method', [None])[0]
    if host_record.get('_lastUpdated', None):
        new_host_record['meta']['_lastUpdated'] = host_record.get('_lastUpdated', None)
    if host_record.get('type', [None])[0]:
        new_host_record['meta']['record_type'] = host_record.get('type', [None])[0]
    if host_record.get('state', None):
        new_host_record['meta']['record_state'] = host_record.get('state', None)
    if host_record.get('host-net-tcp-autotunemaxbuffer-send', [None])[0]:
        new_host_record['meta']['host_net_tcp_autotunemaxbuffer_send'] = host_record.get('host-net-tcp-autotunemaxbuffer-send', [None])[0]
    if host_record.get('host-net-tcp-maxbuffer-recv', [None])[0]:
        new_host_record['meta']['host_net_tcp_maxbuffer_recv'] = host_record.get('host-net-tcp-maxbuffer-recv', [None])[0]
    if host_record.get('host-hardware-cpuid', [None])[0]:
        new_host_record['meta']['host_hardware_cpuid'] = host_record.get('host-hardware-cpuid', [None])[0]
    if host_record.get('uri', None):
        new_host_record['meta']['uri'] = host_record.get('uri', None)
    if host_record.get('ttl', [None])[0]:
        new_host_record['meta']['ttl'] = host_record.get('ttl', [None])[0]
    if host_record.get('host-net-tcp-autotunemaxbuffer-recv', [None])[0]:
        new_host_record['meta']['host_net_tcp_autotunemaxbuffer_recv'] = host_record.get('host-net-tcp-autotunemaxbuffer-recv', [None])[0]
    if host_record.get('host-net-tcp-maxbuffer-send', [None])[0]:
        new_host_record['meta']['host_net_tcp_maxbuffer_send'] = host_record.get('host-net-tcp-maxbuffer-send', [None])[0]
    if host_record.get('host-net-ipv6-enabled', [None])[0]:
        new_host_record['meta']['host_net_ipv6_enabled'] = host_record.get('host-net-ipv6-enabled', [None])[0]
    
    
    
    if host_record.get('host-hardware-processorcore',[None])[0]:
        new_host_record['meta']['host_hardware_processorcore'] = int(host_record.get('host-hardware-processorcore')[0])
    
    if host_record.get('host-os-kernel', [None])[0]:
        new_host_record['os_kernel'] = host_record.get('host-os-kernel', [None])[0]
    if host_record.get('host-os-name', [None])[0]:
        new_host_record['os_name'] = host_record.get('host-os-name', [None])[0]
    if host_record.get('host-hardware-processorspeed', [None])[0]:
        new_host_record['processor_speed'] = host_record.get('host-hardware-processorspeed', [None])[0]
    if host_record.get('host-os-version', [None])[0]:
        new_host_record['os_version'] = host_record.get('host-os-version', [None])[0]
    if host_record.get('host-productname', [None])[0]:
        new_host_record['product_name'] = host_record.get('host-productname', [None])[0]
    if host_record.get('client-uuid', [None])[0]:
        new_host_record['client_uuid'] = host_record.get('client-uuid', [None])[0]
    if host_record.get('pshost-access-policy', [None])[0]:
        new_host_record['access_policy'] = host_record.get('pshost-access-policy', [None])[0]
    if host_record.get('pshost-bundle', [None])[0]:
        new_host_record['perfsonar_bundle'] = host_record.get('pshost-bundle', [None])[0]
    if host_record.get('pshost-bundle', [None])[0]:
        new_host_record['perfsonar_bundle'] = host_record.get('pshost-bundle', [None])[0]
    

    # Bundle version in two places. Populate using one and place the other to meta
    if host_record.get('pshost-bundle-version', [None])[0]:
        new_host_record['perfsonar_version'] = host_record.get('pshost-bundle-version')[0]
        # Add the other version from host_record to meta
        if host_record.get('pshost-toolkitversion', [None])[0]:
            new_host_record['meta']['pshost_toolkitversion'] = host_record.get('pshost-toolkitversion')[0]
    elif host_record.get('pshost_toolkitversion', [None])[0]:
        new_host_record['perfsonar_version'] = host_record.get('pshost_toolkitversion')[0]
    
    if host_record.get('host-manufacturer', [None])[0]:
        new_host_record['manufacturer'] = host_record.get('host-manufacturer', [None])[0]
    if host_record.get('host-hardware-processorcount', [None])[0]:
        new_host_record['processor_core_count'] = int(host_record.get('host-hardware-processorcount', [None])[0])

    if host_record.get('host-net-tcp-congestionalgorithm', [None])[0]:
        new_host_record['net_ipv4_tcp_congestion_control'] = host_record.get('host-net-tcp-congestionalgorithm', [None])[0]
    if host_record.get('host-os-architecture', [None])[0]:
        new_host_record['os_architecture'] = host_record.get('host-os-architecture', [None])[0]
    if host_record.get('host-name'):
        new_host_record['name'] = host_record.get('host-name', [None])
    if host_record.get('group-domains'):
        new_host_record['group_domains'] = host_record.get('group-domains', [None])
    if host_record.get('host-hardware-memory', [None])[0]:
        new_host_record['memory_bytes'] = host_record.get('host-hardware-memory', [None])[0]
    if host_record.get('pshost-role', [None])[0]:
        new_host_record['role'] = host_record.get('pshost-role', [None])[0]
    if host_record.get('group-communities'):
        new_host_record['group_communities'] = host_record.get('group-communities', [None])
    if host_record.get('pshost-access-notes', [None])[0]:
        new_host_record['access_notes'] = host_record.get('pshost-access-notes', [None])[0]


    # return the host record, interfaces and admin details to continue record construction
    return new_host_record, host_record.get('host-net-interfaces'), host_record.get('host-administrators')


def admin_builder(admin_record):
    new_admin_record = {}

    if admin_record.get('person-emails'):
        new_admin_record['emails'] = admin_record.get('person-emails')
    
    new_admin_record['meta'] = {}

    if admin_record.get('location-city', [None])[0]:
        new_admin_record['meta']['location_city'] = admin_record.get('location-city', [None])[0]

    if admin_record.get('expires', None):
        new_admin_record['meta']['expires'] = admin_record.get('expires', None)

    if admin_record.get('location-code', [None])[0]:
        new_admin_record['meta']['location_code'] = admin_record.get('location-code', [None])[0]


    if admin_record.get('_lastUpdated', None):
        new_admin_record['meta']['_lastUpdated'] = admin_record.get('_lastUpdated', None)

    if admin_record.get('person-organization', [None])[0]:
        new_admin_record['meta']['person_organization'] = admin_record.get('person-organization', [None])[0]

    if admin_record.get('type', [None])[0]:
        new_admin_record['meta']['record_type'] = admin_record.get('type', [None])[0]

    if admin_record.get('uri', None):
        new_admin_record['meta']['record_uri'] = admin_record.get('uri', None)

    if admin_record.get('ttl', [None])[0]:
        new_admin_record['meta']['record_ttl'] = admin_record.get('ttl', [None])[0]

    if admin_record.get('location-country', [None])[0]:
        new_admin_record['meta']['location_country'] = admin_record.get('location-country', [None])[0]

    if admin_record.get('location-latitude', [None])[0]:
        new_admin_record['meta']['location_latitude'] = admin_record.get('location-latitude', [None])[0]

    if admin_record.get('location-longitude', [None])[0]:
        new_admin_record['meta']['location_longitude'] = admin_record.get('location-longitude', [None])[0]

    if admin_record.get('client-uuid', [None])[0]:
        new_admin_record['meta']['client_uuid'] = admin_record.get('client-uuid', [None])[0]

    if admin_record.get('location-sitename', [None])[0]:
        new_admin_record['meta']['location_sitename'] = admin_record.get('location-sitename', [None])[0]

    if admin_record.get('state', None):
        new_admin_record['meta']['state'] = admin_record.get('state', None)

    if admin_record.get('person-name', [None])[0]:
        new_admin_record['meta']['person_name'] = admin_record.get('person-name', [None])[0]

    if admin_record.get('location-state', [None])[0]:
        new_admin_record['meta']['location_state'] = admin_record.get('location-state', [None])[0]

    return new_admin_record


def service_builder(service_record):

    new_service_record = {}
    
    service_type =  service_record.get('service-type', [None])[0]

    if (not service_type) or (not(service_type.lower() == "ma" or service_type.lower() == "pscheduler")):
        return None
    
    if service_record.get('service-locator'):
        new_service_record['urls'] = service_record.get('service-locator')
    
    if service_record.get('service-version', [None])[0]:
        new_service_record['version'] = service_record.get('service-version', [None])[0]

    if service_type.lower() == "ma":
        if service_record.get('service-version', [None])[0]:
            new_service_record['archiver_type'] = service_record.get('service-version', [None])[0]
        

    if service_type.lower() == "pscheduler":

        if service_record.get('pscheduler-tools'):
            new_service_record['tools'] = service_record.get('pscheduler-tools')
        
        if service_record.get('pscheduler-tests'):
            new_service_record['tests'] = service_record.get('pscheduler-tests')

    new_service_record['meta'] = {}

    if service_record.get('expires'):
        new_service_record['meta']['expires'] = service_record.get('expires')

    if service_record.get('service-type', [None])[0]:
        new_service_record['meta']['service_type'] = service_record.get('service-type', [None])[0]

    if service_record.get('_lastUpdated'):
        new_service_record['meta']['_lastUpdated'] = service_record.get('_lastUpdated')

    if service_record.get('type', [None])[0]:
        new_service_record['meta']['type'] = service_record.get('type', [None])[0]

    if service_record.get('uri'):
        new_service_record['meta']['uri'] = service_record.get('uri')

    if service_record.get('ttl', [None])[0]:
        new_service_record['meta']['ttl'] = service_record.get('ttl', [None])[0]

    if service_record.get('service-host', [None])[0]:
        new_service_record['meta']['service_host'] = service_record.get('service-host', [None])[0]

    if service_record.get('service-name', [None])[0]:
        new_service_record['meta']['service_name'] = service_record.get('service-name', [None])[0]

    if service_record.get('client-uuid', [None])[0]:
        new_service_record['meta']['client_uuid'] = service_record.get('client-uuid', [None])[0]

    if service_record.get('group-domains'):
        new_service_record['meta']['group_domains'] = service_record.get('group-domains')

    if service_record.get('state', [None])[0]:
        new_service_record['meta']['state'] = service_record.get('state', [None])[0]

    if service_record.get('service-administrators'):
        new_service_record['meta']['service_administrators'] = service_record.get('service-administrators')

    if service_record.get('psservice-eventtypes'):
        new_service_record['meta']['psservice_eventtypes'] = service_record.get('psservice-eventtypes')

    if service_record.get('location-country', [None])[0]:
        new_service_record['meta']['location_country'] = service_record.get('location-country', [None])[0]

    if service_record.get('location-latitude', [None])[0]:
        new_service_record['meta']['location_latitude'] = service_record.get('location-latitude', [None])[0]

    if service_record.get('location-longitude', [None])[0]:
        new_service_record['meta']['location_longitude'] = service_record.get('location-longitude', [None])[0]

    if service_record.get('location-sitename', [None])[0]:
        new_service_record['meta']['location_sitename'] = service_record.get('location-sitename', [None])[0]

    if service_record.get('location-state', [None])[0]:
        new_service_record['meta']['location_state'] = service_record.get('location-state', [None])[0]

    if service_record.get('location-city', [None])[0]:
        new_service_record['meta']['location_city'] = service_record.get('location-city', [None])[0]

    if service_record.get('location-code', [None])[0]:
        new_service_record['meta']['location_code'] = service_record.get('location-code', [None])[0]

    if service_record.get('group-communities'):
        new_service_record['meta']['group_communities'] = service_record.get('group-communities')

    if service_record.get('bwctl-tools'):
        new_service_record['meta']['bwctl_tools'] = service_record.get('bwctl-tools')

    if service_record.get('ma-type', [None])[0]:
        new_service_record['meta']['ma_type'] = service_record.get('ma-type', [None])[0]

    if service_record.get('ma-tests'):
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
    query.add('host-net-interfaces', None)

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
                    administrators.add(admin_part_record)
        
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
                service_type = service_part_record.get('meta', {}).get('service_type', None)
                if service_type == "ma":
                    archive_services.add(service_part_record)
                elif service_type == "pscheduler":
                    pscheduler_services.add(service_part_record)
            
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

                register_response = requests.post('http://ls.perfsonar.net/record/', data=built_record)
                
                logger.info("Register record response: {}".format(register_response.json()))


if __name__ == "__main__":
    while True:
        build_register()
        # Sleep for 5 minutes
        time.sleep(300)
