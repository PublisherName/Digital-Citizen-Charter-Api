"""This module contains the types for the organization app."""

import strawberry

from .models import Department, Designation, Organization, User


@strawberry.django.type(User)
class UserType:
    """
    UserType represents the user model.
    """

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool


@strawberry.django.type(Organization)
class OrganizationType:
    """
    OrganizationType represents the organization model.
    """

    id: int
    user: UserType
    name: str
    tag_line: str
    description: str
    province: str
    district: str
    municipality: str
    ward_no: str
    contact_no: str
    website: str
    logo: str
    is_active: bool


@strawberry.django.type(Department)
class DepartmentType:
    """
    DepartmentType represents the department model.
    """

    id: int
    name: str
    description: str
    contact_no: str
    email: str
    is_active: bool
    organization: OrganizationType


@strawberry.django.type(Designation)
class DesignationType:
    """
    DesignationType represents the designation model.
    """

    id: int
    title: str
    description: str
    priority: int
    allow_multiple_employees: bool
    organization: OrganizationType
    department: DepartmentType
