from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import date
from .models import Task, Project, DailyReport, User
from .forms import TaskForm, DailyReportForm, ProjectForm


class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 bg-white/80 '
                         'text-slate-900 text-sm font-medium focus:outline-none focus:ring-2 '
                         'focus:ring-indigo-500/40 focus:border-indigo-400 transition-all',
                'placeholder': 'Enter new username',
            })
        }


def _is_manager(user):
    """Helper to safely verify if a user has manager or admin status."""
    return (
        getattr(user, 'is_superuser', False) or
        getattr(user, 'is_staff', False) or
        getattr(user, 'is_manager', False) or
        getattr(user, 'role', None) == 'manager'
    )


# --- Login View with Role-Based Redirect ---

class RoleBasedLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        if _is_manager(user):
            return reverse('manager_dashboard')
        return reverse('employee_dashboard')


# --- Dashboard Views ---

@login_required
def dashboard_router(request):
    """Routes users to their respective dashboard based on role."""
    if _is_manager(request.user):
        return redirect('manager_dashboard')
    return redirect('employee_dashboard')


@login_required
def manager_dashboard(request):
    """Displays manager overview with aggregated task & work metrics."""
    if not _is_manager(request.user):
        return redirect('employee_dashboard')

    today = date.today()

    task_stats = Task.objects.aggregate(
        total_tasks=Count('id'),
        todo_count=Count('id', filter=Q(status='todo')),
        in_progress_count=Count('id', filter=Q(status='in_progress')),
        completed_count=Count('id', filter=Q(status='completed'))
    )

    report_stats = DailyReport.objects.aggregate(
        total_hours=Sum('hours_logged'),
        avg_hours_per_report=Avg('hours_logged')
    )

    projects_with_counts = Project.objects.annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='completed'))
    )

    employee_stats = User.objects.filter(role='employee').annotate(
        assigned_tasks_count=Count('assigned_tasks', filter=~Q(assigned_tasks__status='completed')),
        total_logged_hours=Sum('reports__hours_logged')
    )

    recent_tasks = Task.objects.all().select_related('project', 'assigned_to').order_by('-created_at')[:10]

    tasks_due_today = Task.objects.filter(
        due_date=today, status__in=['todo', 'in_progress']
    ).count()

    overdue_tasks = Task.objects.filter(
        due_date__lt=today, status__in=['todo', 'in_progress']
    ).count()

    recent_activity = Task.objects.all().select_related('project', 'assigned_to').order_by('-created_at')[:6]

    project_progress = []
    for proj in projects_with_counts:
        pct = 0
        if proj.total_tasks > 0:
            pct = round((proj.completed_tasks / proj.total_tasks) * 100)
        project_progress.append({
            'project': proj,
            'progress_pct': pct,
        })

    total_tasks = task_stats['total_tasks'] or 0
    completed_tasks = task_stats['completed_count'] or 0
    productivity_score = 0
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
        overdue_penalty = min((overdue_tasks / total_tasks) * 25, 25)
        due_today_bonus = min((tasks_due_today / total_tasks) * 5, 5)
        productivity_score = max(0, min(100, round(completion_rate - overdue_penalty + due_today_bonus)))

    employee_workload = []
    for emp in employee_stats:
        workload_pct = 0
        if emp.assigned_tasks_count > 0:
            workload_pct = min(100, round((emp.assigned_tasks_count / 5) * 100))
        employee_workload.append({
            'employee': emp,
            'workload_pct': workload_pct,
        })

    context = {
        'total_employees': User.objects.filter(role='employee').count(),
        'projects': projects_with_counts,
        'recent_tasks': recent_tasks,
        'tasks': recent_tasks,
        'task_stats': task_stats,
        'total_hours_logged': report_stats['total_hours'] or 0,
        'avg_hours_per_report': round(report_stats['avg_hours_per_report'] or 0, 1),
        'employee_stats': employee_stats,
        'tasks_due_today': tasks_due_today,
        'overdue_tasks': overdue_tasks,
        'recent_activity': recent_activity,
        'project_progress': project_progress,
        'productivity_score': productivity_score,
        'employee_workload': employee_workload,
        'today': today,
    }
    return render(request, 'manager_dashboard.html', context)


