# ITP4104 Project
## Rewrite CloudFormation
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
