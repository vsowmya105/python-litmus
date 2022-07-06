#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import random
import os
import sys
from requests.auth import HTTPDigestAuth

LITMUS_URL = 'http://a3607a9d70c94459caced98ef4a1407c-528077293.us-east-1.elb.amazonaws.com:9091/'
LITMUS_USERNAME = 'admin'
LITMUS_PASSWORD = 'litmus'
LITMUS_PROJECT_ID = '752ed631-5346-4d10-89e7-757dcfa3c630'
LITMUS_CLUSTER_ID = 'c64d87d2-da08-4667-8daa-4bb20458fd9f'
MONGODB_ATLAS_PUBLIC_KEY = ''
MONGODB_ATLAS_PRIVATE_KEY = ''
LITMUS_PROJECT_ID = ''
test_result_dict = {}
global_config_data = ''
running_workflow_details = ''
probe_url = ''
experiment_type = ''
config_data_res = ''


def get_auth_token():
    cred_data = {'username': LITMUS_USERNAME,
                 'password': LITMUS_PASSWORD}
    response = requests.post(LITMUS_URL + '/auth/login',
                             json.dumps(cred_data))
    return response


############################################
def get_cluster_id():
    response = get_auth_token()
    access_token = response.json()['access_token']

    headers = {'authorization': access_token, 'Content-type': 'application/json'}
    data = {
    "operationName": "getClusters",
    "variables": {
        "project_id": "752ed631-5346-4d10-89e7-757dcfa3c630"
    },
    "query": "query getClusters($project_id: String!) {\n  getCluster(project_id: $project_id) {\n    cluster_id\n    __typename\n  }\n}\n"
}
    response = requests.post(LITMUS_URL + '/api/query', data=json.dumps(data), headers=headers)
    #cluster_id=response.json()['data']['getCluster'][0]['cluster_id'];
    print(response.json())
    #print('cluster_id : ' + cluster_id)
    #return cluster_id


##############################################

def execute_pod_kill_experiment():
    pod_delete = config_data_res['pod_delete']
    pod_delete_namespace = pod_delete['eks_ns']
    pod_delete_deployment = pod_delete['eks_pod']
    pod_delete_env = pod_delete['env']
    response = get_auth_token()

    access_token = response.json()['access_token']

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}

    workflow_name = 'pod-kill-workflow-' + get_random_number()
    json_data = get_pod_kill_request_body(workflow_name, pod_delete_namespace,pod_delete_deployment)

    pod_kill_response = requests.post(LITMUS_URL + '/api/query', data=json_data, headers=headers)
    print(pod_kill_response.json())
    print(pod_kill_response.status_code)


####################################################

def get_pod_kill_request_body(workflow_name, namespace, deployment):
    project_id = LITMUS_PROJECT_ID
    cluster_id = LITMUS_CLUSTER_ID
    isCustomWorkflow = bool(True)

    data = {'operationName': 'createChaosWorkFlow',
            'variables': {'ChaosWorkFlowInput': {
                'workflow_manifest': '''{
  "apiVersion": "argoproj.io/v1alpha1",
  "kind": "Workflow",
  "metadata": {
    "name": "updated_workflow_name",
    "namespace": "litmus",
    "labels": {
      "subject": "pod-kill-chaos-workflow_litmus"
    }
  },
  "spec": {
    "arguments": {
      "parameters": [
        {
          "name": "adminModeNamespace",
          "value": "litmus"
        }
      ]
    },
    "entrypoint": "custom-chaos",
    "securityContext": {
      "runAsNonRoot": true,
      "runAsUser": 1000
    },
    "serviceAccountName": "argo-chaos",
    "templates": [
      {
        "name": "custom-chaos",
        "steps": [
          [
            {
              "name": "install-chaos-experiments",
              "template": "install-chaos-experiments"
            }
          ],
          [
            {
              "name": "pod-delete-zw5",
              "template": "pod-delete-zw5"
            }
          ],
          [
            {
              "name": "revert-chaos",
              "template": "revert-chaos"
            }
          ]
        ]
      },
      {
        "name": "install-chaos-experiments",
        "inputs": {
          "artifacts": [
            {
              "name": "pod-delete-zw5",
              "path": "/tmp/pod-delete-zw5.yaml",
              "raw": {
                "data": "apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: |\\n    Deletes a pod belonging to a deployment/statefulset/daemonset\\nkind: ChaosExperiment\\nmetadata:\\n  name: pod-delete\\n  labels:\\n    name: pod-delete\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: latest\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods\\n        verbs:\\n          - create\\n          - delete\\n          - get\\n          - list\\n          - patch\\n          - update\\n          - deletecollection\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - events\\n        verbs:\\n          - create\\n          - get\\n          - list\\n          - patch\\n          - update\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - configmaps\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods/log\\n        verbs:\\n          - get\\n          - list\\n          - watch\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods/exec\\n        verbs:\\n          - get\\n          - list\\n          - create\\n      - apiGroups:\\n          - apps\\n        resources:\\n          - deployments\\n          - statefulsets\\n          - replicasets\\n          - daemonsets\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - apps.openshift.io\\n        resources:\\n          - deploymentconfigs\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - replicationcontrollers\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - argoproj.io\\n        resources:\\n          - rollouts\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - batch\\n        resources:\\n          - jobs\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - delete\\n          - deletecollection\\n      - apiGroups:\\n          - litmuschaos.io\\n        resources:\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n    image: litmuschaos/go-runner:2.0.0\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - ./experiments -name pod-delete\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: TOTAL_CHAOS_DURATION\\n        value: \\"15\\"\\n      - name: RAMP_TIME\\n        value: \\"\\"\\n      - name: FORCE\\n        value: \\"true\\"\\n      - name: CHAOS_INTERVAL\\n        value: \\"5\\"\\n      - name: PODS_AFFECTED_PERC\\n        value: \\"50\\"\\n      - name: LIB\\n        value: litmus\\n      - name: TARGET_PODS\\n        value: \\"\\"\\n      - name: NODE_LABEL\\n        value: \\"\\"\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: pod-delete\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: experiment-job\\n      app.kubernetes.io/version: latest\\n"
              }
            }
          ]
        },
        "container": {
          "args": [
            "kubectl apply -f /tmp/pod-delete-zw5.yaml -n {{workflow.parameters.adminModeNamespace}} |  sleep 30"
          ],
          "command": [
            "sh",
            "-c"
          ],
          "image": "litmuschaos/k8s:latest"
        }
      },
      {
        "name": "pod-delete-zw5",
        "inputs": {
          "artifacts": [
            {
              "name": "pod-delete-zw5",
              "path": "/tmp/chaosengine-pod-delete-zw5.yaml",
              "raw": {
                "data": "apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\"{{workflow.parameters.adminModeNamespace}}\\"\\n  generateName: pod-delete-zw5\\n  labels:\\n    instance_id: 8d042200-c626-4fcd-a83a-aa7d6c90b288\\n    context: pod-delete-zw5_litmus\\n    workflow_name: updated_workflow_name\\nspec:\\n  appinfo:\\n    appns: updated_namespace\\n    applabel: app=updated_deployment\\n    appkind: deployment\\n  engineState: active\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-delete\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\"30\\"\\n            - name: CHAOS_INTERVAL\\n              value: \\"10\\"\\n            - name: FORCE\\n              value: \\"false\\"\\n            - name: PODS_AFFECTED_PERC\\n              value: \\"50\\"\\n        probe: []\\n  annotationCheck: \\"false\\"\\n"
              }
            }
          ]
        },
        "container": {
          "args": [
            "-file=/tmp/chaosengine-pod-delete-zw5.yaml",
            "-saveName=/tmp/engine-name"
          ],
          "image": "litmuschaos/litmus-checker:latest"
        }
      },
      {
        "name": "revert-chaos",
        "container": {
          "image": "litmuschaos/k8s:latest",
          "command": [
            "sh",
            "-c"
          ],
          "args": [
            "kubectl delete chaosengine -l \'instance_id in (8d042200-c626-4fcd-a83a-aa7d6c90b288, )\' -n {{workflow.parameters.adminModeNamespace}} "
          ]
        }
      }
    ],
    "imagePullSecrets": [
      {
        "name": ""
      }
    ],
    "podGC": {
      "strategy": "OnWorkflowCompletion"
    }
  }
}''',
                'cronSyntax': '',
                'workflow_name': 'updated_workflow_name',
                'workflow_description': 'Custom Chaos Workflow',
                'isCustomWorkflow': isCustomWorkflow,
                'weightages': [{'experiment_name': 'pod-delete',
                                'weightage': 10}],
                'project_id': 'updated_project_id',
                'cluster_id': 'updated_cluster_id',
            }},
            'query': '''mutation createChaosWorkFlow($ChaosWorkFlowInput: ChaosWorkFlowInput!) {
  createChaosWorkFlow(input: $ChaosWorkFlowInput) {
    workflow_id
    cronSyntax
    workflow_name
    workflow_description
    isCustomWorkflow
    __typename
  }
}
'''}

    ## replacing values
    updated_workflow_manifest_str = data['variables']['ChaosWorkFlowInput']['workflow_manifest'].replace(
        'updated_workflow_name', workflow_name).replace('updated_namespace', namespace).replace('updated_deployment',
                                                                                                deployment)
    updated_workflow_name_str = data['variables']['ChaosWorkFlowInput']['workflow_name'].replace(
        'updated_workflow_name', workflow_name)
    project_id_str = data['variables']['ChaosWorkFlowInput']['project_id'].replace('updated_project_id', project_id)
    cluster_id_str = data['variables']['ChaosWorkFlowInput']['cluster_id'].replace('updated_cluster_id', cluster_id)

    # Inserting updated values
    data['variables']['ChaosWorkFlowInput']['workflow_manifest'] = updated_workflow_manifest_str
    data['variables']['ChaosWorkFlowInput']['workflow_name'] = updated_workflow_name_str
    data['variables']['ChaosWorkFlowInput']['project_id'] = project_id_str
    data['variables']['ChaosWorkFlowInput']['cluster_id'] = cluster_id_str

    return json.dumps(data)


