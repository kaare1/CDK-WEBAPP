from aws_cdk import (
    # Duration,
    Stack,
    aws_codecommit as codecommit,
    Stage,
    Environment,
    aws_dynamodb as dynamodb,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cognito as cognito,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_apigateway as apigw
)

import aws_cdk as cdk

from constructs import Construct

from aws_cdk.pipelines import CodePipeline, CodeBuildStep, CodePipelineSource, ShellStep
from aws_cdk.aws_lambda import Function, InlineCode, Runtime, Code

class DatabaseStack(Stack):

    def __init__(self, scope, id):
        super().__init__(scope, id)
        self.table = dynamodb.Table(self, "Table",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING)
        )

class ComputeStack(Stack):
    def __init__(self, scope, id, *, table):
        super().__init__(scope, id)

class VpcStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope,id)
        vpc = ec2.Vpc(self, "VPC")

class MyLambdaStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_lambda = Function(
            self, "HelloHandler",
            runtime=Runtime.PYTHON_3_9,
            handler="hello.handler",
            code=Code.from_asset('lambda')
        )  

class DDBInlinePolicy(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:PutItem',
                'dynamodb:DeleteItem',
                'dynamodb:GetItem',
                'dynamodb:Scan',
                'dynamodb:Query',
                'dynamodb:UpdateItem'
            ],
            resources=['arn:aws:lambda:eu-west-1:153065748672:function:Test-PwrMathLambdaStack-PwrMathHandler452B1476-9iEj28yiC5JM']
        )

class PwrMathLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_lambda = Function(
            self, "PwrMathHandler",
            runtime=Runtime.PYTHON_3_9,
            handler="pwr-of-math.lambda_handler",
            code=Code.from_asset('lambda')
        )

        pol = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:PutItem',
                'dynamodb:DeleteItem',
                'dynamodb:GetItem',
                'dynamodb:Scan',
                'dynamodb:Query',
                'dynamodb:UpdateItem'
            ],
            resources=['arn:aws:dynamodb:eu-west-1:153065748672:table/PowerOfMathDatabase']
        )

        api = apigw.LambdaRestApi(
            self, 'Endpoint',
            handler=my_lambda,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                #allow_origins=['*'],
                allow_methods=apigw.Cors.ALL_METHODS,
                #allow_methods=['POST'],
                allow_headers=apigw.Cors.DEFAULT_HEADERS
                #allow_headers='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            ),
            endpoint_configuration=apigw.EndpointConfiguration(
                types=[apigw.EndpointType.REGIONAL]
            )
        )
        #items = api.root.add_resource("items")
        #items.add_method("GET") # GET /items
        #items.add_method("POST") # POST /items
    

class CognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_cognito_user_pool = cognito.UserPool(self, 'myUserPool', user_pool_name='myUserPool', self_sign_up_enabled=False)
        
        client = my_cognito_user_pool.add_client("customer-app-client")

        client_id = client.user_pool_client_id

class CdkStaticWebsiteStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #my_hosted_zone = route53.PublicHostedZone(self, "HostedZone", zone_name="kjk.keycore.cloud")
        #my_n_virginia_certificate = acm.DnsValidatedCertificate(self, "CrossRegionCertificate",
        #my_n_virginia_certificate = acm.Certificate(self, "CrossRegionCertificate",
        #    domain_name="*.kjk.keycore.cloud",
        #    hosted_zone=my_hosted_zone,
        #    region="us-east-1"
        #    )
        # Creates a distribution from an S3 bucket.
        my_bucket = s3.Bucket(self, "myBucket")
        my_distribution=cloudfront.Distribution(self, "myDist",
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(my_bucket)),
            default_root_object='index-ttt.html'
            #certificate=my_n_virginia_certificate,
            #domain_names=['kjk.keycore.cloud']
        )
        s3deploy.BucketDeployment(self, "BucketDeployment",
            sources=[s3deploy.Source.asset("./website")],
            destination_bucket=my_bucket,
            cache_control=[s3deploy.CacheControl.from_string("max-age=31536000,public,immutable")],
            prune=False,
            distribution=my_distribution
        )
        #a_record = route53.ARecord(
        #    self, 
        #    id="AliasRecord", 
        #    zone=my_hosted_zone, 
        #    record_name="frontend.kjk.keycore.cloud", 
        #    target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(my_distribution))
        #    )
        
        


class MyPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository=codecommit.Repository.from_repository_name(self, "codecommit-repository", "my-pipeline")
        pipeline =  CodePipeline(self, "Pipeline", 
                        pipeline_name="MyPipeline",
                        #cross_account_keys=True,
                        synth=CodeBuildStep("Synth", 
                            input=CodePipelineSource.code_commit(repository,"master"),
                            commands=["npm install -g aws-cdk", 
                                "python -m pip install -r requirements.txt", 
                                "cdk synth"],
                                role_policy_statements=[
                                    iam.PolicyStatement(actions=['sts:AssumeRole'], resources=['*'],conditions={'StringEquals':{'iam:ResourceTag/aws-cdk:bootstrap-role': 'lookup'}})
                                ]
                        )
                    )        
        pipeline.add_stage(MyApplication(self, "Test",
            env=cdk.Environment(
                account="153065748672",
                region="eu-west-1"
            )
        ))


class MyApplication(Stage):
    def __init__(self, scope, id, *, env=None, outdir=None,stage_name="Deployment"):
        super().__init__(scope, id, env=env, outdir=outdir)

        vpc_stack = VpcStack(self, "VPC1")
        db_stack = DatabaseStack(self, "Database")
        ComputeStack(self, "Compute", table=db_stack.table)
        iam_stack=DDBInlinePolicy(self, "DDBInlinePolicy")
        lambdaStack = MyLambdaStack(self, "LambdaStack")
        pwr_math_lambda_stack = PwrMathLambdaStack(self, "PwrMathLambdaStack")
        static_website = CdkStaticWebsiteStack(self, "StaticWebsiteStack")
        cognito_stack = CognitoStack(self, "CognitoStack")