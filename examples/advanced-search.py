import urllib.parse

import requests

search_text = 'NAND'
offset = 0
limit = 10

# search_url = parseURLDomain(self.resource)
search_url = 'https://synbiohub.org'

# query = dict(objectType=parseClassName(object_type))
query = dict(objectType='ComponentDefinition')
query = urllib.parse.urlencode(query)
search_text = urllib.parse.quote(search_text)
params = dict(offset=offset, limit=limit)
params = urllib.parse.urlencode(params)
query_url = f'{search_url}/search/{query}&{search_text}/?{params}'
print(query_url)

# return self._search(query_url)
headers = {'Accept': 'text/plain'}
# if self.key:
#     headers['X-authorization'] = self.key

# self.logger.info('search query: %s', url)
response = requests.get(query_url, headers=headers)
if not response:
    # Something went wrong
    print('Failure')
print(response.json())
