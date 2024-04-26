"""This file contains the URL patterns for the organization app."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "get_department_for_organization/",
        views.department_for_organization,
        name="department-for-organization",
    ),
    path(
        "get_designation_for_department/",
        views.get_designation_for_department,
        name="designation-for-department",
    ),
]
