from django.shortcuts import render
from rest_framework import viewsets
from .models import Mark, Opinion
from .serializers import MarkSerializer, OpinionSerializer

class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer

class OpinionViewSet(viewsets.ModelViewSet):
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer
