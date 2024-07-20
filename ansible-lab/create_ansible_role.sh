#!/bin/bash

# Check if correct number of arguments was provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <ansible_project_name> <role_name>"
    exit 1
fi

# Define project and role names
PROJECT_NAME=$1
ROLE_NAME=$2

# Check if the project directory exists
if [ ! -d "$PROJECT_NAME" ]; then
    echo "Project directory '$PROJECT_NAME' does not exist."
    exit 1
fi

# Create the role directory and subdirectories
ROLE_DIR="$PROJECT_NAME/roles/$ROLE_NAME"
mkdir -p "$ROLE_DIR"/{defaults,vars,tasks,handlers,templates,files,meta}

# Create placeholder files for the role
touch "$ROLE_DIR"/{tasks,handlers,defaults,vars,meta}/main.yml
touch "$ROLE_DIR"/templates/.gitkeep
touch "$ROLE_DIR"/files/.gitkeep

echo "Ansible role '$ROLE_NAME' created successfully in project '$PROJECT_NAME'."

