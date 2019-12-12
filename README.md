#  ITP4104 Cloud Services Project
180105912-180081307-180424032-180509181
## Rewrite CloudFormation
https://github.com/wongcyrus/AWS-Developer-Building-on-AWS
## Rewritten Exercise
* `IAMStack      :Exercise5`      `first deploy`    `finished`
* `VPCStack      :Exercise3`      `first deploy`    `finished`
* `ParametersStack:Exercise9`      `first deploy`   `finished`
* `CognitoStack  :Exercise9`      `first deploy`    `finished`
* `SecurityStack :Exercise11`     `second deploy`   `finished`
* `Cloud9Stack   :Exercise9`      `second deploy`   `finished`
* `CDNStack      :Exercise9`      `thrid deploy`    `finished`
* `DBStack       :Exercise11`     `thrid deploy`    `finished`
* `WebStack      :Exercise10`     `final deploy`    `error in 7/10`
* `SNSSQSStack   :Exercise12`     `final deploy`    `error in 2/5`

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
