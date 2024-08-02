import subprocess
import json
import csv
from tabulate import tabulate

# Define a function to run a gcloud command and parse the JSON output
def run_gcloud_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON: {e}")

# Function to get IAM policy for a resource
def get_iam_policy(resource_type, resource_id):
    if resource_type == "organizations":
        command = f"gcloud organizations get-iam-policy {resource_id} --format=json"
    elif resource_type == "folders":
        command = f"gcloud resource-manager folders get-iam-policy {resource_id} --format=json"
    elif resource_type == "projects":
        command = f"gcloud projects get-iam-policy {resource_id} --format=json"
    else:
        raise ValueError(f"Unknown resource type: {resource_type}")
    
    return run_gcloud_command(command)

# Function to extract permissions for a specific member
def extract_permissions(policy):
    permissions = []
    for binding in policy.get("bindings", []):
        role = binding.get("role")
        members = ", ".join(binding.get("members", []))
        permissions.append((role, members))
    return permissions

# Function to get and save permissions for all resources to a CSV file
def save_permissions_to_csv(organization_id, folder_ids, project_ids, output_file):
    all_permissions = []

    # Get organization permissions
    org_policy = get_iam_policy("organizations", organization_id)
    org_permissions = extract_permissions(org_policy)
    for role, members in org_permissions:
        all_permissions.append(["Organization", organization_id, role, members])

    # Get folder permissions
    for folder_id in folder_ids:
        folder_policy = get_iam_policy("folders", folder_id)
        folder_permissions = extract_permissions(folder_policy)
        for role, members in folder_permissions:
            all_permissions.append(["Folder", folder_id, role, members])

    # Get project permissions
    for project_id in project_ids:
        project_policy = get_iam_policy("projects", project_id)
        project_permissions = extract_permissions(project_policy)
        for role, members in project_permissions:
            all_permissions.append(["Project", project_id, role, members])

    # Write the results to a CSV file
    headers = ["Resource Type", "Resource ID", "Role", "Members"]
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(all_permissions)

# Organization ID
ORGANIZATION_ID = "FAKE_ORGANIZATION_ID"

# Folder IDs
FOLDER_IDS = ["FAKE_FOLDER_ID_1", "FAKE_FOLDER_ID_2", "FAKE_FOLDER_ID_3", "FAKE_FOLDER_ID_4", "FAKE_FOLDER_ID_5",
              "FAKE_FOLDER_ID_6", "FAKE_FOLDER_ID_7", "FAKE_FOLDER_ID_8", "FAKE_FOLDER_ID_9", "FAKE_FOLDER_ID_10"]

# Project IDs
PROJECT_IDS = ["FAKE_PROJECT_ID_1", "FAKE_PROJECT_ID_2", "FAKE_PROJECT_ID_3", "FAKE_PROJECT_ID_4", 
               "FAKE_PROJECT_ID_5", "FAKE_PROJECT_ID_6", "FAKE_PROJECT_ID_7", "FAKE_PROJECT_ID_8", "FAKE_PROJECT_ID_9"]

# Output CSV file path
OUTPUT_FILE = "permissions_report.csv"

# Save permissions to CSV
save_permissions_to_csv(ORGANIZATION_ID, FOLDER_IDS, PROJECT_IDS, OUTPUT_FILE)
