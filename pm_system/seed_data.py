import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Project, Task, DailyReport

User = get_user_model()

print("=" * 60)
print("SEEDING PM SYSTEM DATABASE")
print("=" * 60)

# Clear existing data
print("\n[1/6] Clearing existing data...")
DailyReport.objects.all().delete()
Task.objects.all().delete()
Project.objects.all().delete()
User.objects.filter(is_superuser=True).delete()
User.objects.filter(role='manager').delete()
User.objects.filter(role='employee').delete()
print("  -> Existing data cleared.")

# 1. Create Manager
print("\n[2/6] Creating manager user...")
# Use get_or_create to handle existing users - delete first if exists to ensure clean state
User = get_user_model()
User.objects.filter(username="vishwesh_manager").delete()
manager, created = User.objects.get_or_create(
    username="vishwesh_manager",
    defaults={
        "first_name": "Vishwesh",
        "last_name": "",
        "email": "vishwesh@workspace.com",
        "role": "manager",
        "is_staff": True,
        "is_superuser": True,
    }
)
manager.set_password("ManagerPass2026!")
manager.save()
print(f"  -> Manager {'created' if created else 'retrieved'}: '{manager.username}'.")

# 2. Create 10 Employees
print("\n[3/6] Creating 10 employees...")
# Delete existing employees first to ensure clean state
User.objects.filter(role='employee').delete()

employees_data = [
    ("emp_alex", "Alex", "Johnson"),
    ("emp_sarah", "Sarah", " Connor"),
    ("emp_david", "David", "Miller"),
    ("emp_emily", "Emily", "Davis"),
    ("emp_michael", "Michael", "Brown"),
    ("emp_jessica", "Jessica", "Wilson"),
    ("emp_daniel", "Daniel", "Taylor"),
    ("emp_sophia", "Sophia", "Anderson"),
    ("emp_james", "James", "Thomas"),
    ("emp_olivia", "Olivia", "Jackson"),
]

employees = []
for username, fname, lname in employees_data:
    emp, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": fname,
            "last_name": lname,
            "email": f"{username}@workspace.com",
            "role": "employee",
        }
    )
    emp.set_password("EmpPass2026!")
    emp.save()
    employees.append(emp)
print(f"  -> {len(employees)} employees created.")

# 3. Create Projects
print("\n[4/6] Creating 4 projects...")
# Delete existing projects first
Project.objects.all().delete()

projects_data = [
    ("Mobile App Redesign", "Complete UI/UX overhaul of iOS & Android apps."),
    ("Cloud Migration", "Migrate on-prem servers to AWS infrastructure."),
    ("API Gateway Integration", "Build centralized REST API gateway."),
    ("Security & Compliance Audit", "SOC2 compliance check & security patch updates."),
]

projects = []
for p_title, p_desc in projects_data:
    p, _ = Project.objects.get_or_create(
        title=p_title,
        defaults={"description": p_desc, "manager": manager},
    )
    projects.append(p)
print(f"  -> {len(projects)} projects created.")

# 4. Create Tasks (12 total)
print("\n[5/6] Creating 12 tasks...")
# Delete existing tasks first
Task.objects.all().delete()

today = timezone.now().date()

tasks_sample = [
    ("Design Figma Wireframes", projects[0], employees[0], "completed", "high", today - timedelta(days=3)),
    ("Setup AWS S3 Buckets", projects[1], employees[1], "completed", "medium", today - timedelta(days=1)),
    ("API Endpoint Authentication", projects[2], employees[2], "in_progress", "high", today),
    ("Database Index Optimization", projects[1], employees[3], "in_progress", "high", today - timedelta(days=2)),
    ("Frontend Refactoring", projects[0], employees[4], "in_progress", "medium", today + timedelta(days=4)),
    ("Write Security Policies", projects[3], employees[5], "todo", "high", today - timedelta(days=1)),
    ("Push Notification Setup", projects[0], employees[6], "todo", "medium", today),
    ("Docker Container Setup", projects[1], employees[7], "completed", "low", today - timedelta(days=5)),
    ("API Rate Limiting", projects[2], employees[8], "in_progress", "high", today + timedelta(days=2)),
    ("SOC2 Documentation Review", projects[3], employees[9], "todo", "medium", today - timedelta(days=3)),
    ("Mobile Login Flow Redesign", projects[0], employees[1], "completed", "high", today - timedelta(days=7)),
    ("CI/CD Pipeline Setup", projects[1], employees[2], "todo", "medium", today + timedelta(days=5)),
]

for t_title, t_proj, t_emp, t_status, t_priority, t_due in tasks_sample:
    Task.objects.get_or_create(
        title=t_title,
        defaults={
            "project": t_proj,
            "assigned_to": t_emp,
            "status": t_status,
            "priority": t_priority,
            "due_date": t_due,
            "description": f"Task: {t_title}",
        },
    )
print(f"  -> {len(tasks_sample)} tasks created.")

# 5. Create Daily Work Logs
print("\n[6/6] Creating daily work logs...")
# Delete existing work logs first
DailyReport.objects.all().delete()

log_entries = [
    (employees[0], today - timedelta(days=3), "Completed Figma wireframes for mobile app redesign.", 8.0),
    (employees[1], today - timedelta(days=1), "Setup AWS S3 buckets and configured IAM policies.", 7.5),
    (employees[2], today, "Working on API endpoint authentication middleware.", 6.0),
    (employees[3], today - timedelta(days=2), "Optimizing database indexes for performance.", 8.0),
    (employees[4], today - timedelta(days=1), "Frontend refactoring of component library.", 7.0),
    (employees[5], today - timedelta(days=1), "Drafting SOC2 security policies document.", 8.5),
    (employees[6], today, "Setting up push notification service integration.", 5.5),
    (employees[7], today - timedelta(days=5), "Docker container setup and configuration.", 8.0),
    (employees[8], today - timedelta(days=1), "Implementing API rate limiting logic.", 7.0),
    (employees[9], today - timedelta(days=3), "Reviewing SOC2 documentation requirements.", 6.5),
    (employees[1], today - timedelta(days=7), "Redesigned mobile login flow UI components.", 8.0),
    (employees[2], today - timedelta(days=2), "Configuring CI/CD pipeline for automated deployments.", 7.5),
    (employees[0], today - timedelta(days=2), "Reviewed pull requests and updated design tokens.", 6.0),
    (employees[3], today - timedelta(days=1), "Writing database migration scripts.", 8.0),
    (employees[6], today - timedelta(days=1), "Testing push notification delivery on iOS.", 7.0),
]

for emp, log_date, summary, hours in log_entries:
    DailyReport.objects.get_or_create(
        employee=emp,
        date=log_date,
        defaults={
            "summary": summary,
            "hours_logged": hours,
        },
    )
print(f"  -> {len(log_entries)} daily work logs created.")

# Summary
print("\n" + "=" * 60)
print("SEEDING COMPLETE")
print("=" * 60)
print(f"  Manager:    {manager.username}")
print(f"  Employees:  {len(employees)}")
print(f"  Projects:   {len(projects)}")
print(f"  Tasks:      {Task.objects.count()}")
print(f"  Work Logs:  {DailyReport.objects.count()}")
print("=" * 60)