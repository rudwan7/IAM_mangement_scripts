'''
Generate a CSV report on all IAM credentials on all projects
The goal is to cleanup the mess of existing IAM policies
And then review the report periodically to check that everything is still OK

Usage:
    python3 iamReport.py > iamReport.csv
    open the CSV to review the IAM policies
    Requires gcloud to be installed and configured

Takes a minute to run, as it needs to query the IAM policies for each resource.

Code Status: Working & complete
    This is intended to be run manually
    with the user examining the output.
    No further automation is required.

Code Design:
    Appends the IAM policies to the resource records defined in project_tree
    See project_tree.py for the data structure examples
'''

import project_tree
from pprint import pprint

def iam_policies_append(resource_rec):
    # Add the IAM policies to the record
    if resource_rec['type'] == 'organizations':
        cmd = f'gcloud organizations get-iam-policy {resource_rec["id_num"]} --format json'
    elif resource_rec['type'] == 'folders':
        cmd = f'gcloud resource-manager folders get-iam-policy {resource_rec["id_num"]} --format json'
    elif resource_rec['type'] == 'projects':
        cmd = f'gcloud projects get-iam-policy {resource_rec["id_num"]} --format json'
    else:
        raise ValueError(f"Unknown resource type: {resource_rec['type']}")
    iam_bindings = project_tree.return_json_results(cmd)
    if 'bindings' in iam_bindings:
        resource_rec['iam_bindingsL'] = iam_bindings['bindings']
    else:
        resource_rec['iam_bindingsL'] = []

def print_iam_policies_csv(all_recs):
    for r in all_recs:
        iam_policies_print_csv_rows(r)
    pass

def iam_policies_print_csv_rows(resource_rec):
    if resource_rec['iam_bindingsL'] == []:
        print(f"{resource_rec['type']},FAKE_ID,{resource_rec['name']},No IAM bindings")
    else:
        for rec in resource_rec['iam_bindingsL']:
            for member in rec['members']:
                print(f"{resource_rec['type']},FAKE_ID,{resource_rec['name']},{rec['role']},{member}")

def main():
    all_recs = project_tree.all_recs_get()
    for k, r in all_recs.items():
        iam_policies_append(r)
        iam_policies_print_csv_rows(r)

if __name__ == '__main__':
    main()
