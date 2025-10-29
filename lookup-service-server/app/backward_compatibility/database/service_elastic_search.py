from elasticsearch import Elasticsearch
import os
import ssl
from fastapi import HTTPException
import json
import logging
from datetime import datetime, timezone
import copy
from ..message import Message

logger = logging.getLogger(__name__)

class ServiceElasticSearch:

    instance = None
    esclient = None

    def __init__(self):
        self.init()

    def create_index(self):
        try:
            if not ServiceElasticSearch.esclient.indices.exists(index=os.environ['ELASTIC_V1_INDEX']):
                with open('app/backward_compatibility/database/mapping/es_mapping.json') as file:
                    es_mapping = json.load(file)
        
                with open('app/backward_compatibility/database/mapping/es_settings.json') as file:
                    es_settings = json.load(file)
        
                settings = {
                    "settings": es_settings,
                        "mappings": es_mapping
                    }
                ServiceElasticSearch.esclient.indices.create(index=os.environ['ELASTIC_V1_INDEX'], ignore=400, body=settings)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error handling elasticsearch connection - " + str(e))


    def init(self):

        if not ServiceElasticSearch.instance:

            ServiceElasticSearch.instance = self

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

            ServiceElasticSearch.esclient = Elasticsearch(
                os.environ['ELASTIC_HOST'],
                ssl_context=ssl_ctx,
                verify_certs=verify_certs,
                basic_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS']))
            
            # Create the destination index if it does not exist already
            self.create_index()

    def build_elastic_search_request(self, query_request, operator):

        search_request = {}
        
        if operator.lower() == "all":
            logger.debug("Building elastic search request - ALL case")

            for key in query_request:
                key_as_string = str(key)
                value = query_request.get(key_as_string)
                if value:
                    search_request['query'] = search_request.get('query', {})
                    search_request['query']['bool'] = search_request.get('query').get('bool', {})
                    search_request['query']['bool']['must'] = search_request.get('query').get('bool').get('must', [])
                if type(value) is str:
                    if "*" in value:
                        regex_string = self.process_wild_card_pattern(value)
                        search_request['query']['bool']['must'].append({"regexp":{key_as_string: regex_string}})
                    else:
                        search_request['query']['bool']['must'].append({"match":{key_as_string: value}})
                elif type(value) is list:
                    logger.debug("Query values are list - ALL case")
                    for value_obj in value:
                        str_val = str(value_obj)
                        if "*" in str_val:
                            regex_string = self.process_wild_card_pattern(str_val)
                            search_request['query']['bool']['must'].append({"regexp":{key_as_string: regex_string}})
                        else:
                            search_request['query']['bool']['must'].append({"match":{key_as_string: str_val}})
        
        else:
            
            logger.debug("Building elastic search request - ANY case")

            for key in query_request:
                key_as_string = str(key)
                value = query_request.get(key_as_string)
                if value:
                    search_request['query'] = search_request.get('query', {})
                    search_request['query']['bool'] = search_request.get('query').get('bool', {})
                    search_request['query']['bool']['should'] = search_request.get('query').get('bool').get('should', [])
                if type(value) is str:
                    if "*" in value:
                        regex_string = self.process_wild_card_pattern(value)
                        search_request['query']['bool']['should'].append({"regexp":{key_as_string: regex_string}})
                    else:
                        search_request['query']['bool']['should'].append({"match":{key_as_string: value}})
                elif type(value) is list:
                    logger.debug("Query values are list - ALL case")
                    for value_obj in value:
                        str_val = str(value_obj)
                        if "*" in str_val:
                            regex_string = self.process_wild_card_pattern(str_val)
                            search_request['query']['bool']['should'].append({"regexp":{key_as_string: regex_string}})
                        else:
                            search_request['query']['bool']['should'].append({"match":{key_as_string: str_val}})

        logger.debug("Built record to search {}".format(search_request.__str__()))

        return search_request
    
    def process_wild_card_pattern(self, search_term):

        if not search_term:
            return search_term
        
        regexp_search_term = search_term
        if "*" in search_term:
            regexp_search_term = search_term.lower().replace("*", ".*")

        return regexp_search_term

            
    def query(self, query_request, operators):
        '''
        Method to query records from database. // Todo fix documentation

        Parameters
        ----------
        queryRequest query keywords extracted from the original request
        operators operators like ANY, ALL that specifies how query keywords should be applied
        maxResults max results to be returned. not implemented

        Returns
        ----------    
        Number of hits
        '''

        logger.debug("operator: " + str(operators.get_map()))
        logger.debug("query_request: " + str(query_request.get_map()))

        operator = operators.get_map().get("operator")
        search_request = self.build_elastic_search_request(query_request.get_map(), operator)

        response = ServiceElasticSearch.esclient.search(
            index=os.environ['ELASTIC_V1_INDEX'],
            body=search_request
        )

        num_hits = int(response["hits"]["total"]["value"])

        return num_hits


    def query_and_publish_service(self, message, query_request, operators):
        """
        Inserts record into database. The method checks if a record exists before
        inserting it into the database.

        Parameters
        ----------
        message record to be added to the database

        Returns
        ----------
        Message that was added to the database

        Raises
        ----------
        DuplicateEntryException
            if database already contains the record that is being added
        DatabaseException
        """
        try:
            logger.debug("Running query for duplicates")
            num_dup_entries = self.query(query_request, operators)
            if num_dup_entries > 0:
                raise Exception("Record already exists.")
        except Exception as e:
            logger.error("Error inserting record")
            raise Exception(e)
        
        timestamped_message = self.add_time_stamp(message)
        self.insert(timestamped_message)
        return_message = self.remove_ls_added_fields(timestamped_message)
        logger.info("Insert Successful")
        logger.info(return_message)
        return return_message


    def remove_ls_added_fields(self, message):
        if message:
            message_map = copy.deepcopy(message.get_map())
            if 'id' in message_map:
                del message_map['_id']
            if '_lastUpdated' in message_map:
                del message_map['_lastUpdated']
        else:
            message_map = {}

        return Message(message_map)

    def insert(self, message):
        """
        Inserts message into database

        Parameters
        ----------
        message message to be inserted into database
        """
        try:
            resp = ServiceElasticSearch.esclient.index(index=os.environ['ELASTIC_V1_INDEX'], document=message.get_map())
            logger.info('Record with URI {} submitted for creation with the result {}'.format(message.get_URI(), str(resp)))
        except Exception as e:
            logger.error ("Error inserting message: {}".format(str(message.get_map())))
            raise Exception(e)

    def add_time_stamp(self, message):
        """
        Adds a timestamp and a lastupdated field to a given message
        Parameters
        ----------
        message message to which timestamp is to be added

        Returns
        ----------
        message with the timestamp and lastupdated field

        """
        message.add("_lastUpdated", datetime.now(timezone.utc).isoformat())
        return message
        