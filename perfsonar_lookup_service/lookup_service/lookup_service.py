import json
import urllib.request
import re
import copy
from .validate_record import RecordValidation
import uuid
import random
import os
import requests
import logging
import sys
import ssl
import json

#Set logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])

# Read default host
def get_default_host_details(default_host_path):
    default_host = {}
    try:
        with open(default_host_path) as host_info:
            default_host = json.load(host_info)
    except Exception as e:
        logger.info('Error reading the default host Info: {}'.format(e))
    return default_host

# Read default interface
def get_default_interface_details(default_interface_path):
    default_interface = {}
    try:
        with open(default_interface_path) as interface_info:
            default_interface = json.load(interface_info)
    except Exception as e:
        logger.info('Error reading the default interface Info: {}'.format(e))
    return default_interface


def register_record(conf, default_host_path, default_interface_path):

    default_host = get_default_host_details(default_host_path)
    default_interface = get_default_interface_details(default_interface_path)

    #Node_metrics url
    try:
        node_exporter_url = conf.get('auto_discover', 'node_exporter_url')
    except Exception as e:
        logger.error('Specify node_exporter_url: {}'.format(e))
        sys.exit('node_exporter_url not accessed from config: {}'.format(e))

    #perfsonar_host_exporter_url
    try:
        perfsonar_host_exporter_url = conf.get('auto_discover', 'perfsonar_host_exporter_url')
    except Exception as e:
        logger.error('Specify perfsonar_host_exporter_url: {}'.format(e))
        sys.exit('perfsonar_host_exporter_url not accessed from config: {}'.format(e))

    # Read node metrics
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        node_metrics = urllib.request.urlopen(node_exporter_url, timeout=30, context=ctx).read().decode("utf-8")
    except urllib.error.URLError as e:
        logger.error('{} request error: {}'.format(node_exporter_url, e))
        sys.exit('{} request error: {}'.format(node_exporter_url, e))

    try:
        perfsonar_metrics = urllib.request.urlopen(perfsonar_host_exporter_url, timeout=30, context=ctx).read().decode("utf-8")
    except urllib.error.URLError as e:
        logger.info('perfsonar host metrics not accessed: {}'.format(e))

    #Get the interface details
    address_lines_re = re.compile(r'node_network_address_info{.*'+'address.*')
    address_lines = address_lines_re.findall(node_metrics)

    # validation instance of record validation
    validation = RecordValidation()

    # Makes name mandatory
    interfaces = {}

    #Get the address details from each line
    for address_line in address_lines:
        address_line_device_re = re.compile('node_network_address_info{.*'+'device="(.*?)"')
        device = address_line_device_re.findall(address_line)

        if device:
            try:
                name = device[-1]

            # If no device details, ignore the issue and proceed
            except Exception as e:
                logger.info("Device name not found for adress line {}".format(address_line))
                pass
        
        # Ignore if no device name!
        if name:
            address_re = re.compile('node_network_address_info{(.*)address="(.*?)"')
            address = address_re.match(address_line)
            try:
                address = address.groups()[-1]
            except Exception as e:
                #Log address not extracted, Ignore record and proceed to next address
                logger.info('Address not found for address line {}, skipping'.format(address_line))
                continue

            scope_re = re.compile('node_network_address_info{(.*)scope="(.*?)"')
            scope = scope_re.match(address_line)
            try:
                scope = scope.groups()[-1]
            except Exception as e:
                # continue processing if scope not found.
                logger.info('scope not found for address line {}, Ignoring'.format(address_line))
                pass

            # Ignore if link-local
            if scope and (scope != 'link-local'):

                # Add the details to interface
                interfaces[name] = interfaces.get(name, {'addresses': []})
                interfaces[name]['addresses'].append(address)

                # Get mtu if not already
                if not interfaces.get(name).get('mtu'):
                    mtu_re = re.compile('node_network_mtu_bytes{.*'+'device="{}"'.format(name)+'.*} (.*)')

                    try:
                        interfaces[name]['mtu'] = int(mtu_re.findall(node_metrics)[-1])
                    except Exception as e:
                        logger.info('mtu not found for address line {}, Ignoring'.format(address_line))
                        pass
                
                # Get capacity if not already
                if not interfaces.get(name).get('capacity'):
                    capacity_re = re.compile('node_network_speed_bytes{.*'+'device="{}"'.format(name)+'.*} (.*)')
                    try:
                        interfaces[name]['capacity'] = int(capacity_re.findall(node_metrics)[-1])
                    except Exception as e:
                        logger.info('capacity not found for address line {}, Ignoring'.format(address_line))
                        pass

                # Add mac if not already
                if not interfaces.get(name).get('mac'):
                    mac_re = re.compile('node_network_info{.*address="(.*?)"'+'.*device="{}"'.format(name))
                    try:
                        interfaces[name]['mac'] = mac_re.findall(node_metrics)[-1]
                    except Exception as e:
                        logger.info('mac not found for address line {}, Ignoring'.format(address_line))
                        pass

    # pscheduler_tests and meta
    pscheduler_tests = default_interface.get('pscheduler_tests')
    if pscheduler_tests:
        host['pscheduler_tests'] = pscheduler_tests

    meta = default_interface.get('meta')
    if meta:
        host['meta'] = meta
    
    #Build Host record
    host = {}

    # Check if host is a vm
    vm = default_host.get('vm')
    if vm:
        host['vm'] = vm

    # administrator
    admns = default_host.get('host', {}).get('administrators')
    if admns:
        for admn in admns:
            for email in admn.get('emails'):
                if email:
                    admin_info = {'emails': admn.get('emails')}
                    if admn.get('meta'):
                        admin_info['meta'] = admn.get('meta')
                    host['administrators'] = host.get('administrators', [])
                    host['administrators'].append(admin_info)
                    break

    #processor core count
    processor_count_re = re.compile('node_softnet_cpu_collision_total{.*cpu=(.*)')
    host['processor_core_count'] = len(processor_count_re.findall(node_metrics))

    #OS kernel
    sysname_re = re.compile('node_uname_info{.*'+'(\{|,| )sysname="(.*?)"')
    release_re = re.compile('node_uname_info{.*'+'(\{|,| )release="(.*?)"')
    try:
        sysname = sysname_re.findall(node_metrics)[-1][-1]
        release = release_re.findall(node_metrics)[-1][-1]
        host['os_kernel'] = sysname + ' ' + release
    except Exception as e:
        logger.info('Host OS kernel not found, Ignoring')
        pass

    # os name
    os_name_re = re.compile('node_os_info{.*'+'(\{|,| )name="(.*?)"')
    try:
        host['os_name'] = os_name_re.findall(node_metrics)[-1][-1]
    except Exception as e:
        logger.info('Host OS Name not found, Ignoring')
        pass

    # os version
    os_version_re = re.compile('node_os_info{.*'+'(\{|,| )version="(.*?)"')
    try:
        host['os_version'] = os_version_re.findall(node_metrics)[-1][-1]
    except Exception as e:
        logger.info('Host OS version not found, Ignoring')
        pass

    # processor speed - sorted by processor number
    speed_re = re.compile('node_cpu_frequency_max_hertz{.*cpu="(.*)')
    speeds = speed_re.findall(node_metrics)
    if speeds:
        try:
            cpu_speeds = {}
            for speed in speeds:
                cpu, speed_hz = speed.split('"} ')
                cpu = int(cpu)
                cpu_speeds[cpu] = speed_hz

            host['processor_speed'] = [x[1] for x in sorted(cpu_speeds.items())]
        
        except Exception as e:
            logger.info('Host Processor Speed not found, Ignoring')
            pass

    # product name
    product_name_re = re.compile('node_dmi_info{.*product_name="(.*?)"')
    try:
        host['product_name'] = product_name_re.findall(node_metrics)[-1]
    except Exception as e:
        logger.info('Host Product name not found, Ignoring')
        pass

    #perfsonar_bundle
    perfsonar_bundle_type_re = re.compile('perfsonar_bundle{.*type="(.*?)"')
    try:
        host['perfsonar_bundle'] = perfsonar_bundle_type_re.findall(perfsonar_metrics)[-1]
    except Exception as e:
        logger.info('Perfsonar bundle type name not found, Ignoring')
        pass

    #perfsonar_version
    perfsonar_bundle_version_re = re.compile('perfsonar_bundle{.*version="(.*?)"')
    try:
        host['perfsonar_version'] = perfsonar_bundle_version_re.findall(perfsonar_metrics)[-1]
    except Exception as e:
        logger.info('Perfsonar Version not found, Ignoring')
        pass

    #net_core_rmem_max
    net_core_rmem_max_re = re.compile('node_sysctl_net_core_rmem_max (\d+.*)')
    try:
        host['net_core_rmem_max'] = float(net_core_rmem_max_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_core_rmem_max not found, Ignoring')
        pass

    #net_core_rmem_default
    net_core_rmem_default_re = re.compile('net_core_rmem_default (\d+.*)')
    try:
        host['net_core_rmem_default'] = float(net_core_rmem_default_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_core_rmem_default not found, Ignoring')
        pass

    #net_core_wmem_max
    net_core_wmem_max_re = re.compile('net_core_wmem_max (\d+.*)')
    try:
        host['net_core_wmem_max'] = float(net_core_wmem_max_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_core_wmem_max_re not found, Ignoring')
        pass

    #net_core_wmem_default
    net_core_wmem_default_re = re.compile('net_core_wmem_default (\d+.*)')
    try:
        host['net_core_wmem_default'] = float(net_core_wmem_default_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_core_wmem_default not found, Ignoring')
        pass

    #node_sysctl_net_ipv4_tcp_rmem_default
    net_ipv4_tcp_rmem_default_re = re.compile('net_ipv4_tcp_rmem_default (\d+.*)')
    try:
        host['net_ipv4_tcp_rmem_default'] = float(net_ipv4_tcp_rmem_default_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_rmem_default not found, Ignoring')
        pass

    #node_sysctl_net_ipv4_tcp_rmem_max
    net_ipv4_tcp_rmem_max_re = re.compile('net_ipv4_tcp_rmem_max (\d+.*)')
    try:
        host['net_ipv4_tcp_rmem_max'] = float(net_ipv4_tcp_rmem_max_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_rmem_max not found, Ignoring')
        pass

    #node_sysctl_net_ipv4_tcp_rmem_min
    net_ipv4_tcp_rmem_min_re = re.compile('net_ipv4_tcp_rmem_min (\d+.*)')
    try:
        host['net_ipv4_tcp_rmem_min'] = float(net_ipv4_tcp_rmem_min_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_rmem_min not found, Ignoring')
        pass

    #node_sysctl_net_ipv4_tcp_wmem_default
    net_ipv4_tcp_wmem_default_re = re.compile('net_ipv4_tcp_wmem_default (\d+.*)')
    try:
        host['net_ipv4_tcp_wmem_default'] = float(net_ipv4_tcp_wmem_default_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_wmem_default not found, Ignoring')
        pass

    #node_sysctl_net_ipv4_tcp_wmem_max
    net_ipv4_tcp_wmem_max_re = re.compile('net_ipv4_tcp_wmem_max (\d+.*)')
    try:
        host['net_ipv4_tcp_wmem_max'] = float(net_ipv4_tcp_wmem_max_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_wmem_max not found, Ignoring')
        pass

    #node_sysctl_net_ipv4_tcp_wmem_min
    net_ipv4_tcp_wmem_min_re = re.compile('net_ipv4_tcp_wmem_min (\d+.*)')
    try:
        host['net_ipv4_tcp_wmem_min'] = float(net_ipv4_tcp_wmem_min_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_wmem_min not found, Ignoring')
        pass

    #net_ipv4_tcp_no_metrics_save
    net_ipv4_tcp_no_metrics_save_re = re.compile('net_ipv4_tcp_no_metrics_save (\d+.*)')
    try:
        host['net_ipv4_tcp_no_metrics_save'] = bool(int(net_ipv4_tcp_no_metrics_save_re.findall(node_metrics)[-1]))
    except Exception as e:
        logger.info('net_ipv4_tcp_no_metrics_save not found, Ignoring')
        pass


    #node_sysctl_net_ipv4_tcp_mtu_probing
    net_ipv4_tcp_mtu_probing_re = re.compile('net_ipv4_tcp_mtu_probing (\d+.*)')
    try:
        host['net_ipv4_tcp_mtu_probing'] = int(net_ipv4_tcp_mtu_probing_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_tcp_mtu_probing not found, Ignoring')
        pass

    #net_core_default_qdisc
    default_qdisc_line_re = re.compile('.*net.core.default_qdisc.*')
    try:
        default_qdisc_line = default_qdisc_line_re.findall(node_metrics)[-1]
        qdisc_value_re = re.compile('.*value="(.*?)"')
        host['net_core_default_qdisc'] = qdisc_value_re.findall(default_qdisc_line)[-1]
    except Exception as e:
        logger.info('net_core_default_qdisc not found, Ignoring')
        pass

    #net_ipv4_conf_all_arp_ignore
    net_ipv4_conf_all_arp_ignore_re = re.compile('node_sysctl_net_ipv4_conf_all_arp_ignore (\d+.*)')
    try:
        host['net_ipv4_conf_all_arp_ignore'] = int(net_ipv4_conf_all_arp_ignore_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_conf_all_arp_ignore not found, Ignoring')
        pass

    #net_ipv4_conf_all_arp_announce
    net_ipv4_conf_all_arp_announce_re = re.compile('net_ipv4_conf_all_arp_announce (\d+.*)')
    try:
        host['net_ipv4_conf_all_arp_announce'] = int(net_ipv4_conf_all_arp_announce_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_ipv4_conf_all_arp_announce not found, Ignoring')
        pass

    #net_ipv4_conf_default_arp_filter
    net_ipv4_conf_default_arp_filter_re = re.compile('net_ipv4_conf_default_arp_filter (\d+.*)')
    try:
        host['net_ipv4_conf_default_arp_filter'] = bool(int(net_ipv4_conf_default_arp_filter_re.findall(node_metrics)[-1]))
    except Exception as e:
        logger.info('net_ipv4_conf_default_arp_filter not found, Ignoring')
        pass

    #net_ipv4_conf_all_arp_filter
    net_ipv4_conf_all_arp_filter_re = re.compile('net_ipv4_conf_all_arp_filter (\d+.*)')
    try:
        host['net_ipv4_conf_all_arp_filter'] = bool(int(net_ipv4_conf_all_arp_filter_re.findall(node_metrics)[-1]))
    except Exception as e:
        logger.info('net_ipv4_conf_all_arp_filter not found, Ignoring')
        pass

    #node_sysctl_net_core_netdev_max_backlog
    net_core_netdev_max_backlog_re = re.compile('node_sysctl_net_core_netdev_max_backlog (\d+.*)')
    try:
        host['net_core_netdev_max_backlog'] = int(net_core_netdev_max_backlog_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('net_core_netdev_max_backlog not found, Ignoring')
        pass

    # group_domains
    group_domains = default_host.get('group_domains')
    if group_domains:
        for domain in group_domains:
            if domain is not None:
                host['group_domains'] = group_domains
                break

    # memory bytes
    memory_bytes_re = re.compile('node_memory_MemTotal_bytes (\d+.*)')
    try:
        host['memory_bytes'] = float(memory_bytes_re.findall(node_metrics)[-1])
    except Exception as e:
        logger.info('memory_bytes not found, Ignoring')
        pass

    # location
    location = default_host.get('location')
    if location:
        host['location'] = location

    # group_communities
    group_communities = default_host.get('group_communities')
    if group_communities:
        for community in group_communities:
            if community is not None:
                host['group_communities'] = group_communities
                break

    # role
    role = default_host.get('role')
    if role:
        host['role'] = role

    # access_policy
    access_policy = default_host.get('access_policy')
    if access_policy:
        host['access_policy'] = access_policy

    # access_notes
    access_notes = default_host.get('access_notes')
    if access_notes:
        host['access_notes'] = access_notes

    # meta
    meta = default_host.get('meta')
    if meta:
        host['meta'] = meta

    # manufacturer
    manufacturer_re = re.compile('node_dmi_info{.*system_vendor="(.*?)"')
    try:
        host['manufacturer'] = manufacturer_re.findall(node_metrics)[-1]
    except Exception as e:
        logger.info('Host manufacturer not found, Ignoring')
        pass

    #net_ipv4_tcp_congestion_control
    net_ipv4_tcp_congestion_control_line_re = re.compile('node_sysctl_info{.*net.ipv4.tcp_congestion_control.*')
    try:
        net_ipv4_tcp_congestion_control_line = net_ipv4_tcp_congestion_control_line_re.findall(node_metrics)[-1]
        net_ipv4_tcp_congestion_control_re = re.compile('.*value="(.*?)"')
        host['net_ipv4_tcp_congestion_control'] = net_ipv4_tcp_congestion_control_re.findall(net_ipv4_tcp_congestion_control_line)[-1]
    except Exception as e:
        logger.info('net_ipv4_tcp_congestion_control not found, Ignoring')
        pass

    #net_ipv4_tcp_available_congestion_control
    net_ipv4_tcp_available_congestion_control_line_re = re.compile('node_sysctl_info{.*net.ipv4.tcp_available_congestion_control.*')
    try:
        net_ipv4_tcp_available_congestion_control_lines = net_ipv4_tcp_available_congestion_control_line_re.findall(node_metrics)
        net_ipv4_tcp_available_congestion_control = []
        for available_control in net_ipv4_tcp_available_congestion_control_lines:
            net_ipv4_tcp_available_congestion_control_re = re.compile('.*value="(.*?)"')
            value = net_ipv4_tcp_available_congestion_control_re.findall(available_control)[-1]
            net_ipv4_tcp_available_congestion_control.append(value)
        if net_ipv4_tcp_available_congestion_control:
            host['net_ipv4_tcp_available_congestion_control'] = net_ipv4_tcp_available_congestion_control
    except Exception as e:
        logger.info('net_ipv4_tcp_available_congestion_control not found, Ignoring')
        pass

    #net_ipv4_tcp_allowed_congestion_control
    net_ipv4_tcp_allowed_congestion_control_line_re = re.compile('node_sysctl_info{.*net.ipv4.tcp_allowed_congestion_control.*')
    try:
        net_ipv4_tcp_allowed_congestion_control_lines = net_ipv4_tcp_allowed_congestion_control_line_re.findall(node_metrics)
        net_ipv4_tcp_allowed_congestion_control = []
        for available_control in net_ipv4_tcp_allowed_congestion_control_lines:
            net_ipv4_tcp_allowed_congestion_control_re = re.compile('.*value="(.*?)"')
            value = net_ipv4_tcp_allowed_congestion_control_re.findall(available_control)[-1]
            net_ipv4_tcp_allowed_congestion_control.append(value)
        if net_ipv4_tcp_allowed_congestion_control:
            host['net_ipv4_tcp_allowed_congestion_control'] = net_ipv4_tcp_allowed_congestion_control
    except Exception as e:
        logger.info('net_ipv4_tcp_allowed_congestion_control not found, Ignoring')
        pass


    # os_architecture
    os_architecture_re = re.compile('node_uname_info{.*machine="(.*?)"')
    try:
        host['os_architecture'] = os_architecture_re.findall(node_metrics)[-1]
    except Exception as e:
        logger.info('os_architecture not found, Ignoring')
        pass

    #Gather host name
    node_name_re = re.compile('nodename="(.*?)"')
    host_name = node_name_re.findall(node_metrics)

    # build and check client_uuid
    uuid_persist_file = '/var/lib/perfsonar/lookup-service/client-uuid.txt'
    existing_uuid = {}
    try:
        with open(uuid_persist_file, 'r') as file:
            for line in file:
                key, val = line.split('=')
                existing_uuid[key] = val
    except Exception as e:
        logger.info('Error reading client UUID: {}'.format(e))

    # Evaluate seed
    logger.info('')
    rd = random.Random()

    # get seed
    seed = int(str(existing_uuid.get('seed', rd.getrandbits(128))).strip())

    # Generate UUID with seed
    rd.seed(seed)
    new_client_uuid = uuid.UUID(int=rd.getrandbits(128), version=4).hex
    new_client_uuid += '-' + host_name[0]

    if existing_uuid:
        if existing_uuid.get('uuid', '').strip() != new_client_uuid:
            logger.info("Possible host name change. Existing UUID {} did not match with Newly generated UUID {}".format(existing_uuid.get('uuid').strip(), new_client_uuid))
    else:
        os.makedirs(os.path.dirname(uuid_persist_file), exist_ok=True)
        with open(uuid_persist_file, 'w') as file:
            file.write('uuid='+new_client_uuid+'\n')
            file.write('seed='+str(seed))

    host['client_uuid'] = existing_uuid.get('uuid', new_client_uuid).strip()

    host['name'] = host_name
    # ips to host name
    for interface in interfaces:
        host['name'] += interfaces[interface]['addresses']
        record = copy.deepcopy(interfaces[interface])
        record['name'] = interface
        record['host'] = host

        # validate record
        registration_record = validation.validate_record(record)

        if not registration_record['validated']:
            logger.error("Error validating record: {}".format(registration_record['error']))

        else:
            logger.info('Record validated')
            server = ''
            try:
                server = conf.get('server_config', 'server')
            except Exception as e:
                logger.info('Error reading server information from config {}'.format(e))
                logger.info('Defaulting to ls.perfsonar.net')
            
            if not server:
                server = 'http://ls.perfsonar.net:80'
            print(server)
            r = requests.post(server.strip('/') + '/record/', json=record)
            logger.info("Posted to the server with response {}".format(r.status_code))
