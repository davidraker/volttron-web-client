import logging
from pprint import pprint
from load_host_configs import load_host_configs

from volttron.web.client import Authentication, Platforms

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('urllib3.connectionpool').setLevel(level=logging.INFO)

# Get host configuration for VOLTTRON Web Service:
vui_host, username, password = load_host_configs('host_config.json')

a = Authentication(auth_url=f"http://{vui_host}/authenticate", username=username, password=password)

volttron1 = Platforms().get_platform("volttron1")
historian = volttron1.get_agent('platform.historian')
pprint(historian.status)
pprint(historian.rpc.execute('get_topic_list').data)

# for p in Platforms().list():
#     #print(p)
#     for a in p.agents:
#         print("Before set")
#         print(a.configs.enabled)
#         a.configs.set_priority(50)
#         print("After set")
#         print(a.configs.enabled)
#
#         print("Remove priority")
#         a.configs.set_enabled(False)
#         print(a.configs.enabled)
#
#     print(p.status)