@login_required
def employee_dashboard(request):
    """Displays employee-specific Kanban workspace with aggregated personal metrics."""
    user_tasks = Task.objects.filter(assigned_to=request.user).select_related('project')
    
    status_counts = user_tasks.aggregate(
        todo=Count('id', filter=Q(status='todo')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        completed=Count('id', filter=Q(status='completed'))
    )

    my_logged_hours = DailyReport.objects.filter(employee=request.user).aggregate(
        total=Sum('hours_logged')
    )['total'] or 0

    context = {
        'tasks': user_tasks,
        'todo_tasks': user_tasks.filter(status='todo'),
        'in_progress_tasks': user_tasks.filter(status='in_progress'),
        'completed_tasks': user_tasks.filter(status='completed'),
        'status_counts': status_counts,
        'my_logged_hours': my_logged_hours,
    }
    return render(request, 'employee_dashboard.html', context)


# --- Task Views ---

@login_required
def task_search(request):
    """HTMX View: Live search tasks by title, description, project, or assignee."""
    query = request.GET.get('q', '').strip()

    if query:
        if _is_manager(request.user):
            base_qs = Task.objects.all()
        else:
            base_qs = Task.objects.filter(assigned_to=request.user)

        tasks = base_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(project__title__icontains=query) |
            Q(assigned_to__username__icontains=query)
        ).select_related('project', 'assigned_to').distinct()[:15]
    else:
        if _is_manager(request.user):
            tasks = Task.objects.all().select_related('project', 'assigned_to').order_by('-id')[:20]
        else:
            tasks = Task.objects.filter(assigned_to=request.user).select_related('project', 'assigned_to').order_by('-id')[:20]

    if request.headers.get('HX-Request'):
        return render(request, 'partials/task_search_results.html', {'tasks': tasks, 'query': query})

    return render(request, 'task_search.html', {'tasks': tasks, 'query': query})


@login_required
def create_task(request):
    """Allows managers to create and assign tasks."""
    if not _is_manager(request.user):
        return redirect('employee_dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = redirect('manager_dashboard')
                response['HX-Redirect'] = reverse('manager_dashboard')
                return response
            return redirect('manager_dashboard')
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {'form': form, 'title': 'Create New Task'})


@login_required
def create_project(request):
    """Allows managers to create new projects."""
    if not _is_manager(request.user):
        return redirect('employee_dashboard')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = redirect('manager_dashboard')
                response['HX-Redirect'] = reverse('manager_dashboard')
                return response
            return redirect('manager_dashboard')
    else:
        form = ProjectForm()

    return render(request, 'project_form.html', {'form': form, 'title': 'Create New Project'})


@login_required
def update_task_status(request, pk, new_status):
    """Allows employees or managers to update task status."""
    task = get_object_or_404(Task, pk=pk)
    
    if request.user == task.assigned_to or _is_manager(request.user):
        task.status = new_status
        task.save()

    if request.headers.get('HX-Request'):
        if _is_manager(request.user):
            return manager_dashboard(request)
        return employee_dashboard(request)

    return redirect('dashboard')


# --- Report Views ---

@login_required
def submit_report(request):
    """Allows employees to log their daily work summary and hours."""
    if request.method == 'POST':
        form = DailyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.employee = request.user
            report.save()
            if request.headers.get('HX-Request'):
                response = redirect('employee_dashboard')
                response['HX-Redirect'] = reverse('employee_dashboard')
                return response
            return redirect('employee_dashboard')
    else:
        form = DailyReportForm()

    return render(request, 'report_form.html', {'form': form})


@login_required
def view_reports(request):
    """Allows managers to inspect all daily reports along with aggregated totals."""
    if not _is_manager(request.user):
        return redirect('employee_dashboard')

    reports = DailyReport.objects.select_related('employee').order_by('-date')
    
    overall_hours = DailyReport.objects.aggregate(
        total_hours=Sum('hours_logged'),
        avg_hours=Avg('hours_logged')
    )

    context = {
        'reports': reports,
        'total_hours': overall_hours['total_hours'] or 0,
        'avg_hours': round(overall_hours['avg_hours'] or 0, 1),
    }
    return render(request, 'report_list.html', context)


@login_required
def team_members_list(request):
    """Displays a detailed directory of all team members and their metrics."""
    if not _is_manager(request.user):
        return redirect('employee_dashboard')

    members = User.objects.filter(role='employee').annotate(
        active_tasks_count=Count('assigned_tasks', filter=~Q(assigned_tasks__status='completed')),
        completed_tasks_count=Count('assigned_tasks', filter=Q(assigned_tasks__status='completed')),
        total_logged_hours=Sum('reports__hours_logged')
    ).order_by('username')

    context = {
        'members': members,
        'total_members': members.count(),
    }
    return render(request, 'team_members.html', context)


# --- Profile Settings Views ---

class ChangePasswordView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('change_password_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ChangePasswordDoneView(PasswordChangeDoneView):
    template_name = 'change_password_done.html'


@login_required
def change_username(request):
    """Allows any authenticated user to change their username."""
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ChangeUsernameForm(instance=request.user)
    return render(request, 'change_username.html', {'form': form})