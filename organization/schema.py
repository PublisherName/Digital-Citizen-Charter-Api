""" This module contains the schema for the organization app. """

from typing import List, Optional
import strawberry

from .models import Organization, Department, Designation
from .types import OrganizationType, DepartmentType, DesignationType


@strawberry.type
class Query:
    """Query type for the Organization app."""

    @strawberry.field
    def get_organizations_by_id(
        self, organization_id: Optional[int] = None
    ) -> List[OrganizationType]:
        """
        Fetches all the organizations.
        """
        if organization_id:
            return Organization.objects.filter(id=organization_id)
        return Organization.objects.all()

    @strawberry.field
    def get_departments_by_id(
        self, department_id: Optional[int] = None
    ) -> List[DepartmentType]:
        """
        Fetches all the departments.
        """
        if department_id:
            return Department.objects.filter(id=department_id)
        return Department.objects.all()

    @strawberry.field
    def get_departments_by_organization(
        self, organization_id: int
    ) -> List[DepartmentType]:
        """
        Fetches all the departments of an organization.
        """
        return Department.objects.filter(organization_id=organization_id)

    @strawberry.field
    def get_designations_by_id(
        self, designation_id: Optional[int] = None
    ) -> List[DesignationType]:
        """
        Fetches all the designations.
        """
        if designation_id:
            return Designation.objects.filter(id=designation_id)
        return Designation.objects.all()

    @strawberry.field
    def get_designations_by_organization(
        self, organization_id: int
    ) -> List[DesignationType]:
        """
        Fetches all the designations of an organization.
        """
        return Designation.objects.filter(organization_id=organization_id)

    @strawberry.field
    def get_designations_by_department(
        self, department_id: int
    ) -> List[DesignationType]:
        """
        Fetches all the designations of a department.
        """
        return Designation.objects.filter(department_id=department_id)


schema = strawberry.Schema(query=Query)
