from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def healthcheck(request):


  return JsonResponse({ "status": "OK" })