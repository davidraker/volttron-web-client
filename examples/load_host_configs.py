import json


def load_host_configs(host_config_path='host_config.json'):
    # Get host configurations for VOLTTRON Web Service
    with open(host_config_path, 'r') as f:
        host_config = json.load(f)
    vui_host = host_config.get('vui_host')
    username = host_config.get('vui_username', 'admin')
    password = host_config.get('vui_password', 'admin')
    return vui_host, username, password