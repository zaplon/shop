from django.shortcuts import render
from rest_framework import viewsets
from .models import Mark, Opinion
from .serializers import MarkSerializer, OpinionSerializer
from django.shortcuts import render_to_response, RequestContext

class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer

class OpinionViewSet(viewsets.ModelViewSet):
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer

def opinions_view(request):
    opinions = Opinion.objects.all().order_by('-added_at')
    return render_to_response('opinions.html', {'opinions': opinions}, context_instance=RequestContext(request))

