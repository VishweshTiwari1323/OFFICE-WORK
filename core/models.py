from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model supporting Roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_employee(self):
        return self.role == 'employee'


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('completed', 'Completed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class DailyReport(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    date = models.DateField(auto_now_add=True)
    summary = models.TextField(help_text="Describe the tasks you worked on today.")
    hours_logged = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Report by {self.employee.username} on {self.date}"