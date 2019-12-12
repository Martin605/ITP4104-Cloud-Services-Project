#!/bin/bash

echo -e "\033[36mCDK destory VpcStack\033[0m"
cdk destory CDNStack  DBStack  
echo -e "\033[36mCDK destory VpcStack\033[0m"
cdk destory SecurityStack Cloud9Stack 
echo -e "\033[36mCDK destory VpcStack IAMStack ParametesStack CognitoStack\033[0m"
cdk destory VpcStack IAMStack ParametersStack CognitoStack
echo -e "\033[35mEND\033[0m"
