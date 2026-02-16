# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------


DOCUMENTATION = '''
module: commvault.ansible.ansiblev1
short_description: Runs Python SDK functions using the generated entities similar to ansible v1
description: 
    - Runs Python SDK functions using the generated entities similar to ansible v1

options:
    webserver_hostname:
        description:
            - Hostname of the Web Server. 
        type: str
        required: false

    commcell_username:
        description:
            - Username 
        type: str
        required: false    

    commcell_password:
        description:
            - Password 
        type: str
        required: false

    operation:
        description:
            - Name of the target entity's method to be run
        type: str
        required: true

    arguments:
        description:
            - Arguments to be passed to target entity's method to be run
        type: str
        required: true

    entity_type:
        description:
            - Name of the target entity
        type: str
        required: true
        choices: ["Clients", "Client", "Clientgroups", "Clientgroup", "Agents", "Agent", "Instances", "Instance", "Backupsets", "Backupset", "Subclients", "Subclient", "Job", "MediaAgents", "MediaAgent", "StoragePools", "StoragePool", "DiskLibraries", "DiskLibrary"]

    entity_filters:
        description:
            - 'Dictionary consisting of filters to select particular entities. Available filters: "client", "clientgroup", "agent", "instance", "backupset", "subclient", "job_id", "media_agent", "storage_pool", "disk_library"'
        type: dict
        required: False
        default: None
    
'''

EXAMPLES = '''
- name: "GET_CLIENT_ID"
  commvault.ansible.ansiblev1:
    operation: "client_id"
    entity_type: client
    entity_filter: {
      "client": "client_name"
    }
  register: output

- name: "GET_JOB_DETAILS"
  commvault.ansible.ansibleV1:
    operation: "_get_job_details"
    entity_type: job
    entity: {
    "job_id": 746908
    }
  register: output

- name: "CHECK_IF_CLIENT_EXISTS"
  commvault.ansible.request:
    webserver_hostname: "demo-CS-Name"
    commcell_username: "user"
    commcell_password: "CS-Password"
    operation: "has_client"
    entity_type: clients
    arguments: {
      "client_name": "clientXX"
    }
  register: response

'''

RETURN = r'''
response:
    description: Response from the SDK function
    returned: success
    type: dict 
    sample:
      errorCode: 0
      errorMessage: ""

'''
import traceback
from ansible_collections.commvault.ansible.plugins.module_utils.cv_ansible_module import CVAnsibleModule
try:
    from cvpysdk.job import Job
except ModuleNotFoundError:
    pass

def main():

    try:
        module_args =  dict(
            operation=dict(type=str, required=True),
            arguments=dict(type=dict, required=False, default=None),
            entity_type=dict(type=str, required=True),
            entity_filter=dict(type=dict, required=False, default=None),
        )

        module = CVAnsibleModule(argument_spec=module_args)
        
        entity_type = module.params['entity_type']
        entity_filter =  module.params['entity_filter'] if module.params['entity_filter'] else {}

        ENTITY_TYPES = ["clients", "client", "clientgroups", "clientgroup", "agents", "agent", "instances", "instance", "backupsets", "backupset", "subclients", "subclient", "job", "mediaagents", "mediaagent", "storagepools", "storagepool", "disklibraries", "disklibrary"]

        if entity_type.lower() not in ENTITY_TYPES:
            raise Exception("Please provide an appropriate Entity Type")

        clients = module.commcell.clients
        clientgroups = module.commcell.client_groups
        jobs = module.commcell.job_controller
        mediaagents = module.commcell.media_agents
        storagepools = module.commcell.storage_pools
        disklibraries = module.commcell.disk_libraries

        if 'client' in entity_filter:
            client = clients.get(entity_filter['client'])
            agents = client.agents

            if 'agent' in entity_filter:
                agent = agents.get(entity_filter['agent'])
                instances = agent.instances
                backupsets = agent.backupsets

                if 'instance' in entity_filter:
                    instance = instances.get(entity_filter['instance'])
                    subclients = instance.subclients

                if 'backupset' in entity_filter:
                    backupset = backupsets.get(entity_filter['backupset'])
                    subclients = backupset.subclients

                if subclients and 'subclient' in entity_filter:
                    subclient = subclients.get(entity_filter['subclient'])

        if 'job_id' in entity_filter:
            job = jobs.get(entity_filter['job_id'])
        
        if 'clientgroup' in entity_filter:
            clientgroup = clientgroups.get(entity_filter['clientgroup'])

        if 'media_agent' in entity_filter:
            mediaagent = mediaagents.get(entity_filter['media_agent'])

        if 'storage_pool' in entity_filter:
            storagepool = storagepools.get(entity_filter['storage_pool'])

        if 'disk_library' in entity_filter:
            disklibrary = disklibraries.get(entity_filter['disk_library'])

        obj_name = module.params["entity_type"]
        obj = eval(obj_name)
        method = module.params["operation"]

        if not hasattr(obj, method):
            obj_name = '{}s'.format(module.params["entity_type"])
            obj = eval(obj_name)

        statement = '{0}.{1}'.format(obj_name, method)
        attr = getattr(obj, method)

        if callable(attr):
            if module.params.get('arguments'):
                args = module.params["arguments"]
                statement = '{0}(**{1})'.format(statement, args)
            else:
                statement = '{0}()'.format(statement)
            output = eval(statement)
            if type(output).__module__ in ['builtins', '__builtin__']:
                module.result['response'] = output
            elif isinstance(output, Job):
                module.result['response'] = output.job_id
            else:
                module.result['response'] = str(output)

        else:
            if module.params.get('arguments'):
                statement = '{0} = list(module.params["arguments"].values())[0]'.format(statement)
                exec(statement)
                module.result['response'] = "Property set successfully"
            else:
                module.result['response'] = str(eval(statement))

        module.result['failed'] = False
        module.result['changed'] = False
        module.exit_json(**module.result)

    except Exception as exp:
        module.result['failed'] = True
        module.fail_json(msg=str(exp), changed=False, tb=traceback.format_exc())


if __name__ == "__main__":
    main()