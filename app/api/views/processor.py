import os.path
import typing
import subprocess
import base64
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.urls.base import resolve
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response
from rest_framework.schemas import coreapi
from rest_framework.views import APIView, Request
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..drf_auth_override import CsrfExemptSessionAuthentication
from ..utils import xresponse, get_pretty_logger, file_hash, ErrorCode, source_hash, encode_base64
from ..exceptions import ParamError
from ..serializers import ImgSerializer
from ..views import schema_utils

logger = get_pretty_logger('api:views')

class RequestImgFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [

        ]


def validate_payload(serializer_class, payload: dict) -> dict:
    img_serializer = serializer_class(data=payload)
    img_serializer.is_valid(raise_exception=True)
    clean_data = img_serializer.validated_data
    filename = default_storage.save(clean_data['source'].name.replace(' ', '_'), clean_data['source'])

    clean_data['filename'] = filename
    clean_data['storage'] = default_storage.location
    return clean_data


class ImgProcessAPIView(APIView):
    filter_backends = (RequestImgFilterBackend,)
    serializer_class = ImgSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def process_request(self, clean_data, request):
        raise NotImplementedError('not implemented')

    @property
    def return_format(self):
        return ''

    @swagger_auto_schema(operation_description="",
                         manual_parameters=[Parameter('output', in_='query', required=True, type='string')],
                         request_body=serializer_class,
                         responses={200: schema_utils.xresponse_ok(),
                                    400: schema_utils.xresponse_nok()})
    def post(self, request):
        if 'output' not in request.query_params:
            output = 'image'
        else:
            output = str(request.query_params['output']).lower()
        supported_output_formats = ['image', 'url']
        if output not in supported_output_formats:
            return xresponse(
                status=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.InvalidParams,
                msg=f'Unhandled output format. Selected: {output} available: [{", ".join(supported_output_formats)}]'
            )
        try:
            clean_data = validate_payload(self.serializer_class, request.data)
        except ParamError as e:
            return xresponse(status.HTTP_400_BAD_REQUEST, e.error_code, e.msg)

        try:
            output_filepath, output_filename = self.process_request(clean_data, request)

            if output == 'image':
                with open(output_filepath, 'rb') as file:
                    return HttpResponse(content=file.read(), content_type=f'image/{self.return_format}')
            else:
                return HttpResponse(
                    status=status.HTTP_303_SEE_OTHER,
                    headers={
                        'Location': request.build_absolute_uri(f'{settings.MEDIA_URL}{output_filename}')
                    },
                )
        except Exception as e:
            return xresponse(status.HTTP_400_BAD_REQUEST, ErrorCode.NotFound, e)


class Png2Tiff(ImgProcessAPIView):

    @property
    def return_format(self):
        return 'tiff'

    def process_request(self, clean_data, request):
        # convert easy.png -set colorspace RGB -alpha extract easy_alpha.png
        # convert easy_alpha.png easy_alpha.svg
        # convert png to tiff
        # gimp tiff with alpha.svg
        input_filepath = os.path.join(clean_data['storage'], clean_data['filename'])
        output_filename = f"{''.join(clean_data['filename'].split('.')[:-1])}.tiff"
        output_filepath = os.path.join(clean_data['storage'], output_filename)
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
            gimp_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(20)
        logger.info(f'process resultcode: {process.returncode}')

        os.remove(input_filepath)
        os.remove(output_alpha_filepath)
        os.remove(output_svg_filepath)
        os.remove(output_tiff_tmp_filepath)

        return output_filepath, output_filename


class Tiff2Png(ImgProcessAPIView):

    @property
    def return_format(self):
        return 'png'

    def process_request(self, clean_data, request):
        input_filepath = os.path.join(clean_data['storage'], clean_data['filename'])
        output_filename = f"{''.join(clean_data['filename'].split('.')[:-1])}.png"
        output_filepath = os.path.join(clean_data['storage'], output_filename)
        command = f'convert {input_filepath} -alpha transparent -clip -alpha opaque {output_filepath}'
        process = subprocess.Popen(
            command.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'command: {command}')
        logger.info(f'process resultcode: {process.returncode}')

        os.remove(input_filepath)

        return output_filepath, output_filename


class Eps2Png(ImgProcessAPIView):
    @property
    def return_format(self):
        return 'png'

    def process_request(self, clean_data, request):

        input_filepath = os.path.join(clean_data['storage'], clean_data['filename'])
        output_filename = f"{''.join(clean_data['filename'].split('.')[:-1])}.png"
        output_filepath = os.path.join(clean_data['storage'], output_filename)
        command = f'convert {input_filepath} -alpha transparent -clip -alpha opaque {output_filepath}'
        process = subprocess.Popen(
            command.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'command: {command}')
        logger.info(f'process resultcode: {process.returncode}')

        os.remove(input_filepath)
        return output_filepath, output_filename


class Png2Eps(ImgProcessAPIView):

    @property
    def return_format(self):
        return 'postscript'

    def process_request(self, clean_data, request):

        # TODO: convert png-alpha to svg
        # convert easy.png -set colorspace RGB -alpha extract easy_alpha.png
        # convert easy_alpha.png easy_alpha.svg
        # convert png to tiff
        # gimp tiff with alpha.svg
        input_filepath = os.path.join(clean_data['storage'], clean_data['filename'])
        output_filename = f"{''.join(clean_data['filename'].split('.')[:-1])}.eps"
        output_filepath = os.path.join(clean_data['storage'], output_filename)
        output_alpha_filepath = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}_alpha.png")
        command_extract_alpha = f'convert {input_filepath} -set colorspace RGB -alpha extract {output_alpha_filepath}'

        output_svg_filepath = f'{"".join(output_alpha_filepath.split(".")[:-1])}.svg'
        command_alpha_svg = f'convert {output_alpha_filepath} {output_svg_filepath}'

        output_tiff_tmp_filepath = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}_tmp.tiff")
        output_filepath_tiff = os.path.join(clean_data['storage'], f"{''.join(clean_data['filename'].split('.')[:-1])}_final.tiff")
        command_png_to_tiff = f'convert {input_filepath} {output_tiff_tmp_filepath}'
        command_tiff_to_eps = f'convert {output_filepath_tiff} {output_filepath}'

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

        gimp_command = f"gimp -i -b '(svg-clip-path \"{output_tiff_tmp_filepath}\" \"{output_svg_filepath}\" \"{output_filepath_tiff}\" )' -b '(gimp-quit 0)'"

        logger.info(f'command: {gimp_command}')
        process = subprocess.Popen(
            gimp_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(20)
        logger.info(f'process resultcode: {process.returncode}')

        logger.info(f'command: {command_tiff_to_eps}')
        process = subprocess.Popen(
            command_tiff_to_eps.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(10)
        logger.info(f'process resultcode: {process.returncode}')

        os.remove(input_filepath)
        os.remove(output_alpha_filepath)
        os.remove(output_svg_filepath)
        os.remove(output_tiff_tmp_filepath)
        os.remove(output_filepath_tiff)

        return output_filepath, output_filename
