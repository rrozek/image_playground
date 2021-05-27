import typing
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView, Request
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..utils import xresponse, get_pretty_logger, source_hash, ErrorCode
from ..exceptions import ParamError
from ..serializers import ImgSerializer
from ..views import schema_utils

logger = get_pretty_logger('api:views')


class Png2Tiff(APIView):
    """
    expected data:
    {
      "source": <base64 data>,
      "sha256": <sha256 of data>
    }
    """
    serializer_class = ImgSerializer

    @swagger_auto_schema(operation_description="convert png to tiff mapping alpha channel to clipping path ",
                         request_body=serializer_class,
                         responses={200: schema_utils.xresponse_ok(),
                                    400: schema_utils.xresponse_nok()})
    def post(self, request):
        try:
            clean_data = self.validate_payload(request.data)
        except ParamError as e:
            return xresponse(status.HTTP_400_BAD_REQUEST, e.error_code, e.msg)
        # TODO: publish to redis key: hash, data: source

        # {
        #     "result": "success",
        #     "error_code": 0,
        #     "data": {
        #       "result: "base_64_encoded tiff image",
        #     }
        # }
        return xresponse()

    def validate_payload(self, payload: dict) -> dict:
        img_serializer = self.serializer_class(data=payload)
        img_serializer.is_valid(raise_exception=True)
        clean_data = img_serializer.data
        input_hash = source_hash(clean_data['source'])
        if input_hash != clean_data['sha256']:
            raise ParamError(ErrorCode.DataMismatch, f'data hashes dont match. calculated hash: {input_hash}')

        return clean_data

class Tiff2Png(APIView):
    """
    expected data:
    {
      "source": <base64 data>,
      "sha256": <sha256 of data>
    }
    """

    serializer_class = ImgSerializer

    @swagger_auto_schema(operation_description="convert tiff to png mapping clipping path to alpha channel",
                         request_body=serializer_class,
                         responses={200: schema_utils.xresponse_ok(),
                                    400: schema_utils.xresponse_nok()})
    def post(self, request):
        try:
            clean_data = self.validate_payload(request.data)
        except ParamError as e:
            return xresponse(status.HTTP_400_BAD_REQUEST, e.error_code, e.msg)

        
        # {
        #     "result": "success",
        #     "error_code": 0,
        #     "data": {
        #       "result: "base_64_encoded png image",
        #     }
        # }
        return xresponse()

    def validate_payload(self, payload: dict) -> dict:
        img_serializer = self.serializer_class(data=payload)
        img_serializer.is_valid(raise_exception=True)
        clean_data = img_serializer.data
        input_hash = source_hash(clean_data['source'])
        if input_hash != clean_data['sha256']:
            raise ParamError(ErrorCode.DataMismatch, f'data hashes dont match. calculated hash: {input_hash}')

        return clean_data
