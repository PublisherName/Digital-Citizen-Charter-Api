""" This module contains the schema for the employee app. """

from typing import List, Optional
import strawberry

from .models import Employee
from .types import EmployeeType


@strawberry.type
class Query:
    """Query type for the Organization app."""

    @strawberry.field
    def employees(self, employee_id: Optional[int] = None) -> List[EmployeeType]:
        """
        Fetches all the organizations.
        """
        if employee_id:
            return Employee.objects.filter(id=employee_id)
        return Employee.objects.all()


schema = strawberry.Schema(query=Query)
