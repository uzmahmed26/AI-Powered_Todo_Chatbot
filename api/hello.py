"""
Ultra-simple test - no dependencies
"""

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"message": "Python function works!", "status": "success"}'
    }
