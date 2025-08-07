import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime, timedelta
from load_host_configs import load_host_configs

from volttron.web.client import Authentication, Platforms


# Get host configuration for VOLTTRON Web Service:
vui_host, username, password = load_host_configs('host_config.json')

# Collect inputs:
now = datetime.utcnow()
topic = input('Topic to query: ')
start = input('Start from: ') or (now - timedelta(seconds=900)).isoformat()
end = input('End at: ') or now.isoformat()
skip = input('Number of rows to skip: ') or 0
skip = int(skip) if skip else skip
count = input('Number of rows to query: ') or None
count = int(count) if count else count
order = input ('Order as: ') or 'FIRST_TO_LAST'

# Authenticate to API
Authentication(auth_url=f"http://{vui_host}/authenticate", username=username, password=password)

# Get platform
v1 = Platforms().get_platform('volttron1')

# Get historian agent
historian = v1.get_agent('platform.historian')

# Query data
rpc_response = historian.rpc.execute('query', topic=topic, start=start, end=end, skip=skip, count=count, order=order)

# Print output
print(f'Query returns: ')
pprint(rpc_response.data)

# Plot output
x, y = zip(*rpc_response.data['values'])
fig, ax = plt.subplots(figsize=(3, 2))
ax.plot(x, y)
ax.set_title('Sample Writable Float 1')
plt.show()


