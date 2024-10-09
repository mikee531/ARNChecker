# ARNChecker
This script helps someone to check the ARNs that exist in your AWS account. Many ARNs are given permissions and they might have been deleted after sometime but the permissions given to that ARN would still be there leading to chance of exploitation. 

Scope:
1. Looks for all the ARNs in the IAM Roles Trust Permissions
2. Looks for all the ARNs present in Resource based policies. (Currently only S3 policies are covered, other resources will be added in the future)

Steps:
1. Configure AWS CLI and add all those accounts on CLI.
2. Add those profile names in the python script so that script can directly use the AWS keys from the profile name
