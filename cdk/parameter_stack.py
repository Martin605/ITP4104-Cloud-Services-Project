from aws_cdk import (
    aws_ssm as ssm,
    core
    )

class ParametersStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Parameters
        CognitoPoolId = core.CfnParameter(self,"CognitoPoolId",
            type = "String",
            default = "CognitoPoolId"
        )
        CognitoClientId = core.CfnParameter(self,"CognitoClientId",
            type = "String",
            default = "CognitoClientId"
        )
        CognitoClientSecret = core.CfnParameter(self,"CognitoClientSecret",
            type = "String",
            default = "CognitoClientSecret"
        )
        CognitoDomain = core.CfnParameter(self,"CognitoDomain",
            type = "String",
            default = "CognitoDomain"
        )
        BaseUrl = core.CfnParameter(self,"BaseUrl",
            type = "String",
            default = "BaseUrl"
        )
        MyDBEndpoint = core.CfnParameter(self,"MyDBEndpoint",
            type = "String",
            default = "MyDBEndpoint"
        )
        ImageS3Bucket = core.CfnParameter(self,"ImageS3Bucket",
            type = "String",
            default = "ImageS3Bucket"
        )
        DBPassword_parameters = core.CfnParameter(self, "DBPassword",
            no_echo = True,
            description = "RDS Password.",
            min_length = 1,
            max_length = 41,
            constraint_description = "the password must be between 1 and 41 characters",
            default = "default"
        )
        
        # CognitoPoolIdParameter
        CognitoPoolIdParameter = ssm.CfnParameter(self,"CognitoPoolIdParameter",
            name ="edx-COGNITO_POOL_ID",
            type = "String",
            value = CognitoPoolId.value_as_string
        )
        # CognitoClientIdParameter
        CognitoClientIdParameter = ssm.CfnParameter(self,"CognitoClientIdParameter",
            name ="edx-COGNITO_CLIENT_ID",
            type = "String",
            value = CognitoClientId.value_as_string
        )
        # CognitoClientSecretParameter
        CognitoClientSecretParameter = ssm.CfnParameter(self,"CognitoClientSecretParameter",
            name ="edx-COGNITO_CLIENT_SECRET",
            type = "String",
            value = CognitoClientSecret.value_as_string
        )
        # CognitoDomainParameter
        CognitoDomainParameter = ssm.CfnParameter(self,"CognitoDomainParameter",
            name ="edx-COGNITO_DOMAIN",
            type = "String",
            value = CognitoDomain.value_as_string
        )
        # BaseUrlParameter
        BaseUrlParameter = ssm.CfnParameter(self,"BaseUrlParameter",
            name ="edx-BASE_URL",
            type = "String",
            value = BaseUrl.value_as_string
        )
        # DBHostParameter
        DBHostParameter = ssm.CfnParameter(self,"DBHostParameter",
            name ="edx-DATABASE_HOST",
            type = "String",
            value = MyDBEndpoint.value_as_string
        )
        # DBUserParameter
        DBUserParameter = ssm.CfnParameter(self,"DBUserParameter",
            name ="edx-DATABASE_USER",
            type = "String",
            value = "web_user"
        )
        # DBPasswordParameter
        DBPasswordParameter = ssm.CfnParameter(self,"DBPasswordParameter",
            name ="edx-DATABASE_PASSWORD",
            type = "String",
            value = DBPassword_parameters.value_as_string
        )
        # DBNameParameter
        DBNameParameter = ssm.CfnParameter(self,"DBNameParameter",
            name ="edx-DATABASE_DB_NAME",
            type = "String",
            value = "Photos"
        )
        # FlaskSecretParameter
        FlaskSecretParameter = ssm.CfnParameter(self,"FlaskSecretParameter",
            name ="edx-FLASK_SECRET",
            type = "String",
            value = "secret"
        )
        # PhotosBuckeTParameter
        PhotosBuckeTParameter = ssm.CfnParameter(self,"PhotosBuckeTParameter",
            name ="edx-PHOTOS_BUCKET",
            type = "String",
            value = ImageS3Bucket.value_as_string
        )
        