from aws_cdk import (
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_elasticloadbalancingv2 as elv2,
    aws_apigateway as apigw,
    core
)


class CdnStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # WebpageCDN
        webpage_cdn = cloudfront.CfnDistribution(self, 'WebpageCdn',
            distribution_config = {
                "defaultCacheBehavior" : {
                    "allowedMethods" : [
                        "DELETE",
                        "GET",
                        "HEAD",
                        "OPTIONS",
                        "PATCH",
                        "POST",
                        "PUT"
                    ],
                    "maxTTL" : 0,
                    "minTTL" : 0,
                    "defaultTTL" : 0,
                    "forwardedValues" : {
                        "queryString" : True,
                        "cookies" : {
                            "forward" : "all"
                        },
                        "headers" : [
                            "Accept",
                            "Referer",
                            "Athorization",
                            "Content",
                        ]
                    },
                    "targetOriginId" : "website",
                    "viewerProtocolPolicy" : "redirect-to-https",
                },
                "enabled" : True,
                "origins" : [{
                    "domainName" : "Fn::Sub : ${Api}.execute-api.${AWS::Region}.amazonaws.com",
                    "id" : "website",
                    "originPath" : "/Prod",
                    "customOriginConfig" : { "originProtocolPolicy" : "https-only" },
                }],
                "priceClass" : "PriceClass_All"
            }
        )
        
        # LoadBalancer
        loadbalancer = elv2.CfnLoadBalancer(self, 'LoadBalancer',
            subnets = [
                core.Fn.import_value("PublicSubnet1"),
                core.Fn.import_value("PublicSubnet2"),
            ],
            load_balancer_attributes = [{
                "key" : "idle_timeout.timeout_seconds",
                "value" : "50"
            }],
            security_groups = [core.Fn.import_value("WebSecurityGroupOutput"),]
        )
        
        # CloudWatchRole
        cloud_watch_role = iam.CfnRole(self, "CloudWatchRole",
            role_name= "lambda-execution-role",
            assume_role_policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                {
                  "Effect": "Allow",
                  "Principal": {
                    "Service": [
                      "apigateway.amazonaws.com"
                    ]
                  },
                  "Action": [
                    "sts:AssumeRole"
                  ]
                }]
            },
            path = "/",
            managed_policy_arns = [
                "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs",
                "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
            ],
        )
        
        # Account
        account = apigw.CfnAccount(self, "Account",
            cloud_watch_role_arn = cloud_watch_role.attr_arn
        )
        
        # Api
        api = apigw.CfnRestApi(self, "Api",
            name = "WebProxyApi",
            binary_media_types = ["*"]
        )
        
        #Resource
        resource = apigw.CfnResource(self, "Resource",
            parent_id = api.attr_root_resource_id,
            rest_api_id = api.ref,
            path_part = "{proxy+}"
        )
        
        # RootMethod
        root_method = apigw.CfnMethod(self, "RootMethod",
            http_method = "ANY",
            resource_id = api.attr_root_resource_id,
            rest_api_id = api.ref,
            authorization_type = "None",
            integration = {
                "integrationHttpMethod" : "ANY",
                "type" : "HTTP_PROXY",
                "uri" : "http://" + loadbalancer.attr_dns_name, 
                "passthroughBehavior" : "WHEN_NO_MATCH",
                "integrationResponses" : [{ 
                    "statusCode" : "200"
                }]
            }
        )
        
        # ProxyMethod
        proxy_method = apigw.CfnMethod(self, "ProxyMethod",
            http_method = "ANY",
            resource_id = resource.ref,
            rest_api_id = api.ref,
            authorization_type = "None",
            request_parameters = {
                "method.request.path.proxy": True
            },
            integration = {
                "cacheKeyParameters" : [
                    "method.request.path.proxy"
                ],
                "requestParameters" : {
                    "integration.request.path.proxy" : "method.request.path.proxy"
                },
                "integrationHttpMethod" : "ANY",
                "type" : "HTTP_PROXY",
                "uri" : "http://" + loadbalancer.attr_dns_name + "/{proxy}", 
                "passthroughBehavior" : "WHEN_NO_MATCH",
                "integrationResponses" : [{ 
                    "statusCode" : "200"
                }]
            }
        )

        # Deployment
        deployment = apigw.CfnDeployment(self, "Deployment",
            rest_api_id = api.ref
        )
        deployment.add_depends_on(root_method)
        deployment.add_depends_on(proxy_method)
            

        # ProdStage
        prod_stage = apigw.CfnStage(self, "ProdStage",
            stage_name = "Prod",
            description = "Prod Stage",
            rest_api_id = api.ref,
            deployment_id = deployment.ref,
            tracing_enabled = True
        )
        
        # Output
        core.CfnOutput(self, "AlbDNSName",
          value = loadbalancer.attr_dns_name,
          description = "ALB DNSName",
          export_name = "AlbDNSName"
        )
        
        core.CfnOutput(self, "DomainName",
          value = webpage_cdn.attr_domain_name,
          description = "Webpage CloudFront Domain name.",
          export_name = "DomainName"
        )
        
        core.CfnOutput(self, "LoadBalancerArn",
          value = loadbalancer.ref,
          export_name = "LoadBalancerArn"
        )