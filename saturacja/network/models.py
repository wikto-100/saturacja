from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department)
    # Optionally, store the currently selected department.
    current_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_users",
    )

    def __str__(self):
        return f"{self.user.username}"


class Customer(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    location = models.PointField()  # Latitude/longitude as a spatial point.
    city = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100, blank=True, null=True)
    street_no = models.CharField(max_length=50)
    local = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)


class Saturation(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional name or description for the area",
    )
    area = models.PolygonField(
        help_text="Geographic area for which saturation is measured"
    )
    center = models.PointField(
        null=True, blank=True, help_text="Center of the area, for marker display"
    )
    active_clients = models.PositiveIntegerField(
        default=0, help_text="Number of active clients in the area"
    )
    inactive_clients = models.PositiveIntegerField(
        default=0, help_text="Number of inactive clients in the area"
    )
    computed_at = models.DateTimeField(
        auto_now=True, help_text="The time when these measures were computed"
    )

    @property
    def saturation_ratio(self):
        total = self.active_clients + self.inactive_clients
        if total > 0:
            return self.active_clients / total
        return 0

    def __str__(self):
        return f"{self.name or 'Area'}: {self.active_clients} active, {self.inactive_clients} inactive"
