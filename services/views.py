from django.shortcuts import render
from .models import ServiceType

def service_list(request):
    """Show a list of service types."""
    services = ServiceType.objects.all()
    return render(request, 'services/service_list.html', {'services': services})
