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

DOCUMENTATION = r'''
---
module: commvault.ansible.database.backup
short_description: To perform a backup of a database subclient
description:
    - commvault.ansible.database.backup can be used to perform database backup operation.

options:
  webserver_hostname:
    description:
      - Hostname of the Web server.
    type: str
    required: false
  commcell_username:
    description:
      - Commcell username
    type: str
    required: false
  commcell_password:
    description:
      - Commacell password
    type: str
    required: false
  client:
    description:
      - The name of the Client.
    type: str
    required: true
  instance:
    description:
      - The name of the Instance
    type: str
    required: true
  agent_type:
    description:
      - The agent type.
    type: str
    required: true
    default: None
    choices: ["sql server","oracle","mysql", "postgresql"]
  backupset:
    description:
      - The name of the backupset.
    type: str
    required: false
    default: default backupset.
  subclient:
    description:
      - The name of the subclient.
    type: str
    required: false
    default: subclient name default.
  backup_level:
    description:
      - backup level.
    type: str
    required: false
    default: Full
    choices: ["Full","Incremental","Differential","Synthetic_full"]
 
'''

EXMPLES = '''
- name: Run a Database Backup for a default subclient of a default backupset, session file will be used.
  commvault.ansible.database.backup:
    client: "client_name"
    instance: "instance_name"
    agent_type: "mysql

- name: Run a Database Backup for subclient 'user_subclient' of backupset 'user_backupset', session file will be used.
  commvault.ansible.database.backup:
    client: "client_name"
    instance: "instance_name"
    backupset: "user_backupset"
    subclient: "user_subclient"
    agent_type: "mysql

- name: Run a Database Backup for default subclient of default backupset.
  commvault.ansible.database.backup:
    webserver_hostname: "webserver_hostname"
    commcell_username: "user"
    commcell_password: "password"
    client: "client_name"
    instance: "instance_name"
    agent_type: "mysql

- name: Run a Database Backup for subclient 'user_subclient' of backupse ' user_backupset'.
  commvault.ansible.database.backup:
    webserver_hostname: "webserver_hostname"
    commcell_username: "user"
    commcell_password: "password"
    client: "client_name"
    instance: "instance_name"
    backupset: "user_backupset"
    subclient: "user_subclient"
    agent_type: "mysql

- name: run a Database Backup for subclient 'user_subclient' of backupset 'user_backupset' with agent_type of 'mysql'.
  commvault.ansible.database.backup:
    webserver_hostname: "webserver_hostname"
    commecell_username: "user"
    commcell_password: "password"
    client: "client_name"
    instance: "instance_name"
    backupset: "user_backupset"
    subclient: "user_subclient"
    agent_type: "mysql"

'''

RETURN = r'''
job_id:
    description: Backupjob ID
    returned: On succusses
    type: str
    sample: '2025'
'''

from ansible_collections.commvault.ansible.plugins.module_utils.cv_ansible_module import CVAnsibleModule

def main ():
    """Main method for this module."""

    module_args = dict(
        client=dict(type=str, required=True),
        backupset=dict(type=str, required=False),
        subclient=dict(type=str, required=False),
        backup_level=dict(type=str, required=False),
        agent_type=dict(type=str, required=True),
        instance = dict(type=str, required=True)
    )

    module = CVAnsibleModule(argument_spec=module_args)
    module.result['changed'] = False

    try:
        client = module.commcell.clients.get(module.params.get('client'))
        agent_type = module.params.get('agent_type', '')
        agent = client.agents.get(agent_type)
        instance = agent.instances.get(module.params.get('instance'))
        backupset = instance.backupsets.get(agent.backupsets.default_backup_set if not module.params.get('backupset') else module.params.get('backupset'))
        subclient = backupset.subclients.get(backupset.subclients.default_subclient if not module.params.get('subclient') else module.params.get('subclient'))
        backup_level = module.params.get('backup_level', 'Full')
        backup = subclient.backup(backup_level= backup_level)
        module.result['job_id'] = str(backup.job_id)
        module.result['changed'] = True
        module.result['status'] = str(backup.status)
        module.exit_json(**module.result)

    except Exception as e:
        module.result['msg'] = str(e)
        module.fail_json(**module.result)


if __name__ == "__main__":
    main()
