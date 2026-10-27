from flask import Flask, request
import json
import os


app = Flask(__name__)

@app.route('/update_info', methods=['PUT'])
def update_admin_info():
    info = request.get_json()

    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname,'pslookup-record-conf/host.json'), 'r') as json_file:
        host = json.load(json_file)

    location = {}
    if info.get("orgname"):
        location['sitename'] = info.get("orgname")
    admin = {}
    if info.get("admin_email"):
        admin['email'] = [info.get("admin_email")]
    if info.get("admin_name"):
        admin['meta'] = {'name': info.get("admin_name")}
    if info.get("city"):
        location['city'] = info.get("city")
    if info.get("country"):
        location['country'] = info.get("country")
    if info.get("state"):
        location['state_province_region'] = info.get("state")
    if info.get("zip"):
        location['postal_code'] = info.get("zip")
    if info.get("latitude"):
        location['latitude'] = info.get("latitude")
    if info.get("longitude"):
        location['longitude'] = info.get("longitude")
    
    if info.get('node_role'):
        host['host']['role'] = info.get('node_role')
    
    if info.get('node_access_policy'):
        host['host']['access_policy'] = info.get('node_access_policy')

    if info.get('node_access_policy'):
        host['host']['access_policy'] = info.get('node_access_policy')
    
    if info.get('access_notes'):
        host['host']['access_notes'] = info.get('access_notes')

    if info.get('communities'):
        host['host']['group_communities'] = info.get('communities')
    
    if location:
        host['host']['location'] = location

    if admin:
        host['host']['administrators'] = [admin]

    with open(os.path.join(dirname,'pslookup-record-conf/host.json'), 'w') as json_file:
        json.dump(host, json_file)

    return "Record updated"

if __name__ == '__main__':
    app.run()