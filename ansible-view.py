#!/usr/bin/env python3

import os
import sys
import json
import argparse
import subprocess


# Function to list all playbooks in a specified directory
def list_playbooks(playbook_dir):
    playbooks = []
    try:
        for filename in os.listdir(playbook_dir):
            if filename.endswith('.yml') or filename.endswith('.yaml') or filename.endswith('.yml.j2'):
                playbooks.append(filename)
        return playbooks
    except FileNotFoundError:
        return []
        
# Function to list all variables used in all playbooks and templates
def list_all_variables(playbook_path):
    variables = set()
    for dir_path in [playbook_path, os.path.join(playbook_path, 'templates')]:
        if os.path.isdir(dir_path):
            for file_name in os.listdir(dir_path):
                if file_name.endswith('.yml') or file_name.endswith('.yaml') or file_name.endswith('.yml.j2'):
                    file_path = os.path.join(dir_path, file_name)
                    with open(file_path, 'r') as f:
                        for line in f:
                            if '{{' in line:
                                for var in line.split('{{')[1:]:
                                    var = var.split('}}')[0].strip()
                                    variables.add(var)
    for var in sorted(variables):
        print(var)

# Function to list all variables used in a specified playbook/template
def list_playbook_variables(path):
    variables = set()
    with open(path, 'r') as f:
        for line in f:
            if '{{' in line:
                for var in line.split('{{')[1:]:
                    var = var.split('}}')[0].strip()
                    variables.add(var)
    for var in sorted(variables):
        print(var)

# Function returns boolean determining if a specified variable is used in a specified playbook
def search_variable_in_playbook(var_name, playbook_path):
    with open(playbook_path, 'r') as f:
        for line in f:
            if '{{' in line:
                for var in line.split('{{')[1:]:
                    var = var.split('}}')[0].strip()
                    if var == var_name:
                        return True
    return False

# Function to list out all playbooks containing specified variable
def list_playbooks_by_var(var_name):
    playbooks_with_var = []
    for x in all_playbooks:
        if search_variable_in_playbook(var_name, os.path.join(args.path, x)):
            playbooks_with_var.append(x)
    for x in all_templates:
        if search_variable_in_playbook(var_name, os.path.join(args.path, 'templates', x)):
            playbooks_with_var.append(x)
    return playbooks_with_var

# Function to execute the ansible-inventory command and parse the response to collect all hosts
def get_hosts_from_inventory(inventory):
    cmd = ['ansible-inventory', '-i', inventory, '--list']
    result = subprocess.run(cmd, capture_output=True, text=True)
    inventory = json.loads(result.stdout)
    return sorted(inventory['_meta']['hostvars'].keys())

# Function to get all groups that a 'host' is a member of
def get_host_groups(inventory, host):
    cmd = ['ansible-inventory', '-i', inventory, '--list']
    result = subprocess.run(cmd, capture_output=True, text=True)
    inventory = json.loads(result.stdout)
    groups = []
    for group, group_data in inventory.items():
        if 'hosts' in group_data and host in group_data['hosts']:
            groups.append(group)
    return groups

