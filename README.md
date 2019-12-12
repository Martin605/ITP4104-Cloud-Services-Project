#  ITP4104 Cloud Services Project
180105912-180081307-180424032-180509181
## Rewrite CloudFormation
https://github.com/wongcyrus/AWS-Developer-Building-on-AWS
## Rewritten Exercise
* `IAMStack      :Exercise5`      `first deploy`
* `VPCStack      :Exercise3`      `first deploy`
* `ParametersStack:Exercise9`      `first deploy`
* `CognitoStack  :Exercise9`      `first deploy`
* `SecurityStack :Exercise11`     `second deploy`
* `Cloud9Stack   :Exercise9`      `second deploy`
* `CDNStack      :Exercise9`      `thrid deploy`
* `DBStack       :Exercise11`     `thrid deploy`
* `WebStack      :Exercise10`     `final deploy`
* `SNSSQSStack   :Exercise12`     `final deploy`

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
