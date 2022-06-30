import urllib.request
from urllib.request import urlopen
import os
import json
import io
import requests
url='https://raw.githubusercontent.com/sowmyav10/python/python/project1/dev.json'
response = urlopen(url)
data_json = json.loads(response.read())
print(data_json)
project = os.environ['project_name']
envi = os.environ['environment_name']
expt = os.environ['experiment']
print(expt)
print(project)
print(envi)
