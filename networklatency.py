#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import random

LITMUS_URL = 'http://a3607a9d70c94459caced98ef4a1407c-528077293.us-east-1.elb.amazonaws.com:9091/'
LITMUS_USERNAME = 'admin'
LITMUS_PASSWORD = 'litmus'
LITMUS_PROJECT_ID = '752ed631-5346-4d10-89e7-757dcfa3c630'
LITMUS_CLUSTER_ID = 'c64d87d2-da08-4667-8daa-4bb20458fd9f'
POD_DELETE_NAMESPACE = 'nginx'
POD_DELETE_DEPLOYMENT = 'nginx'


def get_auth_token():
    cred_data = {'username': LITMUS_USERNAME,
                 'password': LITMUS_PASSWORD}
    response = requests.post(LITMUS_URL + '/auth/login',
                             json.dumps(cred_data))
    return response


############################################

def get_random_number():
    return random.randint(99, 99999999).__str__()


def get_cluster_id():
    response = get_auth_token()
    access_token = response.json()['access_token']

    headers = {'authorization': access_token, 'Content-type': 'application/json'}
    data = {
        "operationName": "getClusters",
        "variables": {
            "project_id": LITMUS_PROJECT_ID
        },
        "query": "query getClusters($project_id: String!, $cluster_type: String) {\n  getCluster(project_id: $project_id, cluster_type: $cluster_type) {\n    cluster_id\n    cluster_name\n    description\n    is_active\n    is_registered\n    is_cluster_confirmed\n    updated_at\n    created_at\n    cluster_type\n    no_of_schedules\n    no_of_workflows\n    token\n    last_workflow_timestamp\n    agent_namespace\n    agent_scope\n    version\n    __typename\n  }\n}\n"
    }
    response = requests.post(LITMUS_URL + '/api/query', data=json.dumps(data), headers=headers)
    cluster_id = response.json()['data']['getCluster'][0]['cluster_id']
    return cluster_id


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
                "data": "apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: |\\n    Injects network latency on pods belonging to an app deployment\\nkind: ChaosExperiment\\nmetadata:\\n  name: pod-network-latency\\n  labels:\\n    name: pod-network-latency\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: latest\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods\\n        verbs:\\n          - create\\n          - delete\\n          - get\\n          - list\\n          - patch\\n          - update\\n          - deletecollection\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - events\\n        verbs:\\n          - create\\n          - get\\n          - list\\n          - patch\\n          - update\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - configmaps\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods/log\\n        verbs:\\n          - get\\n          - list\\n          - watch\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - pods/exec\\n        verbs:\\n          - get\\n          - list\\n          - create\\n      - apiGroups:\\n          - apps\\n        resources:\\n          - deployments\\n          - statefulsets\\n          - replicasets\\n          - daemonsets\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - apps.openshift.io\\n        resources:\\n          - deploymentconfigs\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - \\"\\"\\n        resources:\\n          - replicationcontrollers\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - argoproj.io\\n        resources:\\n          - rollouts\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - batch\\n        resources:\\n          - jobs\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - delete\\n          - deletecollection\\n      - apiGroups:\\n          - litmuschaos.io\\n        resources:\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n    image: 405524983081.dkr.ecr.ap-southeast-1.amazonaws.com/aella-xplatform-ecr/facility/litmuschaos/go-runner\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - ./experiments -name pod-network-latency\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: TARGET_CONTAINER\\n        value: \\"\\"\\n      - name: NETWORK_INTERFACE\\n        value: eth0\\n      - name: LIB_IMAGE\\n        value: litmuschaos/go-runner:latest\\n      - name: TC_IMAGE\\n        value: gaiadocker/iproute2\\n      - name: NETWORK_LATENCY\\n        value: \\"2000\\"\\n      - name: TOTAL_CHAOS_DURATION\\n        value: \\"60\\"\\n      - name: RAMP_TIME\\n        value: \\"\\"\\n      - name: JITTER\\n        value: \\"0\\"\\n      - name: LIB\\n        value: litmus\\n      - name: PODS_AFFECTED_PERC\\n        value: \\"50\\"\\n      - name: TARGET_PODS\\n        value: \\"\\"\\n      - name: CONTAINER_RUNTIME\\n        value: docker\\n      - name: DESTINATION_IPS\\n        value: \\"\\"\\n      - name: DESTINATION_HOSTS\\n        value: \\"\\"\\n      - name: SOCKET_PATH\\n        value: /var/run/docker.sock\\n      - name: NODE_LABEL\\n        value: \\"\\"\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: pod-network-latency\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: experiment-job\\n      app.kubernetes.io/runtime-api-usage: \\"true\\"\\n      app.kubernetes.io/version: latest\\n"
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
          "image": "405524983081.dkr.ecr.ap-southeast-1.amazonaws.com/aella-xplatform-ecr/facility/litmuschaos/k8s:latest"
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
                "data": "apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\"{{workflow.parameters.adminModeNamespace}}\\"\\n  generateName: pod-network-latency-5kn\\n  labels:\\n    instance_id: 1d8a35b8-e8b5-46e6-859b-c82ace1f9c03\\n    context: pod-network-latency-5kn_litmus\\n    workflow_name: updated_workflow_name\\nspec:\\n  engineState: active\\n  appinfo:\\n    appns: updated_namespace\\n    applabel: app=updated_deployment\\n    appkind: deployment\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-network-latency\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\"60\\"\\n            - name: NETWORK_LATENCY\\n              value: \\"2000\\"\\n            - name: JITTER\\n              value: \\"0\\"\\n            - name: CONTAINER_RUNTIME\\n              value: docker\\n            - name: SOCKET_PATH\\n              value: /var/run/docker.sock\\n            - name: PODS_AFFECTED_PERC\\n              value: \\"50\\"\\n        probe: []\\n  annotationCheck: \\"false\\"\\n"
              }
            }
          ]
        },
        "container": {
          "args": [
            "-file=/tmp/chaosengine-pod-network-latency-5kn.yaml",
            "-saveName=/tmp/engine-name"
          ],
          "image": "405524983081.dkr.ecr.ap-southeast-1.amazonaws.com/aella-xplatform-ecr/facility/litmuschaos/litmus-checker:latest"
        }
      },
      {
        "name": "revert-chaos",
        "container": {
          "image": "405524983081.dkr.ecr.ap-southeast-1.amazonaws.com/aella-xplatform-ecr/facility/litmuschaos/k8s:latest",
          "command": [
            "sh",
            "-c"
          ],
          "args": [
            "kubectl delete chaosengine -l \'instance_id in (1d8a35b8-e8b5-46e6-859b-c82ace1f9c03, )\' -n {{workflow.parameters.adminModeNamespace}} "
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
def execute_network_latency_experiment(namespace, deployment):
    print("running execute_network_latency_experiment")
    response = get_auth_token()
    print("Auth token received ")
    access_token = response.json()['access_token']

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}
    workflow_name = 'network-latency-workflow-' + get_random_number()
    json_data = get_network_latency_experiment_body(workflow_name, namespace, deployment)
    print('got the body ')
    net_latency_response = requests.post(LITMUS_URL + '/api/query',
                                         data=json_data, headers=headers)
    print(net_latency_response.json())
    print(net_latency_response.status_code)


if __name__ == '__main__':
    execute_network_latency_experiment('nginx', 'nginx')
