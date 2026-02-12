import math
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

from charging.models import ChargingStation
from service_center.models import ServiceCenter


def map_page(request):
    return render(request, "maps/map.html")


@dataclass(frozen=True)
class _CacheKey:
    lat: int
    lng: int
    radius_m: int


_OVERPASS_CACHE: Dict[_CacheKey, Tuple[datetime, List[Dict[str, Any]]]] = {}
_OVERPASS_CACHE_TTL = timedelta(seconds=60)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _format_overpass_address(tags: Dict[str, Any]) -> str:
    parts = []
    for key in ("addr:housenumber", "addr:street", "addr:city", "addr:state", "addr:postcode"):
        value = tags.get(key)
        if value:
            parts.append(str(value))
    return ", ".join(parts)


def _overpass_fetch_charging_stations(lat: float, lng: float, radius_m: int) -> List[Dict[str, Any]]:
    """
    Fetch nearby charging stations from OpenStreetMap via Overpass API.

    Returns a list of dicts with: name, latitude, longitude, address, operator, capacity, source.
    """
    key = _CacheKey(lat=int(lat * 1000), lng=int(lng * 1000), radius_m=radius_m)
    cached = _OVERPASS_CACHE.get(key)
    if cached and (datetime.utcnow() - cached[0]) <= _OVERPASS_CACHE_TTL:
        return cached[1]

    overpass_url = getattr(settings, "OVERPASS_URL", "https://overpass-api.de/api/interpreter")
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="charging_station"](around:{radius_m},{lat},{lng});
      way["amenity"="charging_station"](around:{radius_m},{lat},{lng});
      relation["amenity"="charging_station"](around:{radius_m},{lat},{lng});
    );
    out center tags;
    """.strip()

    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        overpass_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
    except Exception:
        return []

    try:
        parsed = json.loads(payload)
    except Exception:
        return []

    results: List[Dict[str, Any]] = []
    for el in parsed.get("elements", []):
        tags = el.get("tags") or {}
        el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
        el_lng = el.get("lon") or (el.get("center") or {}).get("lon")
        if el_lat is None or el_lng is None:
            continue

        address = _format_overpass_address(tags)
        if not address:
            address = tags.get("address") or tags.get("addr:full") or ""

        results.append(
            {
                "osm_id": f"{el.get('type','')}/{el.get('id','')}",
                "name": tags.get("name") or "Charging station",
                "address": address,
                "operator": tags.get("operator") or "",
                "capacity": tags.get("capacity") or tags.get("charge_points") or "",
                "latitude": float(el_lat),
                "longitude": float(el_lng),
                "source": "overpass",
            }
        )

    _OVERPASS_CACHE[key] = (datetime.utcnow(), results)
    return results


def api_nearby(request):
    try:
        lat = float(request.GET.get("lat", ""))
        lng = float(request.GET.get("lng", ""))
    except Exception:
        return JsonResponse({"error": "lat and lng are required"}, status=400)

    try:
        radius_km = float(request.GET.get("radius_km", "10"))
    except Exception:
        radius_km = 10.0
    radius_m = max(100, int(radius_km * 1000))

    include_all_db = str(request.GET.get("include_all_db", "")).strip() in {"1", "true", "yes"}
    overpass_stations = _overpass_fetch_charging_stations(lat, lng, radius_m)

    stations = []
    for s in ChargingStation.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
        d = _haversine_km(lat, lng, float(s.latitude), float(s.longitude))
        if include_all_db or d <= radius_km:
            stations.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address,
                    "latitude": float(s.latitude),
                    "longitude": float(s.longitude),
                    "available_slots": s.available_slots,
                    "plug_types": s.plug_types,
                    "distance_km": round(d, 2),
                    "source": "database",
                }
            )

    centers = []
    for c in ServiceCenter.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
        d = _haversine_km(lat, lng, float(c.latitude), float(c.longitude))
        if include_all_db or d <= radius_km:
            centers.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "address": c.address,
                    "latitude": float(c.latitude),
                    "longitude": float(c.longitude),
                    "phone": c.phone,
                    "distance_km": round(d, 2),
                    "source": "database",
                }
            )

    stations.sort(key=lambda x: x["distance_km"])
    centers.sort(key=lambda x: x["distance_km"])

    return JsonResponse(
        {
            "overpass_stations": overpass_stations,
            "stations": stations,
            "service_centers": centers,
            "radius_km": radius_km,
        }
    )

# Create your views here.
