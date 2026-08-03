from django import forms
from .models import Task, DailyReport, User, Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'manager']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(role='manager')

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assigned_to', 'priority', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
            'assigned_to': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
            'priority': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none'}),
            'due_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to dropdown to only show employees
        self.fields['assigned_to'].queryset = User.objects.filter(role='employee')


class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        fields = ['summary', 'hours_logged']
        widgets = {
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none',
                'rows': 4,
                'placeholder': 'What did you work on today?'
            }),
            'hours_logged': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none',
                'step': '0.5',
                'placeholder': 'e.g. 7.5'
            }),
        }