#######################################################
def get_network_latency_experiment_body(workflow_name, namespace, deployment):
    isCustomWorkflow = bool(True)

    project_id = LITMUS_PROJECT_ID
    cluster_id = LITMUS_CLUSTER_ID

    data = {'operationName': 'createChaosWorkFlow',
            'variables': {'ChaosWorkFlowInput': {
                'workflow_manifest': '''{
  "apiVersion": "argoproj.io/v1alpha1",
  "kind": "Workflow",
  "metadata": {
    "name": "updated_workflow_name",
    "namespace": "litmus",
    "labels": {
      "subject": "network-latency-chaos-workflow_litmus"
    }
  },
  "spec": {
    "arguments": {
      "parameters": [
        {
          "name": "adminModeNamespace",
          "value": "litmus"
        }
      ]
    },
    "entrypoint": "custom-chaos",
    "securityContext": {
      "runAsNonRoot": true,
      "runAsUser": 1000
    },
    "serviceAccountName": "argo-chaos",
    "templates": [
      {
        "name": "custom-chaos",
        "steps": [
          [
            {
              "name": "install-chaos-experiments",
              "template": "install-chaos-experiments"
            }
          ],
          [
            {
              "name": "pod-network-latency-5kn",
              "template": "pod-network-latency-5kn"
            }
          ],
          [
            {
              "name": "revert-chaos",
              "template": "revert-chaos"
            }
          ]
        ]
      },
      {
        "name": "install-chaos-experiments",
        "inputs": {
          "artifacts": [
            {
              "name": "pod-network-latency-5kn",
              "path": "/tmp/pod-network-latency-5kn.yaml",
              "raw": {
                "data": "apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: |\\n    Injects network latency on pods belonging to an app deployment\\nkind: ChaosExperiment\\nmetadata:\\n  name: pod-network-latency\\n  labels:\\n    name: pod-network-latency\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: latest\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods\\n        verbs:\\n          - create\\n          - delete\\n          - get\\n          - list\\n          - patch\\n          - update\\n          - deletecollection\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - events\\n        verbs:\\n          - create\\n          - get\\n          - list\\n          - patch\\n          - update\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - configmaps\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods/log\\n        verbs:\\n          - get\\n          - list\\n          - watch\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods/exec\\n        verbs:\\n          - get\\n          - list\\n          - create\\n      - apiGroups:\\n          - apps\\n        resources:\\n          - deployments\\n          - statefulsets\\n          - replicasets\\n          - daemonsets\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - apps.openshift.io\\n        resources:\\n          - deploymentconfigs\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - replicationcontrollers\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - argoproj.io\\n        resources:\\n          - rollouts\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - batch\\n        resources:\\n          - jobs\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - delete\\n          - deletecollection\\n      - apiGroups:\\n          - litmuschaos.io\\n        resources:\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n    image: litmuschaos/go-runner:2.0.0\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - ./experiments -name pod-network-latency\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: TARGET_CONTAINER\\n        value: \\"\\"\\n      - name: NETWORK_INTERFACE\\n        value: eth0\\n      - name: LIB_IMAGE\\n        value: litmuschaos/go-runner:2.0.0\\n      - name: TC_IMAGE\\n        value: gaiadocker/iproute2\\n      - name: NETWORK_LATENCY\\n        value: \\"2000\\"\\n      - name: TOTAL_CHAOS_DURATION\\n        value: \\"60\\"\\n      - name: RAMP_TIME\\n        value: \\"\\"\\n      - name: JITTER\\n        value: \\"0\\"\\n      - name: LIB\\n        value: litmus\\n      - name: PODS_AFFECTED_PERC\\n        value: \\"50\\"\\n      - name: TARGET_PODS\\n        value: \\"\\"\\n      - name: CONTAINER_RUNTIME\\n        value: docker\\n      - name: DESTINATION_IPS\\n        value: \\"\\"\\n      - name: DESTINATION_HOSTS\\n        value: \\"\\"\\n      - name: SOCKET_PATH\\n        value: /var/run/docker.sock\\n      - name: NODE_LABEL\\n        value: \\"\\"\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: pod-network-latency\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: experiment-job\\n      app.kubernetes.io/runtime-api-usage: \\"true\\"\\n      app.kubernetes.io/version: 2.0.0\\n"
              }
            }
          ]
        },
        "container": {
          "args": [
            "kubectl apply -f /tmp/pod-network-latency-5kn.yaml -n {{workflow.parameters.adminModeNamespace}} |  sleep 30"
          ],
          "command": [
            "sh",
            "-c"
          ],
          "image": "litmuschaos/k8s:latest"
        }
      },
      {
        "name": "pod-network-latency-5kn",
        "inputs": {
          "artifacts": [
            {
              "name": "pod-network-latency-5kn",
              "path": "/tmp/chaosengine-pod-network-latency-5kn.yaml",
              "raw": {
                "data": "apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\"{{workflow.parameters.adminModeNamespace}}\\"\\n  generateName: pod-network-latency-5kn\\n  labels:\\n    instance_id: 543914de-580e-45fb-86de-016c820aed11\\n    context: pod-network-latency-5kn_litmus\\n    workflow_name: updated_workflow_name\\nspec:\\n  engineState: active\\n  appinfo:\\n    appns: updated_namespace\\n    applabel: app=updated_deployment\\n    appkind: deployment\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-network-latency\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\"60\\"\\n            - name: NETWORK_LATENCY\\n              value: \\"2000\\"\\n            - name: JITTER\\n              value: \\"0\\"\\n            - name: CONTAINER_RUNTIME\\n              value: docker\\n            - name: SOCKET_PATH\\n              value: /var/run/docker.sock\\n            - name: PODS_AFFECTED_PERC\\n              value: \\"50\\"\\n        probe: []\\n  annotationCheck: \\"false\\"\\n"
              }
            }
          ]
        },
        "container": {
          "args": [
            "-file=/tmp/chaosengine-pod-network-latency-5kn.yaml",
            "-saveName=/tmp/engine-name"
          ],
          "image": "litmuschaos/litmus-checker:latest"
        }
      },
      {
        "name": "revert-chaos",
        "container": {
          "image": "litmuschaos/k8s:latest",
          "command": [
            "sh",
            "-c"
          ],
          "args": [
            "kubectl delete chaosengine -l \'instance_id in (543914de-580e-45fb-86de-016c820aed11, )\' -n {{workflow.parameters.adminModeNamespace}} "
          ]
        }
      }
    ],
    "imagePullSecrets": [
      {
        "name": ""
      }
    ],
    "podGC": {
      "strategy": "OnWorkflowCompletion"
    }
  }
}''',
                'cronSyntax': '',
                'workflow_name': 'updated_workflow_name',
                'workflow_description': 'Custom Chaos Workflow',
                'isCustomWorkflow': isCustomWorkflow,
                'weightages': [{'experiment_name': 'pod-network-latency',
                                'weightage': 10}],
                'project_id': 'updated_project_id',
                'cluster_id': 'updated_cluster_id',
            }},
            'query': '''mutation createChaosWorkFlow($ChaosWorkFlowInput: ChaosWorkFlowInput!) {
  createChaosWorkFlow(input: $ChaosWorkFlowInput) {
    workflow_id
    cronSyntax
    workflow_name
    workflow_description
    isCustomWorkflow
    __typename
  }
}
'''}

    ## replacing values
    updated_workflow_manifest_str = data['variables']['ChaosWorkFlowInput']['workflow_manifest'].replace(
        'updated_workflow_name', workflow_name).replace('updated_namespace', namespace).replace('updated_deployment',
                                                                                                deployment)
    updated_workflow_name_str = data['variables']['ChaosWorkFlowInput']['workflow_name'].replace(
        'updated_workflow_name', workflow_name)
    project_id_str = data['variables']['ChaosWorkFlowInput']['project_id'].replace('updated_project_id', project_id)
    cluster_id_str = data['variables']['ChaosWorkFlowInput']['cluster_id'].replace('updated_cluster_id', cluster_id)

    ## Inserting updated values
    data['variables']['ChaosWorkFlowInput']['workflow_manifest'] = updated_workflow_manifest_str
    data['variables']['ChaosWorkFlowInput']['workflow_name'] = updated_workflow_name_str
    data['variables']['ChaosWorkFlowInput']['project_id'] = project_id_str
    data['variables']['ChaosWorkFlowInput']['cluster_id'] = cluster_id_str

    return json.dumps(data)


