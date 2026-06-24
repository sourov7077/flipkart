# flipkart/views.py
from django.shortcuts import render

def handler404(request, exception):
    """404 Page Not Found"""
    return render(request, '404.html', status=404)

def handler500(request):
    """500 Server Error"""
    return render(request, '500.html', status=500)

def handler403(request, exception):
    """403 Permission Denied"""
    return render(request, '403.html', status=403)

def handler400(request, exception):
    """400 Bad Request"""
    return render(request, '400.html', status=400)