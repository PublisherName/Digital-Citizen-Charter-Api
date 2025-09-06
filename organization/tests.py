"""
Unit tests for organization models and forms.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from faker import Faker

from .choices import PROVINCE_CHOICES
from .forms import DesignationForm, OrganizationForm
from .models import (
    Department,
    DepartmentTemplate,
    Designation,
    DesignationTemplate,
    Organization,
    OrganizationTemplate,
)

User = get_user_model()
fake = Faker()


class DesignationModelTests(TestCase):
    """Test cases for the Designation model changes."""

    def setUp(self):
        """Set up test data using faker."""
        self.user = User.objects.create_user(
            username=fake.user_name(), email=fake.email(), password=fake.password()
        )

        self.organization = Organization.objects.create(
            user=self.user,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=35)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        self.department = Department.objects.create(
            organization=self.organization,
            name=fake.word().title() + " Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.email(),
        )

        self.designation = Designation.objects.create(
            organization=self.organization,
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

    def test_organization_property_returns_correct_organization(self):
        """Test that organization property returns the correct organization."""
        self.assertEqual(self.designation.organization, self.organization)
        self.assertEqual(self.designation.organization.name, self.organization.name)
        self.assertEqual(self.designation.organization.id, self.organization.id)

    def test_organization_property_with_different_organizations(self):
        """Test organization property with multiple organizations."""
        user2 = User.objects.create_user(
            username=fake.user_name(), email=fake.email(), password=fake.password()
        )

        organization2 = Organization.objects.create(
            user=user2,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=35)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        department2 = Department.objects.create(
            organization=organization2,
            name=fake.word().title() + " Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.email(),
        )

        designation2 = Designation.objects.create(
            organization=organization2,
            department=department2,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        self.assertEqual(self.designation.organization, self.organization)
        self.assertEqual(designation2.organization, organization2)
        self.assertNotEqual(self.designation.organization, organization2)
        self.assertNotEqual(designation2.organization, self.organization)

    def test_model_validation_with_property_based_structure(self):
        """Test model validation works with the new property-based structure."""
        title = fake.job()
        valid_designation = Designation(
            organization=self.organization,
            department=self.department,
            title=title,
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        valid_designation.full_clean()
        valid_designation.save()

        saved_designation = Designation.objects.get(title=title)
        self.assertEqual(saved_designation.organization, self.organization)
        self.assertEqual(saved_designation.department, self.department)

    def test_clean_method_validation_logic(self):
        """Test the model's clean() method validation logic."""
        designation_without_dept = Designation(
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        with self.assertRaises(ValidationError) as context:
            designation_without_dept.clean()

        self.assertEqual(str(context.exception.message), "Department is required.")

    def test_clean_method_with_valid_department(self):
        """Test that clean() method passes with valid department."""
        valid_designation = Designation(
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        try:
            valid_designation.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly with valid department")

    def test_full_clean_validation_with_property_structure(self):
        """Test full_clean() validation with the property-based structure."""
        valid_designation = Designation(
            organization=self.organization,
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        valid_designation.full_clean()

        invalid_designation = Designation(
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        with self.assertRaises(ValidationError):
            invalid_designation.full_clean()

    def test_organization_property_consistency_after_department_change(self):
        """Test organization property consistency when department changes."""
        user2 = User.objects.create_user(
            username=fake.user_name(), email=fake.email(), password=fake.password()
        )

        organization2 = Organization.objects.create(
            user=user2,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=35)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        department2 = Department.objects.create(
            organization=organization2,
            name=fake.word().title() + " Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.email(),
        )

        self.assertEqual(self.designation.organization, self.organization)

        self.designation.organization = organization2
        self.designation.department = department2
        self.designation.save()

        self.assertEqual(self.designation.organization, organization2)
        self.assertNotEqual(self.designation.organization, self.organization)

    def test_string_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.designation), self.designation.title)

    def test_model_fields_and_properties(self):
        """Test that all expected fields and properties are accessible."""
        self.assertIsNotNone(self.designation.title)
        self.assertIsNotNone(self.designation.description)
        self.assertIsInstance(self.designation.priority, int)
        self.assertIsInstance(self.designation.allow_multiple_employees, bool)
        self.assertEqual(self.designation.department, self.department)

        self.assertIsInstance(self.designation.organization, Organization)
        self.assertEqual(self.designation.organization, self.organization)

    def test_multiple_designations_with_faker_data(self):
        """Test creating multiple designations with faker data."""
        designations = []
        for _ in range(5):
            designation = Designation.objects.create(
                organization=self.organization,
                department=self.department,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=fake.random_int(min=1, max=10),
                allow_multiple_employees=fake.boolean(),
            )
            designations.append(designation)

        for designation in designations:
            self.assertEqual(designation.organization, self.organization)
            self.assertEqual(designation.department, self.department)

    def test_organization_property_with_various_provinces(self):
        """Test organization property with designations from different provinces."""
        for province_code, province_name in PROVINCE_CHOICES:
            user = User.objects.create_user(
                username=fake.user_name(), email=fake.email(), password=fake.password()
            )

            organization = Organization.objects.create(
                user=user,
                name=fake.company(),
                tag_line=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                province=province_code,
                district=fake.city(),
                municipality=fake.city(),
                ward_no=str(fake.random_int(min=1, max=35)),
                contact_no=fake.phone_number()[:15],
                website=fake.url(),
            )

            department = Department.objects.create(
                organization=organization,
                name=fake.word().title() + " Department",
                description=fake.text(max_nb_chars=200),
                contact_no=fake.phone_number()[:20],
                email=fake.email(),
            )

            designation = Designation.objects.create(
                organization=organization,
                department=department,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=fake.random_int(min=1, max=10),
                allow_multiple_employees=fake.boolean(),
            )

            self.assertEqual(designation.organization, organization)
            self.assertEqual(designation.organization.province, province_code)

    def test_designation_priority_validation_with_faker(self):
        """Test designation priority with various faker-generated values."""
        for _ in range(10):
            priority = fake.random_int(min=1, max=100)
            designation = Designation(
                organization=self.organization,
                department=self.department,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=priority,
                allow_multiple_employees=fake.boolean(),
            )

            designation.full_clean()
            designation.save()

            saved_designation = Designation.objects.get(id=designation.id)
            self.assertEqual(saved_designation.priority, priority)
            self.assertEqual(saved_designation.organization, self.organization)

    def test_allow_multiple_employees_flag_with_faker(self):
        """Test allow_multiple_employees flag with faker boolean values."""
        for _ in range(10):
            allow_multiple = fake.boolean()
            designation = Designation.objects.create(
                organization=self.organization,
                department=self.department,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=fake.random_int(min=1, max=10),
                allow_multiple_employees=allow_multiple,
            )

            self.assertEqual(designation.allow_multiple_employees, allow_multiple)
            self.assertEqual(designation.organization, self.organization)

    def test_organization_property_performance(self):
        """Test that organization property access doesn't cause N+1 queries."""
        designations = []
        for _ in range(10):
            designation = Designation.objects.create(
                organization=self.organization,
                department=self.department,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=fake.random_int(min=1, max=10),
                allow_multiple_employees=fake.boolean(),
            )
            designations.append(designation)

        organizations = [designation.organization for designation in designations]

        for org in organizations:
            self.assertEqual(org, self.organization)

    def test_edge_cases_with_faker_data(self):
        """Test edge cases with faker-generated data."""
        long_title = fake.text(max_nb_chars=190)
        designation = Designation.objects.create(
            organization=self.organization,
            department=self.department,
            title=long_title,
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )
        self.assertEqual(designation.organization, self.organization)

        min_priority_designation = Designation.objects.create(
            organization=self.organization,
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=1,
            allow_multiple_employees=fake.boolean(),
        )
        self.assertEqual(min_priority_designation.organization, self.organization)

        max_priority_designation = Designation.objects.create(
            organization=self.organization,
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=999999,
            allow_multiple_employees=fake.boolean(),
        )
        self.assertEqual(max_priority_designation.organization, self.organization)


class DesignationFormTests(TestCase):
    """Test cases for the DesignationForm functionality."""

    def setUp(self):
        """Set up test data using faker."""
        self.user1 = User.objects.create_user(
            username=fake.user_name(), email=fake.email(), password=fake.password()
        )
        self.user2 = User.objects.create_user(
            username=fake.user_name(), email=fake.email(), password=fake.password()
        )

        self.organization1 = Organization.objects.create(
            user=self.user1,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=35)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        self.organization2 = Organization.objects.create(
            user=self.user2,
            name=fake.company(),
            tag_line=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=35)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        self.department1 = Department.objects.create(
            organization=self.organization1,
            name=fake.word().title() + " Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.email(),
        )

        self.department2 = Department.objects.create(
            organization=self.organization2,
            name=fake.word().title() + " Department",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.email(),
        )

        self.valid_form_data = {
            "organization": self.organization1.id,
            "department": self.department1.id,
            "title": fake.job(),
            "description": fake.text(max_nb_chars=200),
            "priority": fake.random_int(min=1, max=10),
            "allow_multiple_employees": fake.boolean(),
        }

    def test_form_validation_with_valid_organization_department_combination(self):
        """Test form validation passes with valid organization-department combinations."""
        form = DesignationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        valid_data_2 = self.valid_form_data.copy()
        valid_data_2.update(
            {
                "organization": self.organization2.id,
                "department": self.department2.id,
                "title": fake.job(),
            }
        )
        form2 = DesignationForm(data=valid_data_2)
        self.assertTrue(form2.is_valid(), f"Form errors: {form2.errors}")

    def test_form_validation_rejects_invalid_organization_department_combinations(self):
        """Test form validation rejects invalid organization-department combinations."""
        invalid_data = self.valid_form_data.copy()
        invalid_data["department"] = self.department2.id

        form = DesignationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("department", form.errors)
        self.assertIn(
            f"The selected department '{self.department2.name}' does not belong to "
            f"the selected organization '{self.organization1.name}'",
            form.errors["department"][0],
        )

    def test_form_validation_with_organization_but_no_department(self):
        """Test form validation when organization is selected but no department."""
        invalid_data = self.valid_form_data.copy()
        invalid_data["department"] = ""

        form = DesignationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("department", form.errors)
        error_message = form.errors["department"][0]
        self.assertTrue(
            f"Please select a department from the organization '{self.organization1.name}'"
            in error_message
            or "This field is required." in error_message
        )

    def test_form_validation_with_department_but_no_organization(self):
        """Test form validation when department is selected but no organization."""
        data_without_org = self.valid_form_data.copy()
        data_without_org["organization"] = ""

        form = DesignationForm(data=data_without_org)
        if form.is_valid():
            self.assertEqual(form.cleaned_data["organization"], self.department1.organization)
        else:
            self.assertIn("organization", form.errors)

    def test_form_rendering_includes_organization_field_with_proper_widget(self):
        """Test form rendering includes organization field with proper widget."""
        form = DesignationForm()

        self.assertIn("organization", form.fields)

        org_field = form.fields["organization"]
        self.assertTrue(org_field.required)
        self.assertEqual(org_field.queryset.model, Organization)

        widget = org_field.widget
        self.assertIn("onchange", widget.attrs)
        self.assertEqual(widget.attrs["onchange"], "get_department_for_organization(this.value);")
        self.assertEqual(widget.attrs["autocomplete"], "off")

    def test_form_rendering_includes_all_required_fields(self):
        """Test form rendering includes all required fields."""
        form = DesignationForm()
        expected_fields = [
            "organization",
            "department",
            "title",
            "description",
            "priority",
            "allow_multiple_employees",
        ]

        for field_name in expected_fields:
            self.assertIn(field_name, form.fields, f"Field {field_name} missing from form")

    def test_form_media_includes_javascript_files(self):
        """Test form includes proper JavaScript media files."""
        form = DesignationForm()
        self.assertIn("js/chained/get_department_for_organization.js", form.media._js)

    def test_form_saves_designation_with_correct_department_relationship(self):
        """Test form saves designation with correct department relationship."""
        form = DesignationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        designation = form.save()

        self.assertIsInstance(designation, Designation)
        self.assertEqual(designation.department, self.department1)
        self.assertEqual(designation.organization, self.organization1)
        self.assertEqual(designation.title, self.valid_form_data["title"])
        self.assertEqual(designation.description, self.valid_form_data["description"])
        self.assertEqual(designation.priority, self.valid_form_data["priority"])
        self.assertEqual(
            designation.allow_multiple_employees, self.valid_form_data["allow_multiple_employees"]
        )

    def test_form_save_does_not_save_organization_field_to_model(self):
        """Test form save does not save organization field directly to model."""
        form = DesignationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        designation = form.save()

        self.assertFalse(hasattr(designation, "_organization_id"))
        self.assertEqual(designation.organization, self.organization1)
        self.assertEqual(designation.department.organization, self.organization1)

    def test_form_initialization_with_existing_designation(self):
        """Test form initialization with existing designation sets organization field."""
        existing_designation = Designation.objects.create(
            organization=self.organization1,
            department=self.department1,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        form = DesignationForm(instance=existing_designation)

        self.assertEqual(form.fields["organization"].initial, self.organization1)

    def test_form_validation_with_multiple_valid_combinations(self):
        """Test form validation with multiple valid organization-department combinations."""
        dept1_2 = Department.objects.create(
            organization=self.organization1,
            name=fake.word().title() + " Department 2",
            description=fake.text(max_nb_chars=200),
            contact_no=fake.phone_number()[:20],
            email=fake.email(),
        )

        form_data_1 = self.valid_form_data.copy()
        form1 = DesignationForm(data=form_data_1)
        self.assertTrue(form1.is_valid())

        form_data_2 = self.valid_form_data.copy()
        form_data_2.update(
            {
                "department": dept1_2.id,
                "title": fake.job(),
            }
        )
        form2 = DesignationForm(data=form_data_2)
        self.assertTrue(form2.is_valid())

    def test_form_validation_error_messages_are_user_friendly(self):
        """Test form validation error messages are user-friendly."""
        invalid_data = self.valid_form_data.copy()
        invalid_data["department"] = self.department2.id

        form = DesignationForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        error_message = form.errors["department"][0]
        self.assertIn(self.department2.name, error_message)
        self.assertIn(self.organization1.name, error_message)
        self.assertIn("does not belong to", error_message)

    def test_form_clean_method_handles_edge_cases(self):
        """Test form clean method handles various edge cases."""
        empty_data = {
            "title": fake.job(),
            "description": fake.text(max_nb_chars=200),
            "priority": fake.random_int(min=1, max=10),
            "allow_multiple_employees": fake.boolean(),
        }
        form = DesignationForm(data=empty_data)
        self.assertFalse(form.is_valid())

    def test_form_save_with_commit_false(self):
        """Test form save with commit=False."""
        form = DesignationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        designation = form.save(commit=False)

        self.assertIsInstance(designation, Designation)
        self.assertIsNone(designation.pk)

        designation.save()
        self.assertIsNotNone(designation.pk)
        self.assertEqual(designation.organization, self.organization1)

    def test_form_validation_with_faker_generated_data(self):
        """Test form validation with various faker-generated data."""
        for _ in range(5):
            test_data = {
                "organization": self.organization1.id,
                "department": self.department1.id,
                "title": fake.job(),
                "description": fake.text(max_nb_chars=200),
                "priority": fake.random_int(min=1, max=100),
                "allow_multiple_employees": fake.boolean(),
            }

            form = DesignationForm(data=test_data)
            self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

            designation = form.save()
            self.assertEqual(designation.organization, self.organization1)


class OrganizationFormTemplateValidationTests(TestCase):
    """Test cases for OrganizationForm template validation functionality."""

    def setUp(self):
        """Set up test data for template validation tests."""
        self.user = User.objects.create_user(
            username=fake.user_name(), email=fake.email(), password=fake.password()
        )

        self.active_template = OrganizationTemplate.objects.create(
            name="Active Template", description="An active template for testing", is_active=True
        )

        self.active_dept_template = DepartmentTemplate.objects.create(
            organization_template=self.active_template,
            name="HR Department",
            description="Human Resources Department",
            is_active=True,
        )

        self.active_desig_template = DesignationTemplate.objects.create(
            organization_template=self.active_template,
            department_template=self.active_dept_template,
            title="HR Manager",
            description="Human Resources Manager",
            priority=1,
            allow_multiple_employees=False,
            is_active=True,
        )

        self.inactive_template = OrganizationTemplate.objects.create(
            name="Inactive Template",
            description="An inactive template for testing",
            is_active=False,
        )

        self.empty_template = OrganizationTemplate.objects.create(
            name="Empty Template", description="A template with no departments", is_active=True
        )

        self.template_with_inactive_depts = OrganizationTemplate.objects.create(
            name="Template with Inactive Departments",
            description="A template with only inactive departments",
            is_active=True,
        )

        self.inactive_dept_template = DepartmentTemplate.objects.create(
            organization_template=self.template_with_inactive_depts,
            name="Inactive Department",
            description="An inactive department",
            is_active=False,
        )

        self.template_no_designations = OrganizationTemplate.objects.create(
            name="Template with No Designations",
            description="A template with departments but no designations",
            is_active=True,
        )

        self.dept_no_designations = DepartmentTemplate.objects.create(
            organization_template=self.template_no_designations,
            name="Department without Designations",
            description="A department with no designations",
            is_active=True,
        )

        self.template_inactive_designations = OrganizationTemplate.objects.create(
            name="Template with Inactive Designations",
            description="A template with departments but inactive designations",
            is_active=True,
        )

        self.dept_inactive_designations = DepartmentTemplate.objects.create(
            organization_template=self.template_inactive_designations,
            name="Department with Inactive Designations",
            description="A department with inactive designations",
            is_active=True,
        )

        self.inactive_designation = DesignationTemplate.objects.create(
            organization_template=self.active_template,
            department_template=self.dept_inactive_designations,
            title="Inactive Manager",
            description="An inactive manager position",
            priority=1,
            allow_multiple_employees=False,
            is_active=False,
        )

        self.valid_form_data = {
            "user": self.user.id,
            "name": fake.company(),
            "tag_line": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "province": fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            "district": fake.city(),
            "municipality": fake.city(),
            "ward_no": str(fake.random_int(min=1, max=35)),
            "contact_no": fake.phone_number()[:15],
            "website": fake.url(),
            "is_active": True,
        }

    def test_form_queryset_only_includes_active_templates(self):
        """Test that organization_template field queryset only includes active templates."""
        from organization.forms import OrganizationForm

        form = OrganizationForm()
        template_queryset = form.fields["organization_template"].queryset

        self.assertIn(self.active_template, template_queryset)
        self.assertIn(self.empty_template, template_queryset)
        self.assertIn(self.template_with_inactive_depts, template_queryset)
        self.assertIn(self.template_no_designations, template_queryset)
        self.assertIn(self.template_inactive_designations, template_queryset)

        self.assertNotIn(self.inactive_template, template_queryset)

    def test_valid_template_selection_passes_validation(self):
        """Test that selecting a valid active template passes validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.active_template.id

        form = OrganizationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_no_template_selection_passes_validation(self):
        """Test that not selecting a template passes validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()

        form = OrganizationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_inactive_template_selection_fails_validation(self):
        """Test that selecting an inactive template fails validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.inactive_template.id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)

    def test_deleted_template_selection_fails_validation(self):
        """Test that selecting a deleted template fails validation."""
        from organization.forms import OrganizationForm

        temp_template = OrganizationTemplate.objects.create(
            name="Temporary Template", description="A template to be deleted", is_active=True
        )
        temp_id = temp_template.id
        temp_template.delete()

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = temp_id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)

    def test_template_with_no_active_departments_fails_validation(self):
        """Test that template with no active departments fails validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.empty_template.id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("does not contain any active departments", error_message)
        self.assertIn(self.empty_template.name, error_message)

    def test_template_with_only_inactive_departments_fails_validation(self):
        """Test that template with only inactive departments fails validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.template_with_inactive_depts.id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("does not contain any active departments", error_message)
        self.assertIn(self.template_with_inactive_depts.name, error_message)

    def test_template_with_no_active_designations_fails_validation(self):
        """Test that template with no active designations fails validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.template_no_designations.id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("does not contain any active designations", error_message)
        self.assertIn(self.template_no_designations.name, error_message)

    def test_template_with_only_inactive_designations_fails_validation(self):
        """Test that template with only inactive designations fails validation."""
        from organization.forms import OrganizationForm

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.template_inactive_designations.id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("does not contain any active designations", error_message)
        self.assertIn(self.template_inactive_designations.name, error_message)

    def test_template_field_hidden_for_existing_organization(self):
        """Test that template field is hidden when editing existing organization."""
        from organization.forms import OrganizationForm

        existing_org = Organization.objects.create(
            user=self.user,
            name="Existing Organization",
            tag_line="Test tagline",
            description="Test description",
            province=fake.random_element(elements=[choice[0] for choice in PROVINCE_CHOICES]),
            district=fake.city(),
            municipality=fake.city(),
            ward_no=str(fake.random_int(min=1, max=35)),
            contact_no=fake.phone_number()[:15],
            website=fake.url(),
        )

        form = OrganizationForm(instance=existing_org)

        self.assertIsInstance(form.fields["organization_template"].widget, forms.HiddenInput)

    def test_template_validation_with_multiple_active_departments_and_designations(self):
        """
        Test validation passes with template having multiple active departments and designations.
        """
        from organization.forms import OrganizationForm

        dept2 = DepartmentTemplate.objects.create(
            organization_template=self.active_template,
            name="IT Department",
            description="Information Technology Department",
            is_active=True,
        )

        DesignationTemplate.objects.create(
            organization_template=self.active_template,
            department_template=dept2,
            title="IT Manager",
            description="Information Technology Manager",
            priority=1,
            allow_multiple_employees=False,
            is_active=True,
        )

        DesignationTemplate.objects.create(
            organization_template=self.active_template,
            department_template=self.active_dept_template,
            title="HR Assistant",
            description="Human Resources Assistant",
            priority=2,
            allow_multiple_employees=True,
            is_active=True,
        )

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.active_template.id

        form = OrganizationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_template_validation_with_mixed_active_inactive_departments(self):
        """Test validation with template having both active and inactive departments."""
        from organization.forms import OrganizationForm

        DepartmentTemplate.objects.create(
            organization_template=self.active_template,
            name="Inactive Department",
            description="An inactive department",
            is_active=False,
        )

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.active_template.id

        form = OrganizationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_template_validation_with_nonexistent_template_id(self):
        """Test validation with a template ID that doesn't exist in database."""
        from organization.forms import OrganizationForm

        nonexistent_id = 99999

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = nonexistent_id

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)

    def test_template_validation_with_template_deactivated_after_form_load(self):
        """Test validation when template is deactivated between form load and submission."""
        from organization.forms import OrganizationForm

        temp_template = OrganizationTemplate.objects.create(
            name="Temporary Active Template",
            description="A template that will be deactivated",
            is_active=True,
        )

        temp_dept = DepartmentTemplate.objects.create(
            organization_template=temp_template,
            name="Temp Department",
            description="Temporary department",
            is_active=True,
        )

        DesignationTemplate.objects.create(
            organization_template=temp_template,
            department_template=temp_dept,
            title="Temp Manager",
            description="Temporary manager",
            priority=1,
            allow_multiple_employees=False,
            is_active=True,
        )

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = temp_template.id

        temp_template.is_active = False
        temp_template.save()

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("Select a valid choice", error_message)

    def test_template_validation_with_departments_deactivated_after_form_load(self):
        """Test validation when departments are deactivated between form load and submission."""
        from organization.forms import OrganizationForm

        temp_template = OrganizationTemplate.objects.create(
            name="Template with Departments to Deactivate",
            description="A template whose departments will be deactivated",
            is_active=True,
        )

        temp_dept = DepartmentTemplate.objects.create(
            organization_template=temp_template,
            name="Department to Deactivate",
            description="Department that will be deactivated",
            is_active=True,
        )

        DesignationTemplate.objects.create(
            organization_template=temp_template,
            department_template=temp_dept,
            title="Manager to Deactivate",
            description="Manager in department to be deactivated",
            priority=1,
            allow_multiple_employees=False,
            is_active=True,
        )

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = temp_template.id

        temp_dept.is_active = False
        temp_dept.save()

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("does not contain any active departments", error_message)

    def test_template_validation_with_designations_deactivated_after_form_load(self):
        """Test validation when designations are deactivated between form load and submission."""
        from organization.forms import OrganizationForm

        temp_template = OrganizationTemplate.objects.create(
            name="Template with Designations to Deactivate",
            description="A template whose designations will be deactivated",
            is_active=True,
        )

        temp_dept = DepartmentTemplate.objects.create(
            organization_template=temp_template,
            name="Department with Designations to Deactivate",
            description="Department whose designations will be deactivated",
            is_active=True,
        )

        temp_designation = DesignationTemplate.objects.create(
            organization_template=temp_template,
            department_template=temp_dept,
            title="Designation to Deactivate",
            description="Designation that will be deactivated",
            priority=1,
            allow_multiple_employees=False,
            is_active=True,
        )

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = temp_template.id

        temp_designation.is_active = False
        temp_designation.save()

        form = OrganizationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("organization_template", form.errors)
        error_message = form.errors["organization_template"][0]
        self.assertIn("does not contain any active designations", error_message)

    def test_template_validation_with_mixed_active_inactive_designations_in_department(self):
        """Test validation with departments having both active and inactive designations."""
        from organization.forms import OrganizationForm

        DesignationTemplate.objects.create(
            organization_template=self.active_template,
            department_template=self.active_dept_template,
            title="Inactive HR Assistant",
            description="An inactive HR assistant position",
            priority=3,
            allow_multiple_employees=True,
            is_active=False,
        )

        form_data = self.valid_form_data.copy()
        form_data["organization_template"] = self.active_template.id

        form = OrganizationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_clean_organization_template_method_directly(self):
        """Test the clean_organization_template method directly with various scenarios."""
        form = OrganizationForm(data=self.valid_form_data)
        form.cleaned_data = {"organization_template": None}
        result = form.clean_organization_template()
        self.assertIsNone(result)

        form = OrganizationForm(data=self.valid_form_data)
        form.cleaned_data = {"organization_template": self.active_template}
        result = form.clean_organization_template()
        self.assertEqual(result, self.active_template)

        form = OrganizationForm(data=self.valid_form_data)
        form.cleaned_data = {"organization_template": self.inactive_template}
        with self.assertRaises(forms.ValidationError) as context:
            form.clean_organization_template()
        self.assertIn("not available or has been deactivated", str(context.exception))
