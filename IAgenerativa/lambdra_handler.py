import boto3
import json
from boto3.dynamodb.conditions import Key

seguros = {
    "Seguros de Salud": {
        "Seguro de Salud": "Te facilitamos atención médica en una gran red de clínicas.",
        "Seguro Salud Internacional": "Vive tranquilo con un seguro complementario con excelentes clínicas alrededor del mundo.",
        "Salud Flexible": "Arma tu plan con las coberturas y asistencias que necesites.",
        "Salud Adulto Mayor": "Cuidamos tu salud para que vivas tranquilo tus años dorados.",
        "Salud Hospitalario": "Tus hospitalizaciones y cirugías con una cobertura millonaria.",
        "EPS": "Dale a tus colaboradores un plan EPS con múltiples beneficios.",
        "Salud Empresarial": "Creamos un seguro personalizable para proteger a tus colaboradores."
    },
    "Seguros Vehicular y SOAT": {
        "Vehicular": "Catalogado como excelente por el 98 % de nuestros clientes.",
        "Vehicular Flexible": "Nadie sabe mejor qué necesitas que tú. Elige tu plan y coberturas.",
        "Pago por Kilómetros": "Un seguro con planes según los km que recorras. ¡Ahorra hasta un 45%!",
        "SOAT Virtual": "Protégete a ti y a tus acompañantes con muchos beneficios y descuentos.",
        "Consulta y descarga tu SOAT": "Obtén tu certificado fácil y rápido en nuestra nueva web de consulta."
    },
    "Seguros de Vida": {
        "Vida Ahorro con Devolución": "Vive bien y ahorra a la vez. Y, si lo necesitas, dispón de tu fondo.",
        "Plan Vida Flexible": "Protegemos a tu familia y hacemos crecer la rentabilidad de tus aportes.",
        "Seguro Universitario": "Asegura la educación y futuro de tus hijos con un fondo universitario.",
        "Seguro de Sepelio": "Ten la tranquilidad de que no los dejarás solos en momentos difíciles.",
        "Vida Plus": "Un seguro de vida a tu alcance para proteger a los que más quieres."
    },
    "Seguros de Vida e Inversión": {
        "Ahorro Seguro": "Construye tu bienestar económico futuro mientras proteges tu presente.",
        "Renta Garantizada": "Te garantizamos un ingreso mensual y la rentabilidad de tu fondo.",
        "Inversión Global": "Vive al máximo mientras tu dinero crece en el mercado internacional."
    },
    "Seguros de Hogar": {
        "Casa a tu Medida": "Protegemos tu casa como lo harías tú para que vivas tranquilo.",
        "Seguro Domiciliario": "Cuidamos tu casa y tus pertenencias ante robos, incendios y más."
    },
    "Seguros para Empresas": {
        "Multirriesgo": "Cuidamos tus bienes e inmuebles y los de terceros bajo tu custodia.",
        "Transporte de mercadería": "Protegemos tu mercancía ante daños y pérdidas.",
        "Construcción (CAR & EAR)": "Un seguro integral para proyectos de construcción y montaje.",
        "Responsabilidad Civil (D&O)": "Protege ante demandas el patrimonio de los directivos de tu empresa.",
        "Riesgo Cibernético": "Te cubre ante fallas de seguridad en el sistema y sus consecuencias.",
        "3D, Robo y/o Deshonestidad": "Asegura a tu empresa ante estafas, asaltos, falsificaciones y más."
    },
    "Pensiones": {
        "Renta Vitalicia": "Asegura tu futuro y el de quienes amas, con una pensión de por vida y beneficios adicionales."
    }
}

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Peligros')


def invoke_bedrock_model(bedrock, body, modelId, accept, contentType):
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    return json.loads(response.get('body').read())["content"][0]["text"]

def lambda_handler(event, context):
    
    try:
        ubicacion = event.get('ubicacion', 'Ubicación no especificada')
        tipo = event.get('tipo_alerta', 'Tipo no especificado')
        
        #ubicacion= "Puerto Supe, Peru",
        #tipo= "ACCIDENTE VEHICULAR / PARTICULAR / AUTOMOVIL"
        
    
        bedrock = boto3.client('bedrock-runtime', region_name="us-west-2")
        anthropic_version = "bedrock-2023-05-31"
        max_tokens = 1000
    
        body = json.dumps({
            "anthropic_version": anthropic_version,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": [{"type": "text", "text": f"Genera un título para una alerta de tipo {tipo}, solo dame el titulo"}]}]
        })
    
        body2 = json.dumps({
            "anthropic_version": anthropic_version,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": [{"type": "text", "text": f"Generame un pequeño párrafo informativo sin título para una alerta de {tipo} en {ubicacion}"}]}]
        })
        
        
        
        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
        accept = 'application/json'
        contentType = 'application/json'
    
        titulo = invoke_bedrock_model(bedrock, body, modelId, accept, contentType)
        
    
        descripcion = invoke_bedrock_model(bedrock, body2, modelId, accept, contentType)
        
    
        body3 = json.dumps({
            "anthropic_version": anthropic_version,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": [{"type": "text", "text": f"Dime cuál de los siguientes seguros de este diccionario: {seguros} aplicaría mejor para esta noticia: {descripcion}. Solo el nombre del seguro, no me digas el porque."}]}]
        })
    
        categoria = invoke_bedrock_model(bedrock, body3, modelId, accept, contentType)
        
        print(titulo)
        print(descripcion)
        print(categoria)
        
        # Establecer PK a 1
        pk = 0

        # Obtener el valor más alto de SK
        response = table.query(
            KeyConditionExpression=Key('pk').eq(pk),
            ScanIndexForward=False,  # Ordenar de forma descendente
            Limit=1  # Solo obtener el primer resultado
        )

        # Determinar el siguiente SK
        if 'Items' in response and response['Items']:
            last_sk = response['Items'][0]['sk']
            new_sk = int(last_sk) + 1
        else:
            new_sk = 1  # Si no hay elementos, el primer SK será 1
            
        
        new_item = {
            'pk': pk,
            'sk': new_sk,
            'coordenada': event.get('coordenada'),
            'fecha_hora': event.get('fecha_hora'),
            'id_post': event.get('id_post'),
            'link': event.get('link'),
            'tipo': event.get('tipo'),
            'ubicacion': event.get('ubicacion'),
            'titulo': titulo,
            'descripcion': descripcion,
            'categoria': categoria
        }
        
        print(new_item)
        
        # Insertar el nuevo elemento en la tabla
        table.put_item(Item=new_item)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Elemento procesado y registrado"
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Ocurrió un error: {str(e)}')
        }