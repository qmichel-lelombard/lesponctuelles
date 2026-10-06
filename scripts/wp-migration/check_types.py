import requests, os
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth(os.environ['WP_DEST_USER'], os.environ['WP_DEST_APP_PASSWORD'])
r = requests.get('https://lesponctuelles.be/wp-json/wp/v2/types', auth=auth)
print('status:', r.status_code)
data = r.json()
if isinstance(data, dict) and 'code' in data and 'message' in data:
    print('ERROR:', data)
else:
    for slug, info in data.items():
        print(slug, '->', info.get('rest_base'), '|', info.get('name'))
