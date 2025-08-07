from load_host_configs import load_host_configs

from volttron.web.client import Authentication, Platforms


# Get host configuration for VOLTTRON Web Service:
vui_host, username, password = load_host_configs('host_config.json')

# Collect input:
# point format --> 'Campus/Building2/Fake4/SampleWritableFloat1'
point = input('Point to set: ')
value = input('New value for point: ')
path, point_name = point.rsplit('/', 1)

# Authenticate to API:
Authentication(auth_url=f"http://{vui_host}/authenticate", username=username, password=password)

# Get platform:
v1 = Platforms().get_platform('volttron1')

# Get driver agent:
driver = v1.get_agent('platform.driver')

# Send data to Platform Driver:
rpc_response = driver.rpc.execute('set_point', path=path, point_name=point_name, value=value)

# Print return value:
print(f'{path}/{point_name} has value: {rpc_response.data}')
