"""
Unit tests for organization models and forms.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from faker import Faker

from .choices import PROVINCE_CHOICES
from .forms import DesignationForm
from .models import Department, Designation, Organization

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

    def test_organization_property_returns_none_when_department_is_none(self):
        """Test that organization property returns None when department is None."""
        designation_without_dept = Designation(
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )
        designation_without_dept.department = None

        self.assertIsNone(designation_without_dept.organization)

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
            department=self.department,
            title=long_title,
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )
        self.assertEqual(designation.organization, self.organization)

        min_priority_designation = Designation.objects.create(
            department=self.department,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=1,
            allow_multiple_employees=fake.boolean(),
        )
        self.assertEqual(min_priority_designation.organization, self.organization)

        max_priority_designation = Designation.objects.create(
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


class DesignationAdminIntegrationTests(TestCase):
    """Integration tests for the Designation admin interface."""

    def setUp(self):
        """Set up test data and admin user."""
        from django.contrib.admin.sites import AdminSite
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory

        from .admin import DesignationAdmin

        User = get_user_model()

        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

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

        self.designation1 = Designation.objects.create(
            department=self.department1,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        self.designation2 = Designation.objects.create(
            department=self.department2,
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            priority=fake.random_int(min=1, max=10),
            allow_multiple_employees=fake.boolean(),
        )

        self.site = AdminSite()
        self.factory = RequestFactory()
        self.admin_class = DesignationAdmin(Designation, self.site)

    def test_admin_list_view_displays_organization_information_correctly(self):
        """Test that admin list view displays organization information correctly."""
        from django.contrib.admin import ModelAdmin
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get("/admin/organization/designation/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        changelist = self.admin_class.get_changelist_instance(request)

        self.assertIn("organization", self.admin_class.list_display)

        queryset = changelist.get_queryset(request)
        designations = list(queryset)

        self.assertGreaterEqual(len(designations), 2)

        found_designation1 = None
        found_designation2 = None

        for designation in designations:
            if designation.id == self.designation1.id:
                found_designation1 = designation
            elif designation.id == self.designation2.id:
                found_designation2 = designation

        self.assertIsNotNone(found_designation1)
        self.assertIsNotNone(found_designation2)

        self.assertEqual(found_designation1.organization, self.organization1)
        self.assertEqual(found_designation2.organization, self.organization2)
        self.assertEqual(found_designation1.organization.name, self.organization1.name)
        self.assertEqual(found_designation2.organization.name, self.organization2.name)

    def test_admin_form_submission_workflow_with_organization_department_chaining(self):
        """Test admin form submission workflow with organization-department chaining."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get("/admin/organization/designation/add/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        form_class = self.admin_class.get_form(request)
        form = form_class()

        self.assertIn("organization", form.fields)
        org_field = form.fields["organization"]
        self.assertTrue(org_field.required)
        self.assertIn("onchange", org_field.widget.attrs)
        self.assertEqual(
            org_field.widget.attrs["onchange"], "get_department_for_organization(this.value);"
        )

        post_data = {
            "organization": self.organization1.id,
            "department": self.department1.id,
            "title": fake.job(),
            "description": fake.text(max_nb_chars=200),
            "priority": fake.random_int(min=1, max=10),
            "allow_multiple_employees": fake.boolean(),
        }

        post_request = self.factory.post("/admin/organization/designation/add/", post_data)
        post_request.user = self.admin_user

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(post_request)
        post_request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(post_request)
        post_request._messages = FallbackStorage(post_request)

        form = form_class(post_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        new_designation = form.save()

        self.assertIsInstance(new_designation, Designation)
        self.assertEqual(new_designation.department, self.department1)
        self.assertEqual(new_designation.organization, self.organization1)
        self.assertEqual(new_designation.title, post_data["title"])

    def test_editing_existing_designations_through_admin_interface(self):
        """Test editing existing designations through admin interface."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get(
            f"/admin/organization/designation/{self.designation1.id}/change/"
        )
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        form_class = self.admin_class.get_form(request, self.designation1)
        form = form_class(instance=self.designation1)

        self.assertEqual(form.fields["organization"].initial, self.organization1)

        updated_title = fake.job()
        post_data = {
            "organization": self.organization1.id,
            "department": self.department1.id,
            "title": updated_title,
            "description": self.designation1.description,
            "priority": self.designation1.priority,
            "allow_multiple_employees": self.designation1.allow_multiple_employees,
        }

        post_request = self.factory.post(
            f"/admin/organization/designation/{self.designation1.id}/change/", post_data
        )
        post_request.user = self.admin_user

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(post_request)
        post_request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(post_request)
        post_request._messages = FallbackStorage(post_request)

        form = form_class(post_data, instance=self.designation1)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        updated_designation = form.save()

        self.assertEqual(updated_designation.id, self.designation1.id)
        self.assertEqual(updated_designation.title, updated_title)
        self.assertEqual(updated_designation.organization, self.organization1)
        self.assertEqual(updated_designation.department, self.department1)

        post_data_invalid = {
            "organization": self.organization1.id,
            "department": self.department2.id,
            "title": updated_title,
            "description": self.designation1.description,
            "priority": self.designation1.priority,
            "allow_multiple_employees": self.designation1.allow_multiple_employees,
        }

        form_invalid = form_class(post_data_invalid, instance=self.designation1)
        self.assertFalse(form_invalid.is_valid())
        self.assertIn("department", form_invalid.errors)

    def test_ajax_chaining_works_in_admin_environment(self):
        """Test that AJAX chaining works in admin environment."""
        from django.test import Client

        client = Client()
        client.login(username="admin", password="adminpass123")

        response = client.get(
            "/helper/get_department_for_organization/", {"organization_id": self.organization1.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        import json

        data = json.loads(response.content)

        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

        departments = data["data"]
        self.assertGreater(len(departments), 0)

        found_department = None
        for dept in departments:
            if dept["id"] == self.department1.id:
                found_department = dept
                break

        self.assertIsNotNone(found_department)
        self.assertEqual(found_department["name"], self.department1.name)

        response2 = client.get(
            "/helper/get_department_for_organization/", {"organization_id": self.organization2.id}
        )

        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        departments2 = data2["data"]

        org2_dept_ids = [dept["id"] for dept in departments2]
        self.assertIn(self.department2.id, org2_dept_ids)
        self.assertNotIn(self.department1.id, org2_dept_ids)

        response3 = client.get("/helper/get_department_for_organization/", {"organization_id": 9})

        self.assertEqual(response3.status_code, 200)
        data3 = json.loads(response3.content)
        self.assertEqual(data3["data"], [])

        response4 = client.get("/helper/get_department_for_organization/")

        self.assertEqual(response4.status_code, 200)
        data4 = json.loads(response4.content)
        self.assertEqual(data4["data"], [])

    def test_admin_form_javascript_media_inclusion(self):
        """Test that admin form includes proper JavaScript media files."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get("/admin/organization/designation/add/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        form_class = self.admin_class.get_form(request)
        form = form_class()

        self.assertIn("js/chained/get_department_for_organization.js", form.media._js)

    def test_admin_list_display_with_multiple_designations(self):
        """Test admin list display with multiple designations from different organizations."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        additional_designations = []
        for i in range(3):
            designation = Designation.objects.create(
                department=self.department1,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=fake.random_int(min=1, max=10),
                allow_multiple_employees=fake.boolean(),
            )
            additional_designations.append(designation)

        request = self.factory.get("/admin/organization/designation/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        changelist = self.admin_class.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)

        designations = list(queryset)
        self.assertGreaterEqual(len(designations), 5)

        for designation in designations:
            self.assertIsNotNone(designation.organization)
            if designation.department == self.department1:
                self.assertEqual(designation.organization, self.organization1)
            elif designation.department == self.department2:
                self.assertEqual(designation.organization, self.organization2)

    def test_admin_form_validation_with_invalid_combinations(self):
        """Test admin form validation with invalid organization-department combinations."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get("/admin/organization/designation/add/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        form_class = self.admin_class.get_form(request)

        invalid_data = {
            "organization": self.organization1.id,
            "department": self.department2.id,
            "title": fake.job(),
            "description": fake.text(max_nb_chars=200),
            "priority": fake.random_int(min=1, max=10),
            "allow_multiple_employees": fake.boolean(),
        }

        form = form_class(invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("department", form.errors)

        error_message = form.errors["department"][0]
        self.assertIn(self.department2.name, error_message)
        self.assertIn(self.organization1.name, error_message)
        self.assertIn("does not belong to", error_message)

    def test_admin_interface_with_organization_property_performance(self):
        """Test admin interface performance with organization property access."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        designations = []
        for i in range(10):
            designation = Designation.objects.create(
                department=self.department1,
                title=fake.job(),
                description=fake.text(max_nb_chars=200),
                priority=fake.random_int(min=1, max=10),
                allow_multiple_employees=fake.boolean(),
            )
            designations.append(designation)

        request = self.factory.get("/admin/organization/designation/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        changelist = self.admin_class.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)

        designations_list = list(queryset.select_related("department__organization"))

        with self.assertNumQueries(0):
            organizations = [d.organization for d in designations_list]
            self.assertGreater(len(organizations), 0)

        for designation in designations_list:
            self.assertIsNotNone(designation.organization)
            if designation.department == self.department1:
                self.assertEqual(designation.organization, self.organization1)

    def test_admin_form_with_empty_organization_selection(self):
        """Test admin form behavior with empty organization selection."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get("/admin/organization/designation/add/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        form_class = self.admin_class.get_form(request)

        data_with_dept_only = {
            "department": self.department1.id,
            "title": fake.job(),
            "description": fake.text(max_nb_chars=200),
            "priority": fake.random_int(min=1, max=10),
            "allow_multiple_employees": fake.boolean(),
        }

        form = form_class(data_with_dept_only)
        if form.is_valid():
            self.assertEqual(form.cleaned_data["organization"], self.organization1)
        else:
            self.assertIn("organization", form.errors)

    def test_admin_changelist_filtering_by_organization(self):
        """Test admin changelist filtering functionality with organization property."""
        from django.contrib.messages.storage.fallback import FallbackStorage

        request = self.factory.get("/admin/organization/designation/")
        request.user = self.admin_user

        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request._messages = FallbackStorage(request)

        changelist = self.admin_class.get_changelist_instance(request)

        queryset = changelist.get_queryset(request)
        designations = list(queryset)

        test_designation1 = None
        test_designation2 = None

        for designation in designations:
            if designation.id == self.designation1.id:
                test_designation1 = designation
            elif designation.id == self.designation2.id:
                test_designation2 = designation

        self.assertIsNotNone(test_designation1, "Test designation 1 not found in queryset")
        self.assertIsNotNone(test_designation2, "Test designation 2 not found in queryset")

        self.assertEqual(test_designation1.organization, self.organization1)
        self.assertEqual(test_designation1.department.organization, self.organization1)

        self.assertEqual(test_designation2.organization, self.organization2)
        self.assertEqual(test_designation2.department.organization, self.organization2)

        org1_designations = [d for d in designations if d.organization == self.organization1]
        org2_designations = [d for d in designations if d.organization == self.organization2]

        self.assertGreater(len(org1_designations), 0)
        self.assertGreater(len(org2_designations), 0)

        for designation in org1_designations:
            self.assertEqual(designation.organization, self.organization1)
            self.assertEqual(designation.department.organization, self.organization1)

        for designation in org2_designations:
            self.assertEqual(designation.organization, self.organization2)
            self.assertEqual(designation.department.organization, self.organization2)
            self.assertEqual(designation.department, self.department2)
