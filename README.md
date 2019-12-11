# ITP4104 Project
## Rewrite CloudFormation
https://github.com/wongcyrus/AWS-Developer-Building-on-AWS
## Rewritten Exercise
* `IAMStack      :Exercise5`
* `VPCStack      :Exercise3`
* `SecurityStack :Exercise11`
* `DBStack       :Exercise11`
* `WebStack      :Exercise10`
* `CDNStack      :Exercise9`
* `ParametesStack:Exercise9`
* `Cloud9Stack   :Exercise9`
* `CognitoStack  :Exercise9`
* `SNSSQSStack   :Exercise12`

### Welcome to CDK Python project!

**Linux/Mac platform**

```
$ python -m venv .env
$ source .env/bin/activate
```

**Windows platform**

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
$ cdk synth
```

# CDK Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk destroy`     destroy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
