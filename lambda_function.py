def lambda_handler(event, context):
    """Simple Lambda function to return a message and `200` status code."""
    return {
        'body': 'OK',
        'headers': {'Content-Type': 'application/json'},
        'statusCode': 200,
    }