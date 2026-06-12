from ipaddress import ip_address, IPv6Address, IPv4Address
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch
from opensearchpy import OpenSearch
from fastapi import HTTPException
import json
import os
import logging
import ssl

logger = logging.getLogger(__name__)

_database = os.environ.get('DATABASE', '')
_elastic_client = None
_opensearch_client = None

if _database.startswith('elastic'):
    verify_certs_val = os.environ.get('ELASTIC_VERIFY_CERTS', 'false').lower()
    if verify_certs_val == '1' or verify_certs_val.startswith('t') or verify_certs_val.startswith('y'):
        _ssl_ctx = ssl.create_default_context(cafile=os.environ['ELASTIC_CA_CERT'])
        _ssl_ctx.check_hostname = True
        _ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        _elastic_client = Elasticsearch(
            os.environ['ELASTIC_HOST'],
            ssl_context=_ssl_ctx,
            verify_certs=True,
            basic_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS'])
        )
    else:
        _ssl_ctx = ssl.create_default_context()
        _ssl_ctx.check_hostname = False
        _ssl_ctx.verify_mode = ssl.CERT_NONE
        _elastic_client = Elasticsearch(
            os.environ['ELASTIC_HOST'],
            ssl_context=_ssl_ctx,
            verify_certs=False,
            basic_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS'])
        )

elif _database.startswith('opensearch'):
    verify_certs_val = os.environ.get('OS_VERIFY_CERTS', 'false').lower()
    if verify_certs_val == '1' or verify_certs_val.startswith('t') or verify_certs_val.startswith('y'):
        _opensearch_client = OpenSearch(
            os.environ['OS_HOST'],
            ca_certs=os.environ['OS_CA_CERT'],
            verify_certs=True,
            http_auth=(os.environ['OS_USER'], os.environ['OS_PASS'])
        )
    else:
        _opensearch_client = OpenSearch(
            os.environ['OS_HOST'],
            verify_certs=False,
            http_auth=(os.environ['OS_USER'], os.environ['OS_PASS'])
        )

def map_dbspec(record):
    ip_version = set()

    for ip in record['addresses']:
        if type(ip_address(ip)) is IPv6Address:
            ip_version.add(6)
        elif type(ip_address(ip)) is IPv4Address:
            ip_version.add(4)

    record['ip_versions'] = list(ip_version)
    record['@timestamp'] = datetime.now(timezone.utc)
    if record.get('meta', {}).get('expires'):
        record['expires'] = record['meta']['expires']
    else:
        record['expires'] = record['@timestamp'] + timedelta(hours=24)

    return record

def map_record_id(record):
    record_id = record['host']['client_uuid']
    record_id += '-' + '-'.join(sorted(record['addresses']))
    return record_id

def post_to_opensearch(record):
    try:
        if not _opensearch_client.indices.exists(index=os.environ['OS_INDEX']):
            with open('app/mapping/os_mapping.json') as file:
                os_mapping = json.load(file)

            with open('app/mapping/os_settings.json') as file:
                os_settings = json.load(file)

            settings = {
                "settings": os_settings,
                "mappings": os_mapping
            }

            _opensearch_client.indices.create(index=os.environ['OS_INDEX'], body=settings)

        record_id = map_record_id(record)
        resp = _opensearch_client.index(index=os.environ['OS_INDEX'], body=record, id=record_id, refresh=True)
        logger.info('Record with id {} submitted for creation with the result {}'.format(record_id, resp))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error handling opensearch connection - " + str(e))

    return resp

def post_to_elastic(record):
    try:
        if not _elastic_client.indices.exists(index=os.environ['ELASTIC_INDEX']):
            with open('app/mapping/es_mapping.json') as file:
                es_mapping = json.load(file)

            with open('app/mapping/es_settings.json') as file:
                es_settings = json.load(file)

            settings = {
                "settings": es_settings,
                "mappings": es_mapping
            }

            _elastic_client.indices.create(index=os.environ['ELASTIC_INDEX'], ignore=400, body=settings)

        record_id = map_record_id(record)
        resp = _elastic_client.index(index=os.environ['ELASTIC_INDEX'], document=record, id=record_id)
        logger.info('Record with id {} submitted for creation with the result {}'.format(record_id, resp))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error handling elasticsearch connection - " + str(e))

    return resp
