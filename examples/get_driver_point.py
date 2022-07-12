from volttron.web.client import Authentication, Platforms
point = input('Point to retrieve: ')
Authentication(auth_url="http://localhost:8080/authenticate", username="admin", password="admin")
v1 = Platforms().get_platform('volttron1')
driver = v1.get_agent('platform.driver')
# path = 'Campus/Building2/Fake4'
# point_name = 'SampleWritableFloat1'
path, point_name = point.rsplit('/', 1)
rpc_response = driver.rpc.execute('get_point', path=path, point_name=point_name)
print(f'{path}/{point_name} has value: {rpc_response.data}')