# Function to get all variables, values, and definition levels for a specified host
def get_host_variables(inventory, host_name):
    cmd = ['ansible-inventory', '-i', inventory, '--host', host_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    inventory = json.loads(result.stdout)
    return inventory

# Function to get all groups and their members from the specified inventory
def get_groups_and_members(inventory):
    cmd = ['ansible-inventory', '-i', inventory, '--list']
    result = subprocess.run(cmd, capture_output=True, text=True)
    inventory = json.loads(result.stdout)
    group_members = {}
    for group, group_data in inventory.items():
        if 'hosts' in group_data:
            group_members[group] = group_data['hosts']
        elif 'children' in group_data:
            group_members[group] = group_data['children']
    return group_members

# Function to extract all variable names together with their values from a specified file
def read_vars_from_file(file):
    with open(file, 'r') as f:
        content = f.read()
    lines = content.splitlines()
    variables = {}
    for line in lines:
        if not line.strip().startswith('#') and ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = [value.strip(), file.split('/')[-1]]
            variables[key] = value
    return variables

if __name__ == '__main__':
    # Handling program args
    parser = argparse.ArgumentParser(description='Ansible playbook explorer')
    parser.add_argument('--host', type=str, dest='host',
                        help='Name of the host to get information about')
    parser.add_argument('-p', '--path', type=str, dest='path', default=os.path.dirname(os.path.realpath(__file__)),
                        help='Path to the directory with Ansible playbooks')
    parser.add_argument('-pb', '--playbook', type=str, dest='playbook',
                        help='Name of the playbook to get information about')
    parser.add_argument('-g', '--group', type=str, dest='group',
                        help='Get information about a group')
    parser.add_argument('-v', '--variable', type=str, dest='variable',
                        help='Name of the variable to get information about')
    parser.add_argument('-i', '--inventory', type=str, dest='inventory', default='inventory',
                        help='Path to the inventory file/directory')
    parser.add_argument('--list-all-vars', action='store_true', dest='list_all_vars',
                        help='List all variables from all found playbooks')
    parser.add_argument('--list-all-hosts', action='store_true', dest='list_all_hosts',
                        help='List all hosts found in the inventory')
    parser.add_argument('--list-groups', action='store_true', dest='listgroups',
                        help='Get information about groups')
    

    args = parser.parse_args()
    if not args.path.startswith('/'):
        args.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), args.path)
    
    # Collect all playbooks and templates
    all_playbooks = list_playbooks(args.path)
    all_templates = list_playbooks(os.path.join(args.path, 'templates'))
    # List templates if a 'templates' directory exists in the playbook_dir
    templates_dir = os.path.join(args.path, 'templates')
    
    if args.playbook:
        playbook_path = os.path.join(args.path, args.playbook)
        templates_path = os.path.join(args.path, 'templates' , args.playbook)
        if os.path.isfile(playbook_path):
            print(f'Variables defined in playbook {args.playbook}:')
            list_playbook_variables(playbook_path)
        elif os.path.isfile(templates_path):
            print(f'Variables defined in playbook {args.playbook}:')
            list_playbook_variables(templates_path)
        else:
            print(f'Playbook {args.playbook} not found in {args.path}')
    elif args.host and args.listgroups:
        print(f'Groups used for host {args.host}:')
        groups = get_host_groups(args.inventory, args.host)
        for group in groups:
            print('- {}'.format(group))
    elif args.listgroups: # !!!this must be the last elif having 'args.listgroups' as part of the condition!!!
        group_members = get_groups_and_members(args.inventory)
        for group, members in group_members.items():
            print('Group {} ({}):'.format(group, len(members)))
            for member in members:
                print('- {}'.format(member))
            print()
    elif args.group:
        group_members = get_groups_and_members(args.inventory)
        if args.group in group_members.keys():
                print(f'Group { args.group } members ({ len(group_members[args.group]) }):')
                for member in group_members[args.group]:
                    print(f'- { member }')
                print()
        group_vars = {}
        if  os.path.exists(os.path.join(args.path, 'group_vars', args.group)) and os.path.isfile(os.path.join(args.path, 'group_vars', args.group)):
            group_vars = read_vars_from_file(os.path.join(args.path, 'group_vars', args.group))
        elif os.path.exists(os.path.join(args.path, 'group_vars', args.group) + '.yml') and os.path.isfile(os.path.join(args.path, 'group_vars', args.group) + '.yml'):
            group_vars = read_vars_from_file(os.path.join(args.path, 'group_vars', args.group) + '.yml')
        print(f'Group { args.group } variables:')
        for c in group_vars:
            print(f'- { c } : { group_vars[c][0] }')
        print()
    elif args.host:
        host_groups = get_host_groups(args.inventory, args.host)
        print(f'Host {args.host} is a member of the following groups:')
        for x in host_groups:
            print(f'- { x }')
        print()
        print('Contents of the group vars')
        collected_group_vars = {}
        for y in host_groups:
            if  os.path.exists(os.path.join(args.path, 'group_vars', y)) and os.path.isfile(os.path.join(args.path, 'group_vars', y)):
                collected_group_vars.update(read_vars_from_file(os.path.join(args.path, 'group_vars', y)))
            elif os.path.exists(os.path.join(args.path, 'group_vars', y) + '.yml') and os.path.isfile(os.path.join(args.path, 'group_vars', y) + '.yml'):
                collected_group_vars.update(read_vars_from_file(os.path.join(args.path, 'group_vars', y) + '.yml'))
        for c in collected_group_vars:
            print(f'- { c } : { collected_group_vars[c] }')
        print()
        print('Contents of the host vars')
        collected_host_vars = {}
        if os.path.exists(os.path.join(args.path, 'host_vars', args.host)) and os.path.isfile(os.path.join(args.path, 'host_vars', args.host)):
            collected_host_vars.update(read_vars_from_file(os.path.join(args.path, 'host_vars', args.host)))
        elif os.path.exists(os.path.join(args.path, 'host_vars', args.host) + '.yml') and os.path.isfile(os.path.join(args.path, 'host_vars', args.host) + '.yml'):
            collected_host_vars.update(read_vars_from_file(os.path.join(args.path, 'host_vars', args.host) + '.yml'))
        for c in collected_host_vars:
            print(f'- { c } : { collected_host_vars[c] }')
        print()
        vars = get_host_variables(args.inventory, args.host)
        # iterate through host vars
        for x in collected_host_vars.keys():
            if type(vars[x]) == str:
                if collected_host_vars[x][0].replace('"', '').strip() == vars[x].strip():
                    vars[x] = (vars[x], 'host_var')
                    collected_group_vars.pop(x, None)
            elif type(vars[x]) == int:
                if int(collected_host_vars[x][0]) == vars[x]:
                    vars[x] = (vars[x], 'host_var')
                    collected_group_vars.pop(x, None)
            elif type(vars[x]) == float:
                if float(collected_group_vars[x][0]) == vars[x]:
                    vars[x] = (vars[x], 'host_var')
                    collected_group_vars.pop(x, None)
            elif type(vars[x]) == bool:
                if (collected_host_vars[x][0].upper() == 'TRUE' and vars[x]) or (collected_host_vars[x][0].upper() == 'FALSE' and not vars[x]):
                    vars[x] = (vars[x], 'host_var')
                    collected_group_vars.pop(x, None)
            else:
                print('Unrecognized var type: {} - {}'.format(vars[x], type(vars[x])))
        # iterate through group vars
        for x in collected_group_vars.keys():
            if type(vars[x]) == str:
                if collected_group_vars[x][0].replace('"', '').strip() == vars[x].strip():
                    vars[x] = (vars[x], 'group_var : ' + collected_group_vars[x][1])
            elif type(vars[x]) == int:
                if int(collected_group_vars[x][0]) == vars[x]:
                    vars[x] = (vars[x], 'group_var : ' + collected_group_vars[x][1])
            elif type(vars[x]) == float:
                if float(collected_group_vars[x][0]) == vars[x]:
                    vars[x] = (vars[x], 'group_var : ' + collected_group_vars[x][1])
            elif type(vars[x]) == bool:
                if (collected_group_vars[x][0].upper() == 'TRUE' and vars[x]) or (collected_group_vars[x][0].upper() == 'FALSE' and not vars[x]):
                    vars[x] = (vars[x], 'group_var - ' + collected_group_vars[x][1])
            else:
                print('Unrecognized var type: {} - {}'.format(vars[x], type(vars[x])))
        print(f'Variables used by host {args.host}:')
        for v in vars:
            print(f'- { v } - { vars[v][0] } ({ vars[v][1] })')
        print()
    elif args.variable:
        playbooks_with_var = list_playbooks_by_var(args.variable)
        print(f'Playbooks that use variable {args.variable}:')
        for playbook in playbooks_with_var:
            print(playbook)
        print()
    elif args.list_all_vars:
        print(f'Listing variables used in playbooks in {args.path} and {args.path}/templates:')
        list_all_variables(args.path)
    elif args.list_all_hosts:
        print(f'Listing hosts found in the inventory: { args.path }/{ args.inventory }')
        hosts = get_hosts_from_inventory(os.path.join(args.path, args.inventory))
        for host in hosts:
            print(f'- { host }')
    else:
        # List playbooks from the templates directory
        if os.path.isdir(templates_dir):
            if all_templates:
                print(f'Available templates in {templates_dir}:', end='\n' + '-' * 50 + '\n')
                for t in all_templates:
                    print(t)
                print()
        else:
            print(f'No templates directory found in {args.path}', end='\n' + '-' * 50 + '\n')

        # List playbooks from the playbook_dir (or the current directory if no argument was provided)
        if all_playbooks:
            print(f'Available playbooks in {args.path}:', end='\n' + '-' * 50 + '\n')
            for p in all_playbooks:
                print(p)
            print()
        else:
            print(f'No playbooks found in {args.path}', end='\n' + '-' * 50 + '\n')

