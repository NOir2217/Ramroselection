import os
from django.shortcuts import render
from django.conf import settings

def home(request):
    """
    Renders the main entry point of the web application.
    If the Vite React app has been compiled (creating 'ramro/dist/index.html'), 
    it serves the production React SPA. Otherwise, it renders a fallback 
    landing page ('home.html') instructing the user to build the frontend.
    """
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    if os.path.exists(index_path):
        return render(request, 'index.html')
    return render(request, 'home.html')