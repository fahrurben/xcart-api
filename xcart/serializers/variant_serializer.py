from rest_framework import serializers
from django.utils.text import slugify
from django.db.models import Q
from rest_framework.serializers import ValidationError

from xcart.models import Variant

class VariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    slug = serializers.CharField(max_length=255, read_only=True)
    default_variant = serializers.BooleanField(required=False)

    class Meta:
        model = Variant
        fields = ('id', 'name', 'slug', 'price', 'image', 'default_variant', 'is_active', 'created_at', 'updated_at')
