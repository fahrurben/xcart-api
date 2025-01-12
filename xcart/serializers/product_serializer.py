from rest_framework import serializers
from django.utils.text import slugify
from django.db.models import Q
from rest_framework.serializers import ValidationError

from xcart.models import Product, Variant
from .variant_serializer import VariantSerializer

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.CharField(max_length=255, read_only=True)
    category_id = serializers.IntegerField()
    variants = VariantSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category_id', 'description', 'thumbnail', 'have_variant', 'is_active', 'variants', 'created_at', 'updated_at')

    def validate_name(self, value):
        slug = slugify(value)
        q = Q(slug=slug)
        if self.instance:
            q &= ~Q(id=self.instance.id)

        if Product.objects.filter(q).exists():
            raise ValidationError('Product with same name already exist')
        return value

    def create(self, validated_data):
        have_variant = validated_data['have_variant']
        variants = validated_data.pop('variants')

        product_model = Product(**validated_data)
        product_model.slug = slugify(validated_data['name'])
        product_model.save()

        if have_variant:
            for variant in variants:
                variant_model = Variant(**variant)
                variant_model.slug = product_model.slug + "_" + slugify(variant['name'])
                variant_model.product = product_model
                variant_model.default_variant = False
                variant_model.save()

        return product_model

    def update(self, instance, validated_data):
        variants = validated_data.pop('variants')

        instance.name = validated_data.get('name', instance.name)
        instance.slug = slugify(validated_data.get('name', instance.name))
        instance.description = validated_data.get('description', instance.description)
        instance.have_variant = validated_data.get('have_variant', instance.have_variant)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        old_variants_ids = instance.variant_set.values_list('id', flat=True)
        new_variants_ids = [variant['id'] for variant in variants if 'id' in variant and variant['id'] is not None]

        deleted_ids = list(set(old_variants_ids) - set(new_variants_ids))

        for variant in variants:
            if 'id' in variant and variant['id'] is not None:
                variant_model = Variant.objects.get(id=variant[id])
            else:
                variant_model = Variant()
            variant_model.name = instance.name
            variant_model.slug = instance.slug + "_" + slugify(variant['name'])
            variant_model.product = instance
            variant_model.price = variant['price']
            variant_model.image = variant['image']
            variant_model.default_variant = False
            variant_model.is_active = variant['is_active']
            variant_model.save()

        for id in deleted_ids:
            variant_model = Variant.objects.get(id=id)
            variant_model.delete()

        return instance