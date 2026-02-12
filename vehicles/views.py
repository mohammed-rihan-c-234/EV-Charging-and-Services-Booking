from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Vehicle
from .forms import VehicleForm


# Simple view to list vehicles. Non-technical friendly comments included.
def vehicle_list(request):
    """Show a list of registered vehicles."""
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if vehicle.owner_id and (not request.user.is_authenticated or (vehicle.owner_id != request.user.id and not request.user.is_staff)):
        raise Http404()
    return render(request, 'vehicles/vehicle_detail.html', {'vehicle': vehicle})


@login_required
def my_vehicle_list(request):
    return redirect("vehicles:create")


@login_required
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            try:
                vehicle.owner_name = request.user.profile.full_name  # type: ignore[attr-defined]
            except Exception:
                vehicle.owner_name = request.user.username
            vehicle.save()
            messages.success(request, "Vehicle added successfully.")
            return redirect("vehicles:list")
    else:
        form = VehicleForm()

    return render(request, "vehicles/vehicle_form.html", {"form": form, "mode": "create"})
