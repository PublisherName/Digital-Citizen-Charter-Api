""" This module contains the schema for the root app. """

import strawberry

from organization.schema import Query as OrganizationQuery
from employee.schema import Query as EmployeeQuery


@strawberry.type
class Query(OrganizationQuery, EmployeeQuery):
    """Query type for the root app."""


schema = strawberry.Schema(query=Query)
