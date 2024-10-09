import boto3
import json
import time
from botocore.exceptions import ClientError

# List of AWS CLI profiles to iterate over
profiles = ['Prod', 'Pre-Prod']  # Replace with your profiles

# Function to initialize a session with a specific profile
def initialize_session(profile_name):
    session = boto3.Session(profile_name=profile_name)
    iam_client = session.client('iam')
    s3_client = session.client('s3')
    return iam_client, s3_client

# Extract ARNs from S3 bucket policies
def get_s3_arns(s3_client):
    buckets = s3_client.list_buckets()['Buckets']
    arns = []
    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket_name)['Policy']
            policy_json = json.loads(policy)
            for statement in policy_json.get('Statement', []):
                if 'Principal' in statement and 'AWS' in statement['Principal']:
                    arn = statement['Principal']['AWS']
                    if isinstance(arn, list):
                        arns.extend(arn)
                    else:
                        arns.append(arn)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucketPolicy':
                print(f"No bucket policy exists for {bucket_name}, skipping.")
            else:
                print(f"Error getting bucket policy for {bucket_name}: {e}")
    return arns

# Extract ARNs from IAM role trust policies
def get_iam_trust_arns(iam_client):
    roles = iam_client.list_roles()['Roles']
    arns = []
    for role in roles:
        role_name = role['RoleName']
        trust_policy = iam_client.get_role(RoleName=role_name)['Role']['AssumeRolePolicyDocument']
        for statement in trust_policy.get('Statement', []):
            if 'Principal' in statement and 'AWS' in statement['Principal']:
                arn = statement['Principal']['AWS']
                if isinstance(arn, list):
                    arns.extend(arn)
                else:
                    arns.append(arn)
    return arns

# Create a demo role with trust relationships based on ARNs
def create_demo_role(iam_client, arns):
    non_exist_arn = []
    role_name = "DemoARNCheckRole"
    
    # Trust policy template
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
                "Effect": "Allow",
                "Principal": {"AWS": []},
                "Action": "sts:AssumeRole"
            }]
    }

    # Prepare the trust policy by adding valid ARNs
    for arn in arns:
        if arn.startswith("arn:aws:"):
            trust_policy["Statement"][0]["Principal"]["AWS"] = arn
        role_created = False  # Flag to track if the role was created
        try:
            # Check if the role already exists
            iam_client.get_role(RoleName=role_name)
            print(f"Role '{role_name}' already exists. Skipping creation.")
            print("trust_policy: ", trust_policy)
            try:
                iam_client.update_assume_role_policy(
                RoleName=role_name,
                PolicyDocument=json.dumps(trust_policy)
            )
                role_created = True
            except ClientError as e:
                if e.response['Error']['Code'] == 'MalformedPolicyDocument':
                    print(f"Error updating role: Malformed policy document. Invalid principal in the policy.")
                    non_exist_arn.append(arn)
                else:
                    print(f"Error updating role trust policy: {e}")
        except iam_client.exceptions.NoSuchEntityException:
            # If role doesn't exist, create it
            try:
                iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description="Demo role for ARN existence check."
                )
                print(f"Created role '{role_name}' with the given ARNs in the trust relationship.")
                role_created = True
            except ClientError as e:
                if e.response['Error']['Code'] == 'MalformedPolicyDocument':
                    print(f"Error creating role: Malformed policy document. Invalid principal in the policy.")
                    non_exist_arn.append(arn)
                else:
                    print(f"Error creating role: {e}")
    if role_created:
        try:
            iam_client.delete_role(RoleName=role_name)
            print(f"Deleted role '{role_name}' as part of cleanup.")
        except ClientError as e:
            print(f"Error deleting role '{role_name}': {e}")
    return non_exist_arn

# Main function to check ARN existence using demo role
def check_arn_existence_for_profile(profile_name):
    print(f"\nChecking ARNs for profile: {profile_name}")
    
    iam_client, s3_client = initialize_session(profile_name)

    # Get ARNs from S3 bucket policies
    s3_arns = get_s3_arns(s3_client)

    # Get ARNs from IAM trust policies
    iam_arns = get_iam_trust_arns(iam_client)
    
    # Combine all ARNs from S3 and IAM trust policies
    all_arns = set(s3_arns + iam_arns)  


    if all_arns:
        # Use the ARNs in the trust relationship of a demo role
        clean_arn = create_demo_role(iam_client, list(all_arns))
    else:
        print("No ARNs found for this profile.")
    print("------------------------------------------------")
    print("------------------------------------------------")
    print("------------------------------------------------")
    print("non_exist_arn: ", clean_arn)

# Loop through each profile and check ARNs
for profile in profiles:
    check_arn_existence_for_profile(profile)
