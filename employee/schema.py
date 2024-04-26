"""This module contains the schema for the employee app."""

from typing import List, Optional

import strawberry

from .models import Employee
from .types import EmployeeType


@strawberry.type
class Query:
    """Query type for the Organization app."""

    @strawberry.field
    def get_employees_by_id(self, employee_id: Optional[int] = None) -> List[EmployeeType]:
        """
        Fetches all the organizations.
        """
        if employee_id:
            return Employee.objects.filter(id=employee_id)
        return Employee.objects.all()

    @strawberry.field
    def get_employees_by_department(self, department_id: int) -> List[EmployeeType]:
        """
        Fetches all the employees of a department.
        """
        return Employee.objects.filter(department_id=department_id)

    @strawberry.field
    def get_employees_by_organization(self, organization_id: int) -> List[EmployeeType]:
        """
        Fetches all the employees of an organization.
        """
        return Employee.objects.filter(organization_id=organization_id)


schema = strawberry.Schema(query=Query)