######################################################
def execute_network_latency_experiment():
    pod_network_slowness = config_data_res['pod_nw_slowness']
    pod_network_slowness_namespace = pod_network_slowness['eks_ns']
    pod_network_slowness_deployment = pod_network_slowness['eks_pod']
    pod_network_slowness_env = pod_network_slowness['env']

    response = get_auth_token()

    access_token = response.json()['access_token']

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}
    workflow_name = 'network-latency-workflow-' + get_random_number()
    json_data = get_network_latency_experiment_body(workflow_name, pod_network_slowness_namespace,
                                                    pod_network_slowness_deployment)

    net_latency_response = requests.post(LITMUS_URL + '/api/query',
                                         data=json_data, headers=headers)
    print(net_latency_response.status_code)
    print(net_latency_response.json())


########################################################
def terminate_mongo_atlas_instance():
    mongo_atlas = config_data_res['mongo_atlas']
    pub_key = mongo_atlas['pub_key']
    private_key = mongo_atlas['private_key']
    mongodb_atlas_url = mongo_atlas['atlas_url']

    experiment_status = 'Failed'
    response = requests.post(
        mongodb_atlas_url
        , auth=HTTPDigestAuth(pub_key, private_key))

    if response.status_code == 200:
        experiment_status = 'Succeeded'
    print(experiment_status)


##################################################
def get_random_number():
    return random.randint(99, 99999999).__str__()


####################################################
def load_config_file():
    config_file_name = read_config_file()
    file = open(config_file_name)
    config_data = json.load(file)
    return config_data


###################################################
def read_config_file():
    env = os.environ['environment_name']
    project = os.environ['project_name']
    json_config_path = os.path.join(sys.path[0], project + "/" + "config_" + env + ".json")
    return json_config_path


#############################################################

if __name__ == '__main__':

    config_data_res = load_config_file()
    print(config_data_res)
    print('DATA : CLUSTER ID :')
    get_cluster_id()
    litmus_config = config_data_res['litmus']
    LITMUS_URL = litmus_config['litmus_url']
    LITMUS_PROJECT_ID = litmus_config['litmus_project_id']
    LITMUS_USERNAME = 'admin'
    LITMUS_PASSWORD = 'litmus'
    experiment_type = os.getenv('experiment_type')

    print("Selected Experiment Type :" + experiment_type)

    if experiment_type == 'ALL':
        print(experiment_type)
        execute_pod_kill_experiment()
        execute_network_latency_experiment()
        terminate_mongo_atlas_instance()
    elif experiment_type == 'POD_TERMINATION':
        print(experiment_type)
        execute_pod_kill_experiment()
    elif experiment_type == 'NETWORK_LAG':
        print(experiment_type)
        execute_network_latency_experiment()
    elif experiment_type == 'ATLAS':
        print(experiment_type)
        terminate_mongo_atlas_instance()
    else:
        print("Please enter valid choice[ALL, POD_TERMINATION, NETWORK_LAG, ATLAS, ] ")
