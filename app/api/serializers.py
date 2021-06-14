from rest_framework import serializers
from drf_base64.fields import Base64ImageField


def hash_validator(value):
    if len(value) != 64:
        raise serializers.ValidationError(f'Should be 64 hex digits long')


class HashField(serializers.CharField):
    def __init__(self, **kwargs):
        super(HashField, self).__init__(**kwargs)
        self.max_length = 64
        self.min_length = 64
        self.validators = [hash_validator]


class ImgSerializer(serializers.Serializer):
    source = Base64ImageField(required=True)
    sha256 = HashField(required=True)
    output = serializers.ChoiceField(['url', 'base64'], required=True)



