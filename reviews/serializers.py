from rest_framework import serializers
from .models import Mark, Opinion

class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark

class OpinionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opinion
