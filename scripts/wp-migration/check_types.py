import requests, os
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth(os.environ['WP_DEST_USER'], os.environ['WP_DEST_APP_PASSWORD'])
r = requests.get('https://lesponctuelles.be/wp-json/wp/v2/types', auth=auth)
for slug, info in r.json().items():
    print(slug, '->', info.get('rest_base'), '|', info.get('name'))
