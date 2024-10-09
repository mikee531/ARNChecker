# ARNChecker
This script helps someone to check all the ARNs that exist in your AWS account. Many ARNs are given permissions and they might have been deleted after sometime but the permissions given to that ARN would still be there leading to chance of exploitation.

1. Configure AWS CLI and add all those accounts on CLI.
2. Add those profile names in the python script so that script can directly use the AWS keys from the profile name
