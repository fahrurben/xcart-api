from rest_framework import serializers
from django.utils.text import slugify
from django.db.models import Q
from rest_framework.serializers import ValidationError


from xcart.models import Category

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'is_active', 'created_at', 'updated_at')

    def validate_name(self, value):
        slug = slugify(value)
        q = Q(slug=slug)
        if self.instance:
            q &= ~Q(id=self.instance.id)

        if Category.objects.filter(q).exists():
            raise ValidationError('Category with same name already exist')
        return value

    def create(self, validated_data):
        obj = Category(**validated_data)
        obj.slug = slugify(validated_data['name'])
        obj.save()

        return obj

    def update(self, instance, validated_data):
        instance.slug = slugify(validated_data.get('name', instance.name))
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance