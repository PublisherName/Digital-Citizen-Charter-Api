""" This module contains the schema for the organization app. """

from typing import List, Optional
import strawberry

from .models import Organization, Department, Designation
from .types import OrganizationType, DepartmentType, DesignationType


@strawberry.type
class Query:
    """Query type for the Organization app."""

    @strawberry.field
    def organizations(
        self, organization_id: Optional[int] = None
    ) -> List[OrganizationType]:
        """
        Fetches all the organizations.
        """
        if organization_id:
            return Organization.objects.filter(id=organization_id)
        return Organization.objects.all()

    @strawberry.field
    def departments(self, department_id: Optional[int] = None) -> List[DepartmentType]:
        """
        Fetches all the departments.
        """
        if department_id:
            return Department.objects.filter(id=department_id)
        return Department.objects.all()

    @strawberry.field
    def designations(
        self, designation_id: Optional[int] = None
    ) -> List[DesignationType]:
        """
        Fetches all the designations.
        """
        if designation_id:
            return Designation.objects.filter(id=designation_id)
        return Designation.objects.all()


schema = strawberry.Schema(query=Query)
