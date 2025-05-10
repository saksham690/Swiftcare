from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Doctor, Appointment, Response, helathcare_doctor

class DoctorAdminForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['password'] and not self.cleaned_data['password'].startswith('pbkdf2_sha256'):
            instance.password = make_password(self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm
    list_display = ('name', 'speciality', 'email', 'address', 'phone', 'experience', 'rating', 'rating_count', 'virtual_visit')
    list_filter = ('speciality', 'virtual_visit')
    search_fields = ('name', 'speciality', 'email', 'address')
    fieldsets = (
        (None, {
            'fields': ('name', 'speciality', 'email', 'password')
        }),
        ('Contact Info', {
            'fields': ('address', 'phone')
        }),
        ('Professional Info', {
            'fields': ('experience', 'rating', 'rating_count', 'virtual_visit', 'image_url', 'distance')
        }),
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone', 'dob')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('groups',)
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('phone', 'dob')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor_id', 'requested_date', 'status', 'new_date')
    list_filter = ('status',)
    search_fields = ('patient__first_name', 'patient__last_name')
    fieldsets = (
        (None, {
            'fields': ('patient', 'doctor_id', 'requested_date', 'status', 'new_date')
        }),
    )

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('status', 'new_date', 'appointment')
    search_fields = ('status',)
    fieldsets = (
        (None, {
            'fields': ('status', 'new_date', 'appointment')
        }),
    )

@admin.register(helathcare_doctor)
class HealthcareDoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality', 'email', 'address', 'phone', 'experience', 'rating', 'rating_count', 'virtual_visit')
    list_filter = ('speciality', 'virtual_visit')
    search_fields = ('name', 'speciality', 'email', 'address')