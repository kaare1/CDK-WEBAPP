# CDK-WEBAPP
Serverless webapp in CDK: CDK_PIPELINE, HTML Frontend, JavaScript, CORS, ApiGateway, Lambda, DynamoDB, Iterative, cumulative and  persited calculation of exponential numbers.

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
