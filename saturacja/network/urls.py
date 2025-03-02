from django.urls import path
from .views import (
    map_view,
    get_inactive_addresses,
    delete_inactive_addresses,
    update_client,
    import_clients,
    export_clients,
    measure_saturation,
    saturation_markers,
    delete_saturation,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", map_view, name="map"),
    path("api/inactive_addresses", get_inactive_addresses, name="inactive_addresses"),
    path(
        "api/delete_inactive_addresses",
        delete_inactive_addresses,
        name="delete_inactive_addresses",
    ),
    path("api/update_client", update_client, name="update_client"),
    path("api/import_clients", import_clients, name="import_clients"),
    path("api/export_clients", export_clients, name="export_clients"),
    path("api/measure_saturation", measure_saturation, name="measure_saturation"),
    path('api/saturation_markers', saturation_markers, name='saturation_markers'),
    path('api/delete_saturation', delete_saturation, name='delete_saturation'),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="network/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
