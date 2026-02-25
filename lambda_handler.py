import json
import boto3
import os

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    if path == '/health' and http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'status': 'healthy'})
        }
    elif path == '/alarms' and http_method == 'GET':
        return get_alarms()
    elif path == '/alarms/toggle' and http_method == 'POST':
        body = json.loads(event['body'])
        return toggle_alarm(body['function_name'], body['enabled'])
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'})
    }

def get_alarms():
    functions = os.environ.get('MONITORED_FUNCTIONS', '').split(',')
    alarms = []
    
    for func_name in functions:
        if not func_name:
            continue
        try:
            response = lambda_client.get_function_configuration(FunctionName=func_name)
            env_vars = response.get('Environment', {}).get('Variables', {})
            alarms.append({
                'name': func_name,
                'enabled': env_vars.get('ALARMS_ENABLED', 'true') == 'true'
            })
        except:
            pass
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'alarms': alarms})
    }

def toggle_alarm(function_name, enabled):
    try:
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        env_vars = response.get('Environment', {}).get('Variables', {})
        env_vars['ALARMS_ENABLED'] = 'true' if enabled else 'false'
        
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': env_vars}
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True, 'enabled': enabled})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
