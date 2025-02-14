# Lookup Service Client
 Client daemon that registers records in the lookup service

# Settings and Configs
**For The debian and rpm installations**

systemd service is enabled upon installation and the pslookup client starts with default configurations.

1. [Defaults](pslookup/perfsonar-pslookup/pslookup-config/pslookup-registration.conf) to using the localhost node exporter and perfsonar host exporter
2. Client configuration - Modify the config file registration frequency and default paths for record configurations
```
[/etc/perfsonar/pslookup/pslookup-registration.conf](pslookup/perfsonar-pslookup/pslookup-config/pslookup-registration.conf)
```
3. Record configuration files - To provide data to overwrite or to add to the record. Replace nulls with the values to be placed in the record.
```
Defaults
[/etc/perfsonar/pslookup/pslookup-record-conf/interfaces.json](pslookup/perfsonar-pslookup/pslookup-config/pslookup-record-conf/interfaces.json)
[/etc/perfsonar/pslookup/pslookup-record-conf/host.json](pslookup/perfsonar-pslookup/pslookup-config/pslookup-record-conf/host.json)
```

# Validation Tool
pslookup tool can be used to validate a record.
```
pslookup validate
```
***Customizing
The validation tool allows to validate a record built by the pslookup service using the client config. This will utilize the service to build the record that will be registered and validate it against the schema.
To validate a record built manually, use the record option to point to the json record. If this option is provided, config is ignored.

        | Option | Type | Description |
        | :----: | :--: | :---------: |
        | config | String | Path to the client config file. Defaults to /etc/perfsonar/pslookup/pslookup-registration.conf |
        | record | String | Path to the json record |


# Developer Settings:

1. To modify Schema for record validation
```
[pslookup/perfsonar-pslookup/schema/schema.json](pslookup/perfsonar-pslookup/schema/schema.json)
```
2. The python pslookup package utilizes symlink to the [schema.json](pslookup/perfsonar-pslookup/pslookup/schema/schema.json). Any modification to the schema will be reflected in both the client [package]((pslookup/perfsonar-pslookup/pslookup/schema/schema.json)) and [server](../lookup-service-server/schema/schema.json).
3. Changes in the schema should be complimented with updates to the database mappings and vice versa.
```
[lookup-service-server/app/mapping](../lookup-service-server/app/mapping/)
```
4. Changes to the schema should also be implemented in the default [record configurations](pslookup/perfsonar-pslookup/pslookup-config/pslookup-record-conf/).

**Installing the client locally on Docker**
Using [unibuild](https://github.com/perfsonar/unibuild)
```
git clone https://github.com/perfsonar/pslookup-service.git
cd pslookup-service
wget https://raw.githubusercontent.com/perfsonar/unibuild/main/docker-envs/docker-compose.yml
download the [docker-envs](https://github.com/perfsonar/unibuild/tree/main/docker-envs)
docker compose run el9 bash 
cd lookup-service-client
unibuild build
```
The above will install the service but will fail to start the systemd service. The installation can be tested by running the [pslookup Client Agent](pslookup/perfsonar-pslookup/bin/pslookup_client_agent).
```
/usr/lib/perfsonar/pslookup/bin/pslookup_client_agent --config=/etc/perfsonar/pslookup/pslookup-registration.conf --logger=/etc/perfsonar/pslookup/pslookup-client-agent-logger.conf
```

**Note:**
The record generation process persists a client UUID at the following path. It appends hostnames to UUID to compare changes to the hostname. If any changes are found, the service logs the change in the log files and proceeds to register the record with the new UUID.
```
/var/lib/perfsonar/pslookup/client-uuid.txt
```
The validation tool does not persist the UUID.
