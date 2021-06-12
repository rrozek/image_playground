import os.path
import typing
import subprocess
import base64
from django.conf import settings
from django.core.files.storage import default_storage
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView, Request
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..utils import xresponse, get_pretty_logger, file_hash, ErrorCode, source_hash, encode_base64
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

        # TODO: convert png-alpha to svg
        # convert easy.png -set colorspace RGB -alpha extract easy_alpha.png
        # convert easy_alpha.png easy_alpha.svg
        # convert png to tiff
        # gimp tiff with alpha.svg
        input_filepath = os.path.join(clean_data['storage'], clean_data['filename'])
        output_filepath = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}.tiff")
        output_alpha_filepath = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}_alpha.png")
        command_extract_alpha = f'convert {input_filepath} -set colorspace RGB -alpha extract {output_alpha_filepath}'

        output_svg_filepath = f'{"".join(output_alpha_filepath.split(".")[:-1])}.svg'
        command_alpha_svg = f'convert {output_alpha_filepath} {output_svg_filepath}'

        output_tiff_tmp_filepath = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}_tmp.tiff")
        command_png_to_tiff = f'convert {input_filepath} {output_tiff_tmp_filepath}'

        logger.info(f'command: {command_extract_alpha}')
        process = subprocess.Popen(
            command_extract_alpha.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'process resultcode: {process.returncode}')

        logger.info(f'command: {command_alpha_svg}')
        process = subprocess.Popen(
            command_alpha_svg.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'process resultcode: {process.returncode}')

        logger.info(f'command: {command_png_to_tiff}')
        process = subprocess.Popen(
            command_png_to_tiff.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'process resultcode: {process.returncode}')

        gimp_command = f"gimp -i -b '(svg-clip-path \"{output_tiff_tmp_filepath}\" \"{output_svg_filepath}\" \"{output_filepath}\" )' -b '(gimp-quit 0)'"

        logger.info(f'command: {gimp_command}')
        process = subprocess.Popen(
            gimp_command, shell=True,
            # ['gimp', '-i', '-b', f"'(svg-clip-path \"{output_tiff_tmp_filepath}\" \"{output_svg_filepath}\" \"{output_filepath}\" )'", '-b', "'(gimp-quit 0)'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(20)
        logger.info(f'process resultcode: {process.returncode}')
        # {
        #     "result": "success",
        #     "error_code": 0,
        #     "data": {
        #       "result: "base_64_encoded png image",
        #     }
        # }
        return xresponse(result=encode_base64(output_filepath))

    def validate_payload(self, payload: dict) -> dict:
        img_serializer = self.serializer_class(data=payload)
        img_serializer.is_valid(raise_exception=True)
        clean_data = img_serializer.validated_data
        filename = default_storage.save(clean_data['source'].name, clean_data['source'])
        input_hash = file_hash(default_storage.path(filename))
        if input_hash != clean_data['sha256']:
            raise ParamError(ErrorCode.DataMismatch, f'data hashes dont match. calculated hash: {input_hash}')

        clean_data['filename'] = filename
        clean_data['storage'] = default_storage.location
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

        input_filepath = os.path.join(clean_data['storage'], clean_data['filename'])
        output_filepath = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}.png")
        command = f'convert {input_filepath} -alpha transparent -clip -alpha opaque {output_filepath}'
        process = subprocess.Popen(
            command.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'command: {command}')
        logger.info(f'process resultcode: {process.returncode}')
        # {
        #     "result": "success",
        #     "error_code": 0,
        #     "data": {
        #       "result: "base_64_encoded png image",
        #     }
        # }
        return xresponse(result=encode_base64(output_filepath))

    def validate_payload(self, payload: dict) -> dict:
        img_serializer = self.serializer_class(data=payload)
        img_serializer.is_valid(raise_exception=True)
        clean_data = img_serializer.validated_data
        filename = default_storage.save(clean_data['source'].name, clean_data['source'])
        input_hash = file_hash(default_storage.path(filename))
        if input_hash != clean_data['sha256']:
            raise ParamError(ErrorCode.DataMismatch, f'data hashes dont match. calculated hash: {input_hash}')

        clean_data['filename'] = filename
        clean_data['storage'] = default_storage.location

        return clean_data
