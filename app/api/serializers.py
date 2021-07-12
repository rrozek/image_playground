from rest_framework import serializers


class ImgSerializer(serializers.Serializer):
    source = serializers.ImageField(required=True)


