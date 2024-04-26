"""This module contains the types for the employee app."""

import strawberry

from organization.types import DepartmentType, DesignationType, OrganizationType

from .models import Employee


@strawberry.django.type(Employee)
class EmployeeType:
    """
    EmployeeType represents the employee model.
    """

    id: int
    name: str
    email: str
    contact_no: str
    profile_picture: str
    organization: OrganizationType
    department: DepartmentType
    designation: DesignationType
