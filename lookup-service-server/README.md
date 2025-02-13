# Lookup Service Server
Server to receive records from the clients and store in a database

# Deploying the server
The records are posted to elasticsearch or opensearch.
The following environment variables are needed for the database connection.

    DATABASE - elasticsearch or opensearch
    
**ElasticSearch**
        1. ELASTIC_VERIFY_CERTS - True or False to verify certs
        2. ELASTIC_CA_CERT - Path to CA cert if verify certs set to true
        3. ELASTIC_HOST
        4. ELASTIC_USER
        5. ELASTIC_PASS
        6. ELASTIC_INDEX
    
**OpenSearch**
        1. OS_VERIFY_CERTS
        2. OS_CA_CERT
        3. OS_HOST
        4. OS_USER
        5. OS_PASS
        6. OS_INDEX

# Note for Developers:

1. Schema for record validation
```
lookup-service-client/pslookup/perfsonar-pslookup/schema/schema.json
```
2. Any modification to the schema will be reflected in the client package and server.
3. Changes in the mapping should be complimented with updates to the database mappings.
```
lookup-service-server/app/mapping
```
4. Context for Docker build is the root of the respository since the server needs access to schema from the client.
    To build the docker image locally.
```
docker build -f lookup-service-server/Dockerfile .
```
