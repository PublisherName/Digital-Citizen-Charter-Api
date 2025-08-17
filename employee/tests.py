"""Tests for the Employee app."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from faker import Faker

from employee.forms import EmployeeForm
from employee.models import Employee
from organization.choices import PROVINCE_CHOICES
from organization.models import Department, Designation, Organization

User = get_user_model()
fake = Faker()


class EmployeeModelTest(TestCase):
    """Test Employee model properties and validation logic."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username=fake.user_name(), password=fake.password())

        self.organization = Organization.objects.create(
            user=self.user,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=32)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        self.department = Department.objects.create(
            organization=self.organization,
            name=f"{fake.word().title()} Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.company_email(),
        )

        self.designation_single = Designation.objects.create(
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=False,
        )

        self.designation_multiple = Designation.objects.create(
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=True,
        )

    def test_organization_property_returns_correct_organization(self):
        """Test that organization property returns the correct organization via designation."""
        employee = Employee.objects.create(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        self.assertEqual(employee.organization, self.organization)
        self.assertEqual(employee.organization.id, self.organization.id)
        self.assertEqual(employee.organization.name, self.organization.name)

    def test_department_property_returns_correct_department(self):
        """Test that department property returns the correct department via designation."""
        employee = Employee.objects.create(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        self.assertEqual(employee.department, self.department)
        self.assertEqual(employee.department.id, self.department.id)
        self.assertEqual(employee.department.name, self.department.name)

    def test_organization_property_returns_none_when_designation_is_none(self):
        """Test that organization property returns None when designation is None."""
        employee = Employee.objects.create(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        employee.designation = None
        self.assertIsNone(employee.organization)

    def test_department_property_returns_none_when_designation_is_none(self):
        """Test that department property returns None when designation is None."""
        employee = Employee.objects.create(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        employee.designation = None
        self.assertIsNone(employee.department)

    def test_validate_designation_allows_multiple_employees(self):
        """
        Test that validate_designation allows multiple employees for designations that allow it.
        """
        employee1 = Employee.objects.create(  # noqa: F841
            designation=self.designation_multiple,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )
        employee2 = Employee(
            designation=self.designation_multiple,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        try:
            employee2.validate_designation()
        except ValidationError:
            self.fail("validate_designation() raised ValidationError unexpectedly!")

    def test_validate_designation_prevents_multiple_employees(self):
        """
        Test that validate_designation prevents multiple employees for single-employee designations
        """
        employee1 = Employee.objects.create(  # noqa: F841
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )
        employee2 = Employee(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        with self.assertRaises(ValidationError) as context:
            employee2.validate_designation()

        self.assertIn("already been assigned", str(context.exception))
        self.assertIn(str(self.designation_single), str(context.exception))

    def test_validate_designation_allows_updating_existing_employee(self):
        """
        Test that validate_designation allows updating an existing employee with same designation.
        """
        employee = Employee.objects.create(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        employee.name = fake.name()
        try:
            employee.validate_designation()
        except ValidationError:
            self.fail(
                "validate_designation() raised ValidationError unexpectedly for existing employee!"
            )

    def test_model_clean_calls_validate_designation(self):
        """Test that model's clean() method calls validate_designation()."""
        employee1 = Employee.objects.create(  # noqa: F841
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        employee2 = Employee(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        with self.assertRaises(ValidationError):
            employee2.clean()

    def test_model_save_calls_full_clean(self):
        """Test that model's save() method calls full_clean() which includes validation."""
        employee1 = Employee.objects.create(  # noqa: F841
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        employee2 = Employee(
            designation=self.designation_single,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        with self.assertRaises(ValidationError):
            employee2.save()

    def test_model_save_functionality_with_new_structure(self):
        """
        Test that model save functionality works correctly with the new property-based structure.
        """
        employee_data = {
            "designation": self.designation_multiple,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "email": fake.email(),
            "is_available": True,
        }

        employee = Employee(**employee_data)
        employee.save()

        saved_employee = Employee.objects.get(pk=employee.pk)
        self.assertEqual(saved_employee.designation, self.designation_multiple)
        self.assertEqual(saved_employee.organization, self.organization)
        self.assertEqual(saved_employee.department, self.department)
        self.assertEqual(saved_employee.name, employee_data["name"])
        self.assertEqual(saved_employee.email, employee_data["email"])

    def test_model_update_functionality_with_new_structure(self):
        """
        Test that model update functionality works correctly with the new property-based structure.
        """
        employee = Employee.objects.create(
            designation=self.designation_multiple,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        new_name = fake.name()
        new_email = fake.email()
        employee.name = new_name
        employee.email = new_email
        employee.save()

        updated_employee = Employee.objects.get(pk=employee.pk)
        self.assertEqual(updated_employee.name, new_name)
        self.assertEqual(updated_employee.email, new_email)
        self.assertEqual(updated_employee.organization, self.organization)
        self.assertEqual(updated_employee.department, self.department)

    def test_properties_work_with_select_related(self):
        """
        Test that organization and department properties work efficiently with select_related.
        """
        employee = Employee.objects.create(
            designation=self.designation_multiple,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        employee_with_related = Employee.objects.select_related(
            "designation__department__organization"
        ).get(pk=employee.pk)

        self.assertEqual(employee_with_related.organization, self.organization)
        self.assertEqual(employee_with_related.department, self.department)

    def test_str_method_returns_employee_name(self):
        """Test that __str__ method returns the employee name."""
        employee_name = fake.name()
        employee = Employee.objects.create(
            designation=self.designation_multiple,
            name=employee_name,
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        self.assertEqual(str(employee), employee_name)


class EmployeeFormValidationTest(TestCase):
    """Test form validation for organization-department-designation consistency."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(username=fake.user_name(), password=fake.password())
        self.user2 = User.objects.create_user(username=fake.user_name(), password=fake.password())

        self.org1 = Organization.objects.create(
            user=self.user1,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=32)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )
        self.org2 = Organization.objects.create(
            user=self.user2,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=32)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        self.dept1_org1 = Department.objects.create(
            organization=self.org1,
            name=f"{fake.word().title()} Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.company_email(),
        )
        self.dept2_org1 = Department.objects.create(
            organization=self.org1,
            name=f"{fake.word().title()} Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.company_email(),
        )
        self.dept1_org2 = Department.objects.create(
            organization=self.org2,
            name=f"{fake.word().title()} Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.company_email(),
        )

        self.desig1_dept1_org1 = Designation.objects.create(
            department=self.dept1_org1,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=True,
        )
        self.desig2_dept1_org1 = Designation.objects.create(
            department=self.dept1_org1,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=True,
        )
        self.desig1_dept2_org1 = Designation.objects.create(
            department=self.dept2_org1,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=True,
        )
        self.desig1_dept1_org2 = Designation.objects.create(
            department=self.dept1_org2,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=True,
        )

    def test_valid_organization_department_designation_combination(self):
        """Test that valid combinations pass validation."""
        form_data = {
            "organization": self.org1.id,
            "department": self.dept1_org1.id,
            "designation": self.desig1_dept1_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_designation_wrong_department_validation(self):
        """Test validation fails when designation doesn't belong to selected department."""
        form_data = {
            "organization": self.org1.id,
            "department": self.dept1_org1.id,
            "designation": self.desig1_dept2_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The selected designation does not belong to the selected department", str(form.errors)
        )

    def test_department_wrong_organization_validation(self):
        """Test validation fails when department doesn't belong to selected organization."""
        form_data = {
            "organization": self.org1.id,
            "department": self.dept1_org2.id,
            "designation": self.desig1_dept1_org2.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The selected department does not belong to the selected organization",
            str(form.errors),
        )

    def test_designation_wrong_organization_validation(self):
        """
        Test validation fails when designation's organization doesn't match selected organization.
        """
        form_data = {
            "organization": self.org2.id,
            "department": self.dept1_org1.id,
            "designation": self.desig1_dept1_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The selected department does not belong to the selected organization",
            str(form.errors),
        )

    def test_all_mismatched_validation(self):
        """Test validation with completely mismatched organization, department, and designation."""
        form_data = {
            "organization": self.org2.id,
            "department": self.dept2_org1.id,
            "designation": self.desig1_dept1_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The selected department does not belong to the selected organization",
            str(form.errors),
        )

    def test_form_validation_with_missing_fields(self):
        """Test that validation only runs when all three fields are present."""
        form_data = {
            "department": self.dept1_org1.id,
            "designation": self.desig1_dept1_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization", form.errors)

    def test_form_validation_create_scenario(self):
        """Test form validation works for creating new employees."""
        form_data = {
            "organization": self.org1.id,
            "department": self.dept1_org1.id,
            "designation": self.desig1_dept1_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertTrue(form.is_valid())

        employee = form.save()
        self.assertEqual(employee.designation, self.desig1_dept1_org1)

    def test_form_validation_update_scenario(self):
        """Test form validation works for updating existing employees."""
        employee = Employee.objects.create(
            designation=self.desig1_dept1_org1,
            name=fake.name(),
            description=fake.text(max_nb_chars=100),
            contact_no=fake.phone_number()[:15],
        )

        form_data = {
            "organization": self.org1.id,
            "department": self.dept1_org1.id,
            "designation": self.desig2_dept1_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data, instance=employee)
        self.assertTrue(form.is_valid())

        form_data["designation"] = self.desig1_dept2_org1.id
        form = EmployeeForm(data=form_data, instance=employee)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The selected designation does not belong to the selected department", str(form.errors)
        )

    def test_error_message_content(self):
        """Test that error messages are user-friendly and informative."""
        form_data = {
            "organization": self.org1.id,
            "department": self.dept1_org1.id,
            "designation": self.desig1_dept2_org1.id,
            "name": fake.name(),
            "description": fake.text(max_nb_chars=100),
            "contact_no": fake.phone_number()[:15],
            "is_available": fake.boolean(),
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())

        error_message = str(form.errors)
        self.assertIn(self.desig1_dept2_org1.title, error_message)
        self.assertIn(self.dept2_org1.name, error_message)
        self.assertIn(self.dept1_org1.name, error_message)
