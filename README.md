# ARNChecker
This script helps identify invalid or non-existent ARNs that are still present in your AWS account, ensuring that outdated ARNs, which could potentially pose security risks, are flagged for review or removal. Many ARNs are given permissions and they might have been deleted after sometime but the permissions given to that ARN would still be there leading to chance of exploitation is someone creates any workload or resource with the same name(ARN).

Scope:
1. Looks for all the ARNs in the IAM Roles Trust Permissions
2. Looks for all the ARNs present in Resource based policies. (Currently only S3 policies are covered, other resources will be added in the future)
3. Validates if the ARN exists or not in that AWS account or any AWS Account. Few ARNs of cross account might be added in few policies, even those ARNs will be checked if they are existing or not

How the Script Works:
As there isn't any API provided by AWS to check if any ARN exists or not, the script leveraged to create an IAM roles with invalid ARN in trust policy which will lead to an error while role creation as the ARN does not exist. The Output is listed at all last with all the ARNs that have caused the Invalid ARN exception.

Steps:
1. Configure AWS CLI and add all those accounts on CLI.
2. Add those profile names in the python script so that script can directly use the AWS keys from the profile name
