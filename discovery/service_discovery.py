import os
import json
import time
import logging
import threading
import socket
import requests
from flask import Flask, send_from_directory

JSON_FILE = "servers.json"
servers = {}
servers_lock = threading.Lock()

DISCOVERY_PORT_RANGE = (4242, 4300)
HEALTH_CHECK_TIMEOUT = 3
SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', '15')) 

app = Flask(__name__)



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('orthanc-discovery')


def save_servers_to_json():
    """Save server data to a JSON file."""
    with servers_lock:
        try:
            with open(JSON_FILE, 'w') as f:
                json.dump(servers, f, indent=4)
            print(f"JSON file updated: {JSON_FILE}")
        except Exception as e:
            print(f"Error saving JSON: {e}")

def load_servers_from_json():
    """Load server data from a JSON file."""
    global servers
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            servers = json.load(f)
    else:
        servers = {}


def is_port_open(port, host='127.0.0.1', timeout=3):
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
        if response.status_code == 200:
            system_info = response.json()
            server_info['name'] = f"Orthanc {server_info['web_port']}"
            server_info['version'] = system_info.get('Version', 'Unknown')
            server_info['last_seen'] = time.time()
            server_info['status'] = 'online'
            return True
        return False
    except requests.RequestException:
        return False


def discover_new_servers():
    """Scan local network for Orthanc servers on known ports and update JSON file."""
    hosts_to_check = ['127.0.0.1']
    
    hosts_to_check = list(set(hosts_to_check))  

    for host in hosts_to_check:
        for dicom_port in range(DISCOVERY_PORT_RANGE[0], DISCOVERY_PORT_RANGE[1] + 1):
            web_port = 8042 + (dicom_port - 4242)
            
            server_key = f"{host}:{dicom_port}"
            if server_key in servers:
                continue

            if is_port_open(web_port):
                server_info = {
                    'host': host,
                    'dicom_port': dicom_port,
                    'web_port': web_port,
                    'name': f"Orthanc-{host}-{dicom_port}",
                    'aet': f"ORTHANC{dicom_port - 4242 + 1}",  
                    'first_seen': time.time(),
                    'last_seen': time.time(),
                    'status': 'unknown'
                }

                if check_orthanc_health(server_info):
                    with servers_lock:
                        servers[server_key] = server_info
                    save_servers_to_json()
                    print(f"Discovered new Orthanc server: {server_key} ({server_info['name']})")


def update_server_status():
    """Update the status of registered servers and save to JSON."""
    with servers_lock:
        servers_to_check = list(servers.items())

    for server_key, server_info in servers_to_check:
        if check_orthanc_health(server_info):
            with servers_lock:
                servers[server_key] = server_info
        else:
            with servers_lock:
                if servers[server_key]['status'] == 'online':
                    servers[server_key]['status'] = 'offline'
                    logger.warning(f"Orthanc server went offline: {server_key}")

                if time.time() - servers[server_key]['last_seen'] > 900: 
                    logger.info(f"Removing unreachable Orthanc server: {server_key}")
                    del servers[server_key]

def monitoring_thread():
    """Background thread that monitors servers and discovers new ones."""
    while True:
        try:
            discover_new_servers()
            
            update_server_status()
            
            save_servers_to_json()
            
            logger.info(f"Currently tracking {len(servers)} Orthanc servers")
        
        except Exception as e:
            print(f"Error in monitoring thread: {str(e)}", exc_info=True)
        
        time.sleep(SCAN_INTERVAL)


discover_new_servers()
update_server_status()
save_servers_to_json()  


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  

@app.route('/servers.json')
def get_servers_json():
    """Serve the servers.json file from the root directory."""
    return send_from_directory(ROOT_DIR, 'servers.json', mimetype='application/json')

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

# Serve dashboard.html
@app.route('/dashboard.html')
def dashboard():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'dashboard.html')


if __name__ == '__main__':
    monitor = threading.Thread(target=monitoring_thread, daemon=True)
    monitor.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
