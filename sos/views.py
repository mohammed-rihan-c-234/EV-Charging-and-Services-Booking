from django.shortcuts import render, redirect
from .models import SOSAlert
from .forms import SOSForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from service_center.models import ServiceCenter
from .utils import haversine_distance
from .models import AssignedCenter


def sos_list(request):
    """Show recent SOS alerts."""
    alerts = SOSAlert.objects.order_by('-created_at')[:50]
    return render(request, 'sos/sos_list.html', {'alerts': alerts})


def sos_submit(request):
    """Simple page where users can submit an SOS alert.

    If the user is logged in we attach them to the alert. After successful
    submission we redirect back to the alerts list and notify nearby service centers.
    """
    if request.method == 'POST':
        form = SOSForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            if request.user.is_authenticated:
                alert.user = request.user
            
            # Store additional form data
            name = form.cleaned_data.get('name', '')
            vehicle_model = form.cleaned_data.get('vehicle_model', '')
            number_plate = form.cleaned_data.get('number_plate', '')
            
            # Store in vehicle_plate field (or message if needed)
            if number_plate:
                alert.vehicle_plate = number_plate
            
            alert.save()
            
            # Notify nearby service centers if location is available
            if alert.latitude and alert.longitude:
                notify_nearby_service_centers(alert, name, vehicle_model)
            
            return redirect('sos:list')
    else:
        form = SOSForm()

    return render(request, 'sos/sos_alert_form.html', {'form': form})


def notify_nearby_service_centers(alert, user_name, vehicle_model, radius_km=50):
    """Find and notify nearest service centers about the SOS alert."""
    nearest = []
    
    # Get service centers with location data
    centers = ServiceCenter.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    for center in centers:
        distance = haversine_distance(float(alert.latitude), float(alert.longitude), 
                                    float(center.latitude), float(center.longitude))
        if distance is not None and distance <= radius_km:
            nearest.append((distance, center))
    
    # Sort by distance and keep top 5 nearest
    nearest.sort(key=lambda x: x[0])
    top_centers = nearest[:5]
    
    # Create AssignedCenter records to notify them
    for distance, center in top_centers:
        AssignedCenter.objects.create(
            alert=alert, 
            center=center, 
            distance_km=round(distance, 3)
        )
    
    return len(top_centers)


@csrf_exempt
def api_receive_alert(request):
    """Receive an SOS alert as JSON (for IoT devices or external services).

    Expected JSON: { "vehicle_plate": "ABC123", "latitude": 12.34, "longitude": 56.78, "message": "help", "contact": "+123" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    lat = payload.get('latitude')
    lon = payload.get('longitude')
    message = payload.get('message') or payload.get('msg') or ''
    plate = payload.get('vehicle_plate') or payload.get('plate')
    contact = payload.get('contact')

    alert = SOSAlert.objects.create(
        vehicle_plate=plate or 'unknown',
        latitude=lat or 0.0,
        longitude=lon or 0.0,
        message=message,
        contact=contact or ''
    )

    # find nearest service centers within radius (km)
    nearest = []
    try:
        radius_km = float(payload.get('radius_km', 50))
    except Exception:
        radius_km = 50.0

    # gather centers with lat/lon
    centers = ServiceCenter.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    for c in centers:
        d = haversine_distance(lat, lon, c.latitude, c.longitude)
        if d is None:
            continue
        if d <= radius_km:
            nearest.append((d, c))

    # sort by distance and keep top N
    nearest.sort(key=lambda x: x[0])
    top = nearest[:5]

    # create AssignedCenter records
    assigned = []
    for dist, center in top:
        ac = AssignedCenter.objects.create(alert=alert, center=center, distance_km=round(dist, 3))
        assigned.append({'id': center.id, 'name': center.name, 'distance_km': round(dist, 3), 'phone': center.phone, 'address': center.address})

    return JsonResponse({'status': 'ok', 'id': alert.id, 'nearest_centers': assigned})
