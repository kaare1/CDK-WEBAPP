# CDK-WEBAPP
Serverless webapp in CDK: CDK_PIPELINE, HTML Frontend, JavaScript, CORS, ApiGateway, Lambda, DynamoDB, Iterative, cumulative and  persited calculation of exponential numbers.

This web application is a continued development of the web application presented by "Tiny Tech Tutorials" on YouTube in ythe following video: 

AWS Project - Architect and Build an End-to-End AWS Web Application from Scratch, Step by Step

https://www.youtube.com/watch?v=7m_q1ldzw0U

In the video above, a serverless web application is developed by defining a dynamodb table, lambda function and apigateway (with cors) in the AWS console, and then deploying a html/js frontend using AWS Amplify.

This present project transforms it all to CDK (Python) and replaces the Amnplify app with a S3 static  website and a cloudfront distribution.

    # This webapplication computes the exponential, base^exponent, by an iterative porocedure:
    # 
    # base^0 = 1
    # base^1 = base * base^0 = base
    # base^2 = base^1 * base
    # ...
    # base^exponent = base^(exponent-1)* base 
    # 
    # All results, final results as well as intermediary, are stored in dynamoDB as triples
    # 
    # (BASE, EXPONENT, Result)
    #
    # Any compoutation will lookup and prerecorded results (or sub-results), and use these if possible.
