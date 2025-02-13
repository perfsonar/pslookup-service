from ipaddress import ip_address, IPv6Address, IPv4Address
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch
import elasticsearch
import opensearchpy
from opensearchpy import OpenSearch
import json
from fastapi import HTTPException
import os
import logging
import ssl

logger = logging.getLogger(__name__)

def map_dbspec(record):

    ip_version = set()

    for ip in record['addresses']:
        if type(ip_address(ip)) is IPv6Address:
            ip_version.add(6)
        elif type(ip_address(ip)) is IPv4Address:
            ip_version.add(4)
        
    record['ip_versions'] = list(ip_version)
    record['@timestamp'] = datetime.now(timezone.utc)
    record['expires'] = record['@timestamp'] + timedelta(hours=24)

    return record

def map_record_id(record):
    record_id = record['host']['client_uuid']
    record_id += '-' + '-'.join(sorted(record['addresses']))
    return record_id

def post_to_opensearch(record):
    # Create the client instance
    verify_certs_val = os.environ.get('OS_VERIFY_CERTS', 'false').lower()
    if verify_certs_val == '1' or verify_certs_val.startswith('t') or verify_certs_val.startswith('y'):
        verify_certs=True
    else:
        verify_certs=False

    os_client = OpenSearch(
        os.environ['OS_HOST'],
        ca_certs=os.environ['OS_CA_CERT'],
        verify_certs=verify_certs,
        http_auth=(os.environ['OS_USER'], os.environ['OS_PASS'])
    )

    try:
        if not os_client.indices.exists(index=os.environ['OS_INDEX']):
            with open('app/mapping/os_mapping.json') as file:
                os_mapping = json.load(file)
            
            with open('app/mapping/os_settings.json') as file:
                os_settings = json.load(file)
            
            settings = {
                "settings": os_settings,
                    "mappings": os_mapping
                }
            
            os_client.indices.create(index=os.environ['OS_INDEX'], body=settings)

        #Generate record id
        record_id = map_record_id(record)

        #Delete record if exists
        try:
            resp = os_client.delete(index=os.environ['OS_INDEX'], id=record_id)
            if not resp.get('result') == 'deleted':
                logger.debug('record with id {} not deleted'.format(record_id))
        except opensearchpy.exceptions.NotFoundError:
            logger.debug('Record id - {} not found for deletion. Proceeding to add the record'.format(record_id))
            pass

        #Create the record
        resp = os_client.index(index=os.environ['OS_INDEX'], body=record, id=record_id, refresh=True)
        logger.info('Record with id {} submitted for creation with the result {}'.format(record_id, resp))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error handling opensearch connection - " + str(e))

    return resp

def post_to_elastic(record):
    # Create the client instance
    verify_certs_val = os.environ.get('ELASTIC_VERIFY_CERTS', 'false').lower()
    verify_certs=False
    if verify_certs_val == '1' or verify_certs_val.startswith('t') or verify_certs_val.startswith('y'):
        verify_certs=True
        ssl_ctx = ssl.create_default_context(cafile=os.environ['ELASTIC_CA_CERT'])
        ssl_ctx.check_hostname = True
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    else:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

    esclient = Elasticsearch(
        os.environ['ELASTIC_HOST'],
        ssl_context=ssl_ctx,
        verify_certs=verify_certs,
        basic_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS'])
    )
    
    try:
        if not esclient.indices.exists(index=os.environ['ELASTIC_INDEX']):
            with open('app/mapping/es_mapping.json') as file:
                es_mapping = json.load(file)
            
            with open('app/mapping/es_settings.json') as file:
                es_settings = json.load(file)
            
            settings = {
                "settings": es_settings,
                    "mappings": es_mapping
                }
            
            esclient.indices.create(index=os.environ['ELASTIC_INDEX'], ignore=400, body=settings)

        #Generate record id
        record_id = map_record_id(record)

        #Delete record if exists
        try:
            resp = esclient.delete(index=os.environ['ELASTIC_INDEX'], id=record_id)
            if not resp.get('result') == 'deleted':
                logger.debug('record with id {} not deleted'.format(record_id))
        except elasticsearch.NotFoundError:
            logger.debug('Record id - {} not found for deletion. Proceeding to add the record'.format(record_id))
            pass

        #Create the record
        resp = esclient.index(index=os.environ['ELASTIC_INDEX'], document=record, id=record_id)
        logger.info('Record with id {} submitted for creation with the result {}'.format(record_id, resp))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error handling elasticsearch connection - " + str(e))

    return resp