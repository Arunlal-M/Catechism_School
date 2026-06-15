import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from admissions.models import SchoolClass, Division, Provision, Unit
from common.constants import ROLE_ADMIN

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with master data and an admin user"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seed...")

        # 1. Create superuser
        admin_email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@school.com")
        admin_pass = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")
        
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password=admin_pass,
                first_name="System",
                last_name="Admin",
                role=ROLE_ADMIN
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_email} / {admin_pass}"))
        else:
            self.stdout.write(f"Admin user {admin_email} already exists.")

        # 2. Seed Classes
        classes_data = [
            ("LKG", 1), ("UKG", 2),
            ("Class 1", 3), ("Class 2", 4), ("Class 3", 5),
            ("Class 4", 6), ("Class 5", 7), ("Class 6", 8),
            ("Class 7", 9), ("Class 8", 10), ("Class 9", 11),
            ("Class 10", 12), ("Class 11", 13), ("Class 12", 14)
        ]
        for name, order in classes_data:
            SchoolClass.objects.get_or_create(name=name, defaults={"order": order})
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(classes_data)} classes."))

        # 3. Seed Divisions
        divisions = ["A", "B", "C", "D", "E"]
        for div in divisions:
            Division.objects.get_or_create(name=div)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(divisions)} divisions."))

        # 4. Seed Provisions and Units (Example data)
        provisions_data = {
            "North Provision": ["Unit Alpha", "Unit Beta"],
            "South Provision": ["Unit Gamma", "Unit Delta"],
            "Central Provision": ["Main Unit"]
        }
        for prov_name, units in provisions_data.items():
            provision, _ = Provision.objects.get_or_create(name=prov_name)
            for unit_name in units:
                Unit.objects.get_or_create(name=unit_name, provision=provision)
        self.stdout.write(self.style.SUCCESS("Seeded provisions and units."))

        # 5. Seed Occupations
        from admissions.models import Occupation
        occupations = ["Engineer", "Doctor", "Business", "Teacher", "Unemployed", "Other", "Government Employee"]
        for occ in occupations:
            Occupation.objects.get_or_create(name=occ)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(occupations)} occupations."))

        # 6. Seed Students (Faker)
        self.stdout.write("Generating mock students...")
        import random
        from faker import Faker
        from students.models import StudentProfile, ParentInfo, CatechismInfo
        from common.constants import STATUS_ACTIVE, STATUS_PENDING

        fake = Faker()
        
        all_classes = list(SchoolClass.objects.all())
        all_divisions = list(Division.objects.all())
        all_occupations = list(Occupation.objects.all())
        
        # We need provisions and units to assign if attended_catechism
        all_provisions = list(Provision.objects.all())

        if all_classes and all_divisions:
            for i in range(20):
                is_active = i < 15
                gender = random.choice(["M", "F"])
                first_name = fake.first_name_male() if gender == "M" else fake.first_name_female()
                last_name = fake.last_name()
                
                # Student Profile
                student = StudentProfile.objects.create(
                    student_name=f"{first_name} {last_name}",
                    email=fake.email(),
                    gender=gender,
                    date_of_birth=fake.date_of_birth(minimum_age=4, maximum_age=18),
                    school_class=random.choice(all_classes),
                    division=random.choice(all_divisions),
                    residential_address=fake.address(),
                    attended_catechism=random.choice([True, False]),
                    status=STATUS_ACTIVE if is_active else STATUS_PENDING,
                    remarks=fake.sentence() if random.random() > 0.5 else ""
                )

                # Parent Info
                ParentInfo.objects.create(
                    student=student,
                    father_name=f"{fake.first_name_male()} {last_name}",
                    father_occupation=random.choice(all_occupations) if random.random() > 0.2 else None,
                    father_phone=fake.numerify(text="##########"),
                    mother_name=f"{fake.first_name_female()} {last_name}",
                    mother_occupation=random.choice(all_occupations) if random.random() > 0.2 else None,
                    mother_phone=fake.numerify(text="##########")
                )

                # Catechism Info
                if student.attended_catechism:
                    provision = random.choice(all_provisions)
                    unit = random.choice(list(provision.units.all())) if provision.units.exists() else None
                    CatechismInfo.objects.create(
                        student=student,
                        catechism_teacher_name=fake.name(),
                        provision=provision,
                        unit=unit
                    )
            self.stdout.write(self.style.SUCCESS("Seeded 20 mock students (15 active, 5 pending)."))
        else:
            self.stdout.write(self.style.WARNING("Skipped seeding students due to missing master data."))

        self.stdout.write(self.style.SUCCESS("Database seed complete!"))
