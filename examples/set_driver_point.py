from volttron.web.client import Authentication, Platforms
# point format --> 'Campus/Building2/Fake4/SampleWritableFloat1'
point = input('Point to set: ')
value = input('New value for point: ')
Authentication(auth_url="http://localhost:8080/authenticate", username="admin", password="admin")
v1 = Platforms().get_platform('volttron1')
driver = v1.get_agent('platform.driver')
path, point_name = point.rsplit('/', 1)
rpc_response = driver.rpc.execute('set_point', path=path, point_name=point_name, value=value)
print(f'{path}/{point_name} has value: {rpc_response.data}')
