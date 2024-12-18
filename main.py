import json
import urllib.request
import re
import collections
import copy
from validate_record import RecordValidation
import uuid
import random
import os
import requests
import logging
from configparser import ConfigParser
import sys
import ssl
import time

#Set logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])

#Read the config file
conf = ConfigParser()

try:
    conf.read('ls-config/ls-registration.conf')
except Exception as e:
    logger.error('Error reading the registration config: {}'.format(e))
    sys.exit('Error reading the registration config: {}'.format(e))

# Get the registration frequency
def get_check_interval():
    try:
        check_interval = int(conf.get('auto_discover', 'check_interval'))
    except Exception as e:
        logger.info('check_interval not read: {}'.format(e))
        logger.info('Defaulting to 3600s')
        check_interval = 3600

    if check_interval < 3600 or check_interval > 86400:
        logger.info('check_interval should be between 3600 and 86400')
        logger.info('Defaulting to 3600s')
        check_interval = 3600
    
    return check_interval

check_interval = get_check_interval()
#If check interval is changed in the config.
check_interval_updated = get_check_interval()

while check_interval <= check_interval_updated:
    
    # For the new turn
    check_interval = get_check_interval()

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


    #######Add pscheduler_tests and meta

    #Build Host record
    host = {}
            
    #How to check if host is a VM???????????
    ###########Add administrator

    #processor core count
    processor_count_re = re.compile('node_softnet_cpu_collision_total{.*cpu=(.*)')
    host['processor_core_count'] = len(processor_count_re.findall(node_metrics))

    #OS kernel??????????????
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

    ##########Add group_domains

    # memory bytes
    memory_bytes_re = re.compile('node_memory_MemTotal_bytes (\d+.*)')
    try:
        host['memory_bytes'] = memory_bytes_re.findall(node_metrics)[-1]
    except Exception as e:
        logger.info('memory_bytes not found, Ignoring')
        pass

    ##########Add location
    ##########Add group_communities
    ##########Add role
    ##########Add access_policy
    ##########Add access_notes
    ##########Add meta

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
    #Add ips to host name
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
            r = requests.post(server.strip('/') + '/record/', json=record)
            logger.info("Posted to the server with response {}".format(r.status_code))

    logger.info("Sleeping for {}s. Next config check/ registration after wakeup.".format(check_interval))
    time.sleep(check_interval)
    
    #If the check interval is updated during sleep.
    check_interval_updated = get_check_interval()