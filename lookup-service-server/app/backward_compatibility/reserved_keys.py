class ReservedKeys:

    #record-level keys
    RECORD_TYPE = "type"
    RECORD_TTL = "ttl"
    RECORD_URI = "uri"
    RECORD_OPERATOR = "operator"
    RECORD_EXPIRES = "expires"
    RECORD_SKIP = "skip"
    RECORD_MAXRESULTS = "maxresults"
    RECORD_PRIVATEKEY = "privatekey"
    RECORD_STATE = "state"

    #error keys
    ERROR_MESSAGE = "error-message"
    ERROR_CODE = "error-code"

    #server (bootstrap) keys
    SERVER_STATUS = "status"
    SERVER_TIMESTAMP = "lastupdated"
    SERVER_LOCATOR = "locator"
    SERVER_PRIORITY = "priority"

    #subscribe keys
    RECORD_SUBSCRIBE_QUEUE = "subscribe-queue"
    RECORD_SUBSCRIBE_LOCATOR = "subscribe-locator"

    #operator keys
    RECORD_OPERATOR_SUFFIX = "operator"

    #group keys
    RECORD_GROUP_DOMAINS = "group-domains"
    RECORD_GROUP_COMMUNITIES = "group-communities"

    #location keys
    RECORD_LOCATION_SITENAME = "location-sitename"
    RECORD_LOCATION_CITY = "location-city"
    RECORD_LOCATION_STATE = "location-state"
    RECORD_LOCATION_COUNTRY = "location-country"
    RECORD_LOCATION_ZIPCODE = "location-zipcode"
    RECORD_LOCATION_LATITUDE = "location-latitude"
    RECORD_LOCATION_LONGITUDE = "location-longitude"

    #service keys
    RECORD_SERVICE_NAME = "service-name"
    RECORD_SERVICE_VERSION = "service-version"
    RECORD_SERVICE_TYPE = "service-type"
    RECORD_SERVICE_LOCATOR = "service-locator"
    RECORD_SERVICE_ADMINISTRATORS = "service-administrators"
    RECORD_SERVICE_HOST = "service-host"
    RECORD_SERVICE_EVENTTYPES = "psservice-eventtypes"

    #interface keys
    RECORD_INTERFACE_NAME = "interface-name"
    RECORD_INTERFACE_ADDRESSES = "interface-addresses"
    RECORD_INTERFACE_SUBNET = "interface-subnet"
    RECORD_INTERFACE_CAPACITY = "interface-capacity"
    RECORD_INTERFACE_MACADDRESS = "interface-mac"
    RECORD_INTERFACE_MTU = "interface-mtu"

    #host keys
    RECORD_HOST_NET_INTERFACES = "host-net-interfaces"
    RECORD_HOST_NET_TCP_MAXBACKLOG = "host-net-tcp-maxbacklog"
    RECORD_HOST_NET_TCP_AUTOTUNEMAXBUFFER_SEND = "host-net-tcp-autotunemaxbuffer-send"
    RECORD_HOST_NET_TCP_AUTOTUNEMAXBUFFER_RECV = "host-net-tcp-autotunemaxbuffer-recv"
    RECORD_HOST_NET_TCP_MAXBUFFER_SEND = "host-net-tcp-maxbuffer-send"
    RECORD_HOST_NET_TCP_MAXBUFFER_RECV = "host-net-tcp-maxbuffer-recv"
    RECORD_HOST_NET_TCP_CONGESTIONALGORITHM = "host-net-tcp-congestionalgorithm"
    RECORD_HOST_OS_NAME = "host-os-name"
    RECORD_HOST_OS_VERSION = "host-os-version"
    RECORD_HOST_OS_KERNEL = "host-os-kernel"
    RECORD_HOST_NAME = "host-name"
    RECORD_HOST_HARDWARE_MEMORY = "host-hardware-memory"
    RECORD_HOST_HARDWARE_PROCESSORSPEED = "host-hardware-processorspeed"
    RECORD_HOST_HARDWARE_PROCESSORCOUNT = "host-hardware-processorcount"
    RECORD_HOST_HARDWARE_PROCESSORCORE = "host-hardware-processorcore"

    #person keys
    RECORD_PERSON_EMAILIDS = "person-emails"
    RECORD_PERSON_PHONENUMBERS = "person-phonenumbers"
    RECORD_PERSON_ORGANIZATION = "person-organization"
    RECORD_PERSON_NAME = "person-name"

    BOOTSTRAP_HOSTS = "hosts"

    #PSMetadata keys (for esmond / perfSONAR)
    RECORD_PSMETADATA_DST_ADDRESS = "psmetadata-dst-address"
    RECORD_PSMETADATA_EVENTTYPES = "psmetadata-event-types"
    RECORD_PSMETADATA_MA_LOCATOR = "psmetadata-ma-locator"
    RECORD_PSMETADATA_MEASUREMENT_AGENT = "psmetadata-measurement-agent"
    RECORD_PSMETADATA_SRC_ADDRESS = "psmetadata-src-address"
    RECORD_PSMETADATA_TOOL_NAME = "psmetadata-tool-name"
    RECORD_PSMETADATA_URI = "psmetadata-uri"

    SUBSCRIBER = "subscriber"
    QUEUE_URL = "queue-url"
    QUEUE = "queue"
    RECORD_SUBSCRIBE_QUEUE_STATE = "queue-state"
    RECORD_SUBSCRIBE_QUEUE_TIMESTAMP = "queue-timestamp"

    RECORD_BULK_URIS = "record-uris"
    RECORD_BULKRENEW_TOTALRECORDS = "total"
    RECORD_BULKRENEW_RENEWEDCOUNT = "renewed"
    RECORD_BULKRENEW_FAILURECOUNT = "failure"
    RECORD_BULKRENEW_FAILUREURIS = "failed-uris"
    RECORD_BULKRENEW_RENEWEDURIS = "renewed-uris"
