""" This file contains the views for the organization app. """

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Department, Designation


@login_required
def department_for_organization(request):
    """This function returns the department list for the organization."""

    if (
        "organization_id" in request.GET
        and request.GET["organization_id"] != ""
        and request.GET["organization_id"].isdigit()
    ):
        department_list = Department.objects.filter(
            organization=request.GET["organization_id"]
        )
        return JsonResponse(
            {
                "data": [
                    {"id": department.id, "name": department.name}
                    for department in department_list
                ]
            }
        )
    else:
        return JsonResponse({"data": []})


@login_required
def get_designation_for_department(request):
    """This function returns the designation list for the department."""

    if (
        "department_id" in request.GET
        and request.GET["department_id"] != ""
        and request.GET["department_id"].isdigit()
    ):
        designation_list = Designation.objects.filter(
            department=request.GET["department_id"]
        )
        return JsonResponse(
            {
                "data": [
                    {"id": designation.id, "name": designation.title}
                    for designation in designation_list
                ]
            }
        )
    else:
        return JsonResponse({"data": []})
