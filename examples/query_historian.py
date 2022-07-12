from pprint import pprint
from volttron.web.client import Authentication, Platforms
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


now = datetime.utcnow()
# Collect inputs:
topic = input('Topic to query: ')
start = input('Start from: ') or (now - timedelta(seconds=900)).isoformat()
end = input('End at: ') or now.isoformat()
skip = input('Number of rows to skip: ') or 0
count = input('Number of rows to query: ') or None
order = input ('Order as: ') or 'FIRST_TO_LAST'

# Authenticate to API
Authentication(auth_url="http://localhost:8080/authenticate", username="admin", password="admin")

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
fig, ax = plt.subplots(figsize=(3, 2), constrained_layout=True)
ax.plot(x, y)
ax.set_title('Sample Writable Float 1')
plt.show()


