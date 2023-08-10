# import the JSON utility package
import json

# import the AWS SDK (for Python the package name is boto3)
import boto3

# Import dynamodb conditions to be able to express Key conditions in table queries.
from boto3.dynamodb.conditions import Key

# import two packages to help us with dates and date formatting
from time import gmtime, strftime

# create a DynamoDB resource object using the AWS SDK
dynamodb = boto3.resource('dynamodb')

# use the DynamoDB object to select our table
table = dynamodb.Table('PowerOfMathDatabase')
# store the current time in a human readable format in a variable
now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

# define the handler function that the Lambda service will use an entry point
def lambda_handler(event, context):
    print('request body: {}'.format(json.loads(event['body'])))
    
    # This function computes the exponential, base^exponent, by an iterative porocedure:
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

    #Initialize variables
    max_exponent=0
    max_result=1
    event_json=json.loads(event['body'])
    print('event_json=',event_json)
    base = int(event_json['base'])
    print('base=',base)
    #base = int(event_json['base'])
    exponent = int(event_json['exponent'])
    print('exponent=',exponent)
    
    #If inputs are negative, exit computation with an error message
    if base<0 or exponent<0:
        return {
            'statusCode': 200,
            'body': json.dumps('Negative input values provided: base='+ str(base)+', exponent '+str(exponent))
        }

    # store the current time in a human readable format in a variable
    now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    # Lookup prerecorded results for current base. 
    # ScanIndexForward=False gives us the dynamodb item with the largest possible exponent recorded for base.
    # Limit=1 ensures that we get one item, at most.
    rs=table.query(KeyConditionExpression=Key('BASE').eq(base), Limit=1, ScanIndexForward=False)
    print('rs=',rs)

    # If no items for base is prerecorded, insert the first item for base, (base, 0, 1)
    if len(rs['Items'])==0:
        print('ok1')
        response = table.put_item(
            Item={
                'BASE': base,
                'EXPONENT': 0,
                'Result': 1,
                'LatestGreetingTime':now
                })
        max_exponent=0
        max_result=1
    else:
        print('ok2')
        #An item for base exists, check the value of the exponent
        max_exponent=rs['Items'][0]['EXPONENT']
        max_result=rs['Items'][0]['Result']
        if exponent <= max_exponent:
            print('ok3')
            #An item for this pair of base and exponent already exists, look it up
            rs=table.query(KeyConditionExpression=Key('BASE').eq(base)&Key('EXPONENT').eq(exponent), Limit=1, ScanIndexForward=False)
            max_result=rs['Items'][0]['Result']

    #Compute items from the highest recorded pair of (base, exponent), up to the exponent desired in this invocation.
    #Store these items in DynamoDB
    for i in range(int(max_exponent)+1, exponent+1):
        print('ok4')
        max_result=max_result*base
        response = table.put_item(
            Item={
                'BASE': base,
                'EXPONENT': i,
                'Result': max_result,
                'LatestGreetingTime':now
                })
    print('Ready to return the result') 
    #body= json.loads('{"body":' +  str(max_result)+'}')
    body= '{"body":' +  str(max_result)+'}'
    print('body=', body)
    return {
            'statusCode': 200,
            'body': body,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
        }        

# write result and time to the DynamoDB table using the object we instantiated and save response in a variable

# return a properly formatted JSON object
