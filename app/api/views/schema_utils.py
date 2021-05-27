from drf_yasg import openapi


hash_item = openapi.Items(
    type=openapi.TYPE_STRING, pattern='base58 representation of sha256 hash(xpub, recovery_key, instant_key)'
)

result_schema = openapi.Schema(type=openapi.TYPE_STRING, description='success or error')
session_token_schema = openapi.Schema(type=openapi.TYPE_STRING, description='token for follow-up requests')
msg_schema = openapi.Schema(type=openapi.TYPE_STRING, description='error description or empty string')
error_code_schema = openapi.Schema(type=openapi.TYPE_INTEGER, description='internal error code')

def xresponse_ok(json_example={'result': 'success', 'error_code': 0, 'msg': '', 'data': {'actual_response': 'content'}}):
    return openapi.Response(
        description='OK response',
        examples={'application/json': json_example},
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': result_schema,
                'error_code': error_code_schema,
                'msg': msg_schema,
                'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='response data')
            },
        ),
    )


def xresponse_nok(
    json_example={
        'result': 'error',
        'msg': 'something went wrong',
        'error_code': 12,
    }
):
    return openapi.Response(
        description='NOK response',
        examples={'application/json': json_example},
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': result_schema,
                'msg': msg_schema,
                'error_code': error_code_schema,
            },
        ),
    )

