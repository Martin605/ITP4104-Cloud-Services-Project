#!/bin/bash

echo -e "\033[36mCDK destroy CdnStack DBStack  \033[0m"
cdk destroy CdnStack DBStack  
echo -e "\033[36mCDK destroy SecurityStack Cloud9Stack \033[0m"
cdk destroy SecurityStack Cloud9Stack 
echo -e "\033[36mCDK destroy VpcStack IAMStack ParametesStack CognitoStack\033[0m"
cdk destroy VpcStack IAMStack ParametersStack CognitoStack
echo -e "\033[35mEND\033[0m"
