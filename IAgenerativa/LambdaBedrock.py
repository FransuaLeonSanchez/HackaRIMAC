import boto3
import json

def invoke_bedrock_model(bedrock, body, modelId, accept, contentType):
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    return json.loads(response.get('body').read())["content"][0]["text"]

def lambda_handler(event, context):
    ubicacion = event.get('ubicacion', 'Ubicación no especificada')
    tipo = event.get('tipo', 'Tipo no especificado')

    bedrock = boto3.client('bedrock-runtime', region_name="us-west-2")
    anthropic_version = "bedrock-2023-05-31"
    max_tokens = 1000

    body = json.dumps({
        "anthropic_version": anthropic_version,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [{"type": "text", "text": f"Genera un título para una alerta de tipo {tipo}"}]}]
    })

    body2 = json.dumps({
        "anthropic_version": anthropic_version,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [{"type": "text", "text": f"Generame un pequeño párrafo informativo sin título para una alerta de {tipo} en {ubicacion}"}]}]
    })

    modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
    accept = 'application/json'
    contentType = 'application/json'

    answer = invoke_bedrock_model(bedrock, body, modelId, accept, contentType)
    print(answer)

    answer2 = invoke_bedrock_model(bedrock, body2, modelId, accept, contentType)
    print(answer2)
