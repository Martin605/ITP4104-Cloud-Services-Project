const AWS = require('aws-sdk');
const response = require('cfn-response');
const cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider();
exports.handler = (event, context) => {
    try {
        switch (event.RequestType) {
            case 'Create':
            case 'Update':
                cognitoIdentityServiceProvider.updateUserPoolClient({
                    UserPoolId: event.ResourceProperties.UserPoolId,
                    ClientId: event.ResourceProperties.UserPoolClientId,
                    SupportedIdentityProviders: event.ResourceProperties.SupportedIdentityProviders,
                    CallbackURLs: [event.ResourceProperties.CallbackURL],
                    LogoutURLs: [event.ResourceProperties.LogoutURL],
                    AllowedOAuthFlowsUserPoolClient: (event.ResourceProperties.AllowedOAuthFlowsUserPoolClient == 'true'),
                    AllowedOAuthFlows: event.ResourceProperties.AllowedOAuthFlows,
                    AllowedOAuthScopes: event.ResourceProperties.AllowedOAuthScopes
                })
                    .promise()
                    .then(data => {
                        let params = {
                            Domain: event.ResourceProperties.AppDomain,
                            UserPoolId: event.ResourceProperties.UserPoolId
                        };
                        console.log(params);
                        return cognitoIdentityServiceProvider.createUserPoolDomain(params).promise();
                    })
                    .then(data => {
                        let params = {
                            ClientId: event.ResourceProperties.UserPoolClientId,
                            UserPoolId: event.ResourceProperties.UserPoolId
                        };
                        return cognitoIdentityServiceProvider.describeUserPoolClient(params).promise();
                    })
                    .then(data => {
                        console.log(data);
                        let responseData = { ClientSecret: data.UserPoolClient.ClientSecret };
                        console.log(responseData);
                        response.send(event, context, response.SUCCESS, responseData);
                    })
                    .catch(err => {
                        console.error(err);
                        response.send(event, context, response.FAILED, {});
                    });

                break;

            case 'Delete':
                let params = {
                    Domain: event.ResourceProperties.AppDomain,
                    UserPoolId: event.ResourceProperties.UserPoolId
                };
                cognitoIdentityServiceProvider.deleteUserPoolDomain(params).promise()
                    .then(data => response.send(event, context, response.SUCCESS, {}))
                    .catch(error => response.send(event, context, response.FAILED, {}));
                break;
        }

        console.info(`CognitoUserPoolClientSettings Success for request type ${event.RequestType}`);
    } catch (error) {
        console.error(`CognitoUserPoolClientSettings Error for request type ${event.RequestType}:`, error);
        response.send(event, context, response.FAILED, {});
    }
}