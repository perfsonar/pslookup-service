# Lookup Service Query Guide

This guide covers sample queries for the perfSONAR Lookup Service Elasticsearch query endpoint:

```
http://35.223.142.206/lookup/_search
```

Records are split into separate types: `host`, `interface`, `service`, and `person`.

> **Note on field types:** The full field mapping is available at `http://35.223.142.206/lookup/_mapping`.
>
> - Fields mapped as `keyword` (e.g. `type`, `host-name`, `interface-addresses`) support exact-match `term` queries directly.
> - Fields mapped as `text` (e.g. `service-type`, `location-city`) are analyzed for full-text search. For exact-match `term` queries on these fields, use the `.keyword` subfield (e.g. `service-type.keyword`, `location-city.keyword`).

---

## Hosts

**Query all host records**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [{"term": {"type": "host"}}],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

**Query host by hostname**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "host"}},
          {"term": {"host-name": "host.example.net"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

**Query hosts by community**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "host"}},
          {"term": {"group-communities.keyword": "CommunityName"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

**Query hosts by perfSONAR bundle**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "host"}},
          {"term": {"pshost-bundle.keyword": "perfsonar-tools"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

**Query hosts by role**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "host"}},
          {"term": {"pshost-role.keyword": "science-dmz"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

---

## Interfaces

**Query interface records by IP address**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "interface"}},
          {"term": {"interface-addresses": "198.51.100.1"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

---

## Services

**Query all pScheduler service records**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "service"}},
          {"term": {"service-type.keyword": "pscheduler"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

**Query all measurement archive (MA) service records**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "service"}},
          {"term": {"service-type.keyword": "ma"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

---

## Location

**Query hosts by country**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "host"}},
          {"term": {"location-country.keyword": "US"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

**Query hosts by city**
```
curl -X GET http://35.223.142.206/lookup/_search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"type": "host"}},
          {"term": {"location-city.keyword": "Chicago"}}
        ],
        "filter": [{"range": {"expires": {"gt": "now"}}}]
      }
    },
    "size": 10
  }'
```

