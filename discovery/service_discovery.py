#!/usr/bin/env python3

import os
import json
import time
import logging
import threading
from flask import Flask, jsonify, request, send_from_directory
from urllib.parse import quote as url_quote
import socket
import requests
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('orthanc-discovery')


app = Flask(__name__)

servers = {}
servers_lock = threading.Lock()

SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', '15'))  
DISCOVERY_PORT_RANGE = (4242, 4300) 
HEALTH_CHECK_TIMEOUT = 3  


def is_port_open(host, port, timeout=3):
    """Check if a port is open on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False
    
def check_orthanc_health(server_info):
    """Check if an Orthanc server is healthy using its REST API."""
    try:
        url = f"http://{server_info['host']}:{server_info['web_port']}/system"
        auth = ('orthanc', 'orthanc')
        response = requests.get(url, auth=auth, timeout=HEALTH_CHECK_TIMEOUT)
        response = requests.get(url, timeout=HEALTH_CHECK_TIMEOUT)
        if response.status_code == 200:
            system_info = response.json()
            server_info['name'] = system_info.get('Name', server_info['name'])
            server_info['version'] = system_info.get('Version', 'Unknown')
            server_info['last_seen'] = time.time()
            server_info['status'] = 'online'
            return True
        return False
    except requests.RequestException:
        return False



@app.route('/')
def index():
    return """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=/dashboard.html" />
        </head>
        <body>
            Redirecting to dashboard...
        </body>
    </html>
    """

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'dashboard.html')


if __name__=="__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Orthanc Discovery Service on port {port}")
    app.run(host='0.0.0.0', port=port)