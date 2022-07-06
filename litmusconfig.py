import urllib
import sys
import os
import json
import io
import requests
project = os.environ['project_name']
envi = os.environ['environment_name']
expt = os.environ['experiment_type']

def read_config_file():
    json_config_path = os.path.join(sys.path[0], project + "/config_"  + envi + ".json")
    return json_config_path
  
def load_config_file():
    config_file_name = read_config_file()
    file = open(config_file_name)
    config_data = json.load(file)
    return config_data
  
data=load_config_file()
print('DATA : ')
print(data)

