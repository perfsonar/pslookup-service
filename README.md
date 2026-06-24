# Lookup Service
Lookup Service to register and store host and interface records from perfsonar hosts.
It opaquely handles most record management tasks, such as refreshing a record and avoiding duplicate registrations.<br/>

The [lookup-service-client](/lookup-service-client/) running on the host registers records to the [lookup-service-server](/lookup-service-server/)