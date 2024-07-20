#!/bin/bash

# Function to create directory and verify
create_dir() {
    mkdir -p "$1"
    if [ ! -d "$1" ]; then
        echo "Failed to create directory $1"
        exit 1
    fi
}

# Function to create role structure
create_role() {
    local role_name=$1
    for subdir in defaults vars tasks handlers templates files meta; do
        create_dir "$PROJECT_NAME/roles/$role_name/$subdir"
        touch "$PROJECT_NAME/roles/$role_name/$subdir/main.yml"
    done
    # Create empty placeholder files for templates and files directories
    touch "$PROJECT_NAME/roles/$role_name/templates/.gitkeep"
    touch "$PROJECT_NAME/roles/$role_name/files/.gitkeep"
}

# Check if at least project name was provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <ansible_project_name> [role_name...]"
    exit 1
fi

# Define the project name
PROJECT_NAME=$1
shift

# Create the directory structure
create_dir "$PROJECT_NAME/inventory/group_vars"
create_dir "$PROJECT_NAME/roles"
create_dir "$PROJECT_NAME/playbooks"
create_dir "$PROJECT_NAME/vault"

# Create roles
if [ "$#" -eq 0 ]; then
    # Create default role 'role1' if no roles are provided
    create_role "role1"
else
    # Create roles as provided in the arguments
    for role in "$@"; do
        create_role "$role"
    done
fi

# Create the ansible.cfg file
cat << EOF > "$PROJECT_NAME/ansible.cfg"
[defaults]
inventory = ./inventory/hosts
remote_user = ansible
host_key_checking = False
retry_files_enabled = False
roles_path = ./roles

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
EOF

echo "Ansible project '$PROJECT_NAME' structure created successfully with roles: $@"