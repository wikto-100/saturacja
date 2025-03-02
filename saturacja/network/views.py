import json
import requests
import csv, datetime
from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point, Polygon
from django.utils import timezone
from .models import Customer, Saturation
from saturacja.settings import SESSION_COOKIE_AGE
from .view_utils import (
    sanitize_label,
    parse_polygon_coords,
    is_polygon_too_large,
    build_overpass_query,
    parse_csv_file,
    customer_data_from_csv_row,
)


@login_required
def map_view(request):
    """
    Renders a map page with two GeoJSON datasets:
    one for active customers and one for inactive customers.
    """
    try:
        user_profile = request.user.userprofile
        dept_id = request.GET.get("dept_id")
        if dept_id:
            from .models import Department  # Import here if not already imported
            try:
                new_dept = Department.objects.get(id=dept_id)
                user_profile.current_department = new_dept
                user_profile.save()
            except Department.DoesNotExist:
                # Optionally, you can set a message if the dept isn't found.
                pass
        departments = user_profile.departments.all()
        current_dept = user_profile.current_department
        active_customers = Customer.objects.filter(
            department=current_dept, status="active"
        )
        inactive_customers = Customer.objects.filter(
            department=current_dept, status="inactive"
        )

        active_clients_geojson = serialize(
            "geojson",
            active_customers,
            geometry_field="location",
            fields=(
                "city",
                "street_name",
                "street_no",
                "local",
                "phone",
                "email",
                "status",
                "note",
                "created_at",
            ),
        )
        inactive_clients_geojson = serialize(
            "geojson",
            inactive_customers,
            geometry_field="location",
            fields=(
                "city",
                "street_name",
                "street_no",
                "status",
                "note",
                "phone",
                "email",
                "created_at",
            ),
        )
        login_time = request.user.last_login  # Use user.last_login as login time
        now = timezone.now()
        elapsed = (now - login_time).total_seconds() if login_time else 0
        remaining_seconds = SESSION_COOKIE_AGE - elapsed
        if remaining_seconds < 0:
            remaining_seconds = 0

        context = {
            "active_clients_geojson": active_clients_geojson,
            "inactive_clients_geojson": inactive_clients_geojson,
            "remaining_seconds": int(remaining_seconds),
            "departments": departments,
            "current_department": current_dept,
        }
        return render(request, "network/map.html", context)
    except Exception as e:
        return JsonResponse(
            {"error": f"Wystąpił nieoczekiwany błąd: {str(e)}"}, status=500
        )


@login_required
def get_inactive_addresses(request):
    """
    Receives a polygon in 'lat lon,lat lon,...' format via GET parameter "polygon",
    fetches addresses from the Overpass API, updates the database with new inactive addresses,
    and returns a GeoJSON of all inactive addresses within that polygon.
    """
    polygon_coords_str = request.GET.get("polygon")
    if not polygon_coords_str:
        return JsonResponse({"error": "Wymagany jest parametr polygon."}, status=400)

    coords = parse_polygon_coords(polygon_coords_str)
    if len(coords) < 3:
        return JsonResponse(
            {
                "error": "Nie podano wystarczającej liczby prawidłowych współrzędnych dla wielokąta."
            },
            status=400,
        )

    # Build poly_coords for GEOS Polygon (expects (lon, lat))
    poly_coords = [(lon, lat) for lat, lon in coords]
    if poly_coords[0] != poly_coords[-1]:
        poly_coords.append(poly_coords[0])
    try:
        polygon_geom = Polygon(poly_coords)
    except ValueError as e:
        return JsonResponse(
            {"error": f"Nieprawidłowa geometria wielokąta: {str(e)}"}, status=400
        )

    if is_polygon_too_large(coords, threshold=0.5):
        return JsonResponse(
            {"error": "Wybrany wielokąt jest zbyt duży. Proszę zawęzić wybór."},
            status=400,
        )

    poly_str = " ".join(f"{lat} {lon}" for lat, lon in coords)
    overpass_query = build_overpass_query(poly_str)

    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter", data=overpass_query, timeout=60
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse(
            {"error": f"Żądanie do Overpass API nie powiodło się: {str(e)}"}, status=502
        )

    try:
        osm_data = response.json()
    except json.JSONDecodeError as e:
        return JsonResponse(
            {"error": f"Nie udało się zdekodować odpowiedzi Overpass API: {str(e)}"},
            status=502,
        )

    elements = osm_data.get("elements", [])
    if len(elements) > 10000:
        return JsonResponse(
            {
                "error": "Zbyt wiele adresów do importu jednorazowo. Proszę zawęzić wielokąt."
            },
            status=400,
        )

    for element in elements:
        if element["type"] == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            center = element.get("center")
            if center:
                lat = center.get("lat")
                lon = center.get("lon")
            else:
                continue

        if lat is None or lon is None:
            continue

        tags = element.get("tags", {})
        print(tags)
        city = tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:place") or "??"
        street = tags.get("addr:street") or ""
        housenumber = tags.get("addr:housenumber") or ""


        city = city.strip()
        street = street.strip()
        housenumber = housenumber.strip()

        point = Point(lon, lat)
        if not polygon_geom.contains(point):
            continue

        if Customer.objects.filter(
            city__iexact=city, street_name__iexact=street, street_no__iexact=housenumber
        ).exists():
            continue
        current_dept = request.user.userprofile.current_department
        Customer.objects.create(
            department=current_dept,
            location=point,
            city=city,
            street_name=street,
            street_no=housenumber,
            local="",
            phone="",
            email="",
            status="inactive",
        )

    inactive_customers = Customer.objects.filter(
        department=current_dept, status="inactive", location__within=polygon_geom
    )
    features = []
    for cust in inactive_customers:
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [cust.location.x, cust.location.y],
                },
                "properties": {
                    "city": cust.city,
                    "street_name": cust.street_name,
                    "street_no": cust.street_no,
                    "status": cust.status,
                    "note": cust.note,
                    "phone": cust.phone,
                    "email": cust.email,
                    "created_at": cust.created_at.strftime("%Y-%m-%d %H:%M"),
                },
            }
        )
    geojson = {"type": "FeatureCollection", "features": features}
    return JsonResponse(geojson)


