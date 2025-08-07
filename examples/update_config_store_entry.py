import sys
from pprint import pprint
from load_host_configs import load_host_configs

from volttron.web.client import Authentication, Platforms


# Get host configuration for VOLTTRON Web Service
vui_host, username, password = load_host_configs('host_config.json')

# Collect input:
agent = input('Agent to update: ')
entry_to_change = input('Configuration name to update: ')

# Authenticate to API:
Authentication(auth_url=f"http://{vui_host}/authenticate", username=username, password=password)

# Get platform:
v1 = Platforms().get_platform('volttron1')

# Get driver agent:
driver = v1.get_agent(agent)

# Get a driver configuration:
entry_list = [e for e in driver.configs.entries if e.key == entry_to_change]
if not entry_list:
    print(f'Did not find a config store entry "{entry_to_change}" on agent: {agent}')
else:
    entry = entry_list[0]
    print('Current configuration store entry: ')
    print(entry.content)
    print('')
    pprint('New entry: ')
    new_entry = '\n'.join(sys.stdin.readlines())
    entry.put(url=entry.link, data=new_entry, headers={'Content-Type': 'application/json'})
