import os
import json
import io
import requests
url='https://raw.githubusercontent.com/sowmyav10/python/blob/python/project1/dev.json'
page = requests.get(url)
print(page.json())
project = os.environ['project_name']
envi = os.environ['environment_name']
expt = os.environ['experiment']
print(expt)
print(project)
print(envi)