@login_required
def delete_inactive_addresses(request):
    polygon_coords_str = request.GET.get("polygon")
    if not polygon_coords_str:
        return JsonResponse({"error": "Wymagany jest parametr polygon."}, status=400)

    coords = parse_polygon_coords(polygon_coords_str)
    if len(coords) < 3:
        return JsonResponse(
            {
                "error": "Nie podano wystarczającej liczby prawidłowych współrzędnych dla wielokąta."
            },
            status=400,
        )

    poly_coords = [(lon, lat) for lat, lon in coords]
    if poly_coords[0] != poly_coords[-1]:
        poly_coords.append(poly_coords[0])
    try:
        polygon_geom = Polygon(poly_coords)
    except ValueError as e:
        return JsonResponse(
            {"error": f"Nieprawidłowa geometria wielokąta: {str(e)}"}, status=400
        )

    current_dept = request.user.userprofile.current_department
    qs = Customer.objects.filter(
        department=current_dept, status="inactive", location__within=polygon_geom
    )

    count_deleted = qs.count()
    qs.delete()

    return JsonResponse({"deleted": count_deleted})


@csrf_exempt
@login_required
def update_client(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Nieprawidłowa metoda; dozwolone są tylko żądania POST."},
            status=405,
        )
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Nieprawidłowy JSON."}, status=400)
    client_id = data.get("id")
    if not client_id:
        return JsonResponse({"error": "Brak identyfikatora klienta."}, status=400)

    current_dept = request.user.userprofile.current_department
    try:
        client = Customer.objects.get(id=client_id, department=current_dept)
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Klient nie został znaleziony."}, status=404)
    client.status = data.get("status", client.status)
    client.city = data.get("city", client.city)
    client.street_name = data.get("street_name", client.street_name)
    client.street_no = data.get("street_no", client.street_no)
    client.local = data.get("local", client.local)
    client.phone = data.get("phone", client.phone)
    client.email = data.get("email", client.email)
    client.note = data.get("note", client.note)
    client.save()
    return JsonResponse(
        {
            "success": True,
            "client": {
                "id": client.id,
                "status": client.status,
                "city": client.city,
                "street_name": client.street_name,
                "street_no": client.street_no,
                "local": client.local,
                "phone": client.phone,
                "email": client.email,
                "note": client.note,
                "created_at": client.created_at.strftime("%Y-%m-%d %H:%M"),
            },
        }
    )


@csrf_exempt
@login_required
def import_clients(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Nieprawidłowa metoda; dozwolone są tylko żądania POST."},
            status=405,
        )
    if "file" not in request.FILES:
        return JsonResponse({"error": "Nie przesłano pliku."}, status=400)
    csv_file = request.FILES["file"]
    if not csv_file.name.lower().endswith(".csv"):
        return JsonResponse(
            {"error": "Przesłany plik nie jest plikiem CSV."}, status=400
        )
    try:
        reader = parse_csv_file(csv_file, encoding="cp1250", delimiter=";")
    except Exception as e:
        return JsonResponse(
            {"error": f"Błąd przy odczycie pliku CSV: {str(e)}"}, status=400
        )
    imported_count = 0
    for row in reader:
        try:
            data = customer_data_from_csv_row(row)
            if data is None:
                continue
        except Exception:
            continue
        current_dept = request.user.userprofile.current_department
        existing = Customer.objects.filter(
            department=current_dept,
            city__iexact=data["city"],
            street_name__iexact=data["street_name"],
            street_no__iexact=data["street_no"],
            local__iexact=data["local"],
        ).first()
        if existing:
            existing.location = data["location"]
            existing.phone = data["phone"]
            existing.email = data["email"]
            existing.note = data["note"]
            existing.status = "active"
            existing.save()
            imported_count += 1
        else:
            # Ensure the department is assigned when creating a new record.
            Customer.objects.create(department=current_dept, **data)
            imported_count += 1
    return JsonResponse({"success": True, "imported_count": imported_count})


