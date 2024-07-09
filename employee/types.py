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
    description: str
    organization: OrganizationType
    department: DepartmentType
    designation: DesignationType

    @strawberry.field
    def profile_picture(self, info) -> str:
        """
        Returns the profile picture URL. If the employee does not have a profile picture,
        returns a URL to the default profile picture.
        """
        if self.profile_picture:
            return self.profile_picture.url
        else:
            return "/static/images/default_profile_picture.jpg"
