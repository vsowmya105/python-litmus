import urllib
import os
import json
import io
import requests
project = os.environ['project_name']
envi = os.environ['environment_name']
expt = os.environ['experiment']

url='https://raw.githubusercontent.com/sowmyav10/python/python/'
url = url + project + '/' + envi + '.json'
print(url)

response = urllib.urlopen(url)
data_json = json.loads(response.read())
print(data_json)

print(expt)
print(project)
print(envi)