@csrf_exempt
@login_required
def export_clients(request):
    city = request.GET.get("city", "").strip()
    street = request.GET.get("street", "").strip()
    status = request.GET.get("status", "both").strip()

    current_dept = request.user.userprofile.current_department
    qs = Customer.objects.filter(department=current_dept)

    if status == "active":
        qs = qs.filter(status="active")
    elif status == "inactive":
        qs = qs.filter(status="inactive")

    if city:
        qs = qs.filter(city__icontains=city)
    if street:
        qs = qs.filter(street_name__icontains=street)

    city_label = sanitize_label(city) if city else "Wszystkie"
    street_label = sanitize_label(street) if street else "wszystkie"

    date_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"Klienci_{city_label}_{street_label}_{date_str}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Miejscowość",
            "Ulica",
            "Nr. domu",
            "Mieszkanie",
            "Telefon",
            "E-mail",
            "Stan",
            "Notatka",
        ]
    )
    for client in qs:
        writer.writerow(
            [
                client.city,
                client.street_name,
                client.street_no,
                client.local,
                client.phone,
                client.email,
                "Aktywny" if client.status == "active" else "Nieaktywny",
                client.note,
                client.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return response


@login_required
def measure_saturation(request):
    """
    Receives a polygon in 'lat lon,lat lon,...' format via GET parameter "polygon",
    counts active and inactive customers within the polygon,
    computes the saturation ratio, saves a Saturation record (including the polygon's center),
    and returns the counts, ratio, center, and saturation record id.
    """
    polygon_coords_str = request.GET.get("polygon")
    if not polygon_coords_str:
        return JsonResponse({"error": "Wymagany jest parametr polygon."}, status=400)

    coords = parse_polygon_coords(polygon_coords_str)
    if len(coords) < 3:
        return JsonResponse(
            {"error": "Nie podano wystarczającej liczby współrzędnych."}, status=400
        )

    # Build poly_coords for GEOS Polygon (expects (lon, lat))
    poly_coords = [(lon, lat) for lat, lon in coords]
    if poly_coords[0] != poly_coords[-1]:
        poly_coords.append(poly_coords[0])
    try:
        polygon_geom = Polygon(poly_coords)
    except ValueError as e:
        return JsonResponse(
            {"error": f"Nieprawidłowa geometria wielokąta: {str(e)}"}, status=400
        )
    current_dept = request.user.userprofile.current_department
    active_count = Customer.objects.filter(
        department=current_dept, status="active", location__within=polygon_geom
    ).count()
    inactive_count = Customer.objects.filter(
        department=current_dept, status="inactive", location__within=polygon_geom
    ).count()
    total = active_count + inactive_count
    ratio = (active_count / total) if total > 0 else 0

    # Compute the center using GEOS centroid
    center_point = polygon_geom.centroid
    center = {"lon": center_point.x, "lat": center_point.y}

    # Save saturation data to the database including the center.
    saturation = Saturation.objects.create(
        department=current_dept,
        area=polygon_geom,
        center=center_point,
        active_clients=active_count,
        inactive_clients=inactive_count,
        name=f"Pomiar saturacji {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
    )
    computed_at_local = timezone.localtime().strftime("%Y-%m-%d %H:%M")
    return JsonResponse(
        {
            "active": active_count,
            "inactive": inactive_count,
            "ratio": round(ratio, 2),
            "center": center,
            "saturation_id": saturation.id,
            "computed_at": computed_at_local,
        }
    )


@login_required
def saturation_markers(request):
    """
    Returns a GeoJSON FeatureCollection of Saturation records,
    using the center field for the marker location.
    """
    current_dept = request.user.userprofile.current_department
    saturations = Saturation.objects.filter(department=current_dept)

    features = []
    for s in saturations:
        computed_at_local = timezone.localtime(s.computed_at).strftime("%Y-%m-%d %H:%M")
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [s.center.x, s.center.y],
                },
                "properties": {
                    "id": s.id,
                    "active": s.active_clients,
                    "inactive": s.inactive_clients,
                    "ratio": round(s.saturation_ratio, 2),
                    "computed_at": computed_at_local,
                    "name": s.name or "",
                },
            }
        )
    geojson = {"type": "FeatureCollection", "features": features}
    return JsonResponse(geojson)


@csrf_exempt
@login_required
def delete_saturation(request):
    """
    Expects a POST request with JSON body: { "id": <saturation_record_id> }.
    Deletes the corresponding Saturation record.
    """
    if request.method != "POST":
        return JsonResponse(
            {"error": "Nieprawidłowa metoda; dozwolone są tylko żądania POST."},
            status=405,
        )
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Nieprawidłowy JSON."}, status=400)
    saturation_id = data.get("id")
    if not saturation_id:
        return JsonResponse({"error": "Brak identyfikatora pomiaru."}, status=400)
    try:
        current_dept = request.user.userprofile.current_department
        saturation = Saturation.objects.get(department=current_dept, id=saturation_id)
        saturation.delete()
        return JsonResponse({"success": True})
    except Saturation.DoesNotExist:
        return JsonResponse({"error": "Pomiar nie został znaleziony."}, status=404)
