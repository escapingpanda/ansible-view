# Ansible View

Ansible View is a simple Python-script, that allows for a better view over Ansible resources.

## Main Functions

1. **List all available playbooks:** Unless specified, the script searches for playbooks inside its own working directory (the "templates" folder inside the specified directory will be searched for additional playbook templates).

    **Usage:**
    ```
    python3 ansible-view.py                        # Search in the current directory and workdir/templates

    python3 ansible-view.py --path /path/to/dir    # Search in the specified directory and /path/to/dir/templates

    python3 ansible-view.py -p /path/to/dir        # Same as previous example
    
    python3 ansible-view.py -p path/to/dir         # Concatenation search in workdir + /path/to/dir and workdir + /path/to/dir/templates
    ```

2. **List variables used in any playbook:**

    **Usage:**
    ```
    python3 ansible-view.py --list-all-vars                       # Search in the current directory and workdir/templates

    python3 ansible-view.py --path /path/to/dir --list-all-vars   # Search in the specified directory (/templates)

    python3 ansible-view.py -p path/to/dir --list-all-vars        # Concatenation search in workdir + /path/to/dir (/templates)
    ```

3. **List all variables used in a specific playbook:**

    **Usage:**
    ```
    python3 ansible-view.py -pb testbook.yml                      # Get variables from workdir/(templates/) + testbook.yml

    python3 ansible-view.py -p test/dir -pb testbook.yml          # Get variables from workdir + /test/dir/(templates/) + testbook.yml
    ```

4. **List all playbooks in which a particular variable is used:**

    **Usage:**
    ```
    python3 ansible-view.py -v var_name                         # Search variable in playbooks in workdir/(templates/)

    python3 ansible-view.py -p test/dir -v var_name             # Search variable in playbooks in workdir + /test/dir/(templates/)
    ```

5. **List all hosts:**

    **Usage:**
    ```
    python3 ansible-view.py --list-all-hosts                    # Get all hosts, use inventory= workdir + /inventory

    python3 ansible-view.py -i production --list-all-hosts      # Get all hosts, use inventory= workdir + /production
    ```

6. **List all groups a host is a member of:**

    **Usage:**
    ```
    python3 ansible-view.py --host testHost1 --list-groups                                           # Get all groups a host (testHost1) is a member of, use inventory=workdir + /inventory and default path

    python3 ansible-view.py -i testing --host testHost1 --list-groups                                # Get all groups a host (testHost1) is a member of, use inventory=workdir + /testing and default path

    python3 ansible-view.py -p testing -i production --host testHost1 --list-groups                  # Get all groups a host (testHost1) is a member of, use path=workdir + /testing inventory=workdir + /production
    ```

7. **List all groups and their members:**

    **Usage:**
    ```
    python3 ansible-view.py --list-groups                                # Get all groups and their members, use inventory= workdir + /inventory

    python3 ansible-view.py -i testing/testinventory --list-groups       # Get all groups and their members, use inventory= workdir + /testing/testinventory
    ```

8. **List all used variables for a particular host together with the level at which they are defined (host var, group var)**

    **Usage:**
    ```
    python3 ansible-view.py --host testHost1                            # Get all variables, use default workdir and inventory

    python3 ansible-view.py -p testing -i testing/inventory --host testHost1     # Get all variables, workdir=workdir + /testing inventory=workdir + /testing/inventory
    ```

9. **Get information about a specified group (members, variables)**
    
    **Usage:**
    ```
    python3 ansible-view.py -g groupName                                     # Get information about a specified group
    
    python3 ansible-view.py --group groupName                                # Get information about a specified group

    python3 ansible-view.py -p testing -i testing/inventory -g groupName     # Get information about a specified group, workdir=workdir + /testing/groups_vars/groupName inventory=workdir + /testing/inventory
    ```


***TODO***

**List unique variables (occurring in single or few cases)**

**Automated creation of the alias 'ansible-view'**

**List all IP Addresses**
