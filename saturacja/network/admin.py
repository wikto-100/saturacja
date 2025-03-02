from django.contrib import admin
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.forms.widgets import OSMWidget
from .models import Department, Customer, Saturation, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )

# Unregister the default User admin and register the new one.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Register the Department model.
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

# Customer Admin: Display key fields and override the PointField widget.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'street_name', 'street_no', 'phone', 'email', 'status', 'department')
    list_filter = ('status', 'department')
    search_fields = ('city', 'street_name', 'street_no', 'local', 'phone', 'email')
    formfield_overrides = {
        geomodels.PointField: {'widget': OSMWidget(attrs={
            'map_width': 800,
            'map_height': 500,
        })},
    }

# Saturation Admin: Display details about saturation measurements.
@admin.register(Saturation)
class SaturationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'active_clients', 'inactive_clients', 'computed_at')
    list_filter = ('department',)
    search_fields = ('name',)
