# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Commvault Ansible Collection (`commvault.ansible`) — an official Ansible collection providing modules and roles to automate Commvault data protection operations via CVPySDK.

**Requirements**: Ansible >= 2.10.0, Python 3.6+, CVPySDK >= 11.36, Commvault v11 SP16+ with WebConsole.

## Build & Install

```bash
# Install Python dependency
pip install -r requirements.txt

# Install collection from Galaxy
ansible-galaxy collection install commvault.ansible

# Install collection dependencies
ansible-galaxy collection install -r requirements.yml

# Build collection artifact locally
ansible-galaxy collection build
```

There is no test suite, linter configuration, or CI pipeline in this repository. Role-level test playbooks exist at `roles/*/tests/test.yml` but require a live Commvault environment.

## Git Conventions

- Follow [Conventional Commits](https://www.conventionalcommits.org) for commit messages:
  - Format: `<type>[optional scope]: <description>`
  - Types: `feat` (new feature), `fix` (bug fix), `docs`, `style`, `refactor`, `perf`, `test`, `build`, `chore`, `ci`
  - Use `!` before colon or `BREAKING CHANGE:` footer for breaking changes (e.g., `feat!: remove legacy API`)
  - Optional body and footers separated by blank lines
- Do not include "Co-Authored-By" lines in commit messages.

## Coding Standards

- PEP8 compliant, formatted with **autopep8** at **line-length 119** (not the default 79)
- Docstrings required on all methods/classes, matching existing format
- Consistent with CVPySDK design patterns

## Architecture

### Core: CVAnsibleModule (`plugins/module_utils/cv_ansible_module.py`)

Base class extending `AnsibleModule` that all modules inherit. Handles:
- Automatic CVPySDK login from credentials, auth tokens, or persisted session files
- Session persistence via serialization to `/tmp/CVANSIBLE_{uid}`
- Credential validation (mutual exclusivity of auth methods)
- Required `changed` field enforcement on `exit_json()`

The `override=True` parameter bypasses automatic login (used by the `login` module itself).

### Session Management (`plugins/module_utils/login/pre_login.py`)

Sessions are serialized Commcell objects stored per-user in `/tmp`. The `login` module writes the session file; subsequent modules read it. The `logout` module destroys it.

### Module Organization (`plugins/modules/`)

Modules are namespaced by domain using subdirectories:
- `login`, `logout` — authentication lifecycle
- `request` — raw HTTP API wrapper (GET/POST/PUT/DELETE)
- `ansiblev1` — SDK entity operations (backward-compat interface)
- `database/` — backup and restore for SQL Server, Oracle, MySQL, PostgreSQL
- `file_servers/` — file system backup, restore, content management, plan assignment
- `job/` — kill, resume, status, suspend, wait_for_task_completion
- `plans/` — add and delete backup plans
- `storage/disk/` — add storage pools, query details
- `deployment/` — install_software, download_software, push_updates
- `workflow/` — deploy, execute, export, import

Modules are referenced as `commvault.ansible.{path}` (e.g., `commvault.ansible.database.backup`).

### Module Template

Every module follows this structure:
```python
DOCUMENTATION = r'''...'''
EXAMPLES = r'''...'''
RETURN = r'''...'''

def main():
    module = CVAnsibleModule(argument_spec={...})
    # Use module.commcell to access CVPySDK
    module.result['changed'] = True
    module.exit_json(**module.result)

if __name__ == "__main__":
    main()
```

### Roles (`roles/`)

Roles compose modules into workflows (login → operation → logout):
- `database` — database backup/restore orchestration (requires SP26+)
- `fs_deployment` — file system deployment
- `oracle_db_deployment` — Oracle-specific server registration and configuration

### Action Groups (`meta/runtime.yml`)

All modules belong to the `session` action group, signaling shared authentication state across playbook tasks.
