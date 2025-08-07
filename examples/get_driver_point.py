from time import sleep
from load_host_configs import load_host_configs

from volttron.web.client import Authentication, Platforms


# Get host configuration for VOLTTRON Web Service
vui_host, username, password = load_host_configs('host_config.json')

# Collect input:
point = input('Point to retrieve: ')
path, point_name = point.rsplit('/', 1)

# Authenticate to API:
Authentication(auth_url=f"http://{vui_host}/authenticate", username=username, password=password)

# Get platform:
v1 = Platforms().get_platform('volttron1')

# Get driver agent:
driver = v1.get_agent('platform.driver')

for i in range(100):
    # Retrieve data from Platform Driver:
    rpc_response = driver.rpc.execute('get_point', path=path, point_name=point_name)

    # Print output:
    print(f'{path}/{point_name} has value: {rpc_response.data}')
    sleep(1)
