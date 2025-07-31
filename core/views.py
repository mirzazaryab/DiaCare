from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import CustomUser, GlucoseLog, MealLog, ActivityLog, Summary, DoctorNote, Consent
from django.utils import timezone
from datetime import date
import csv
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        age = request.POST['age']
        gender = request.POST['gender']
        diabetes_type = request.POST['diabetes_type']
        medications = request.POST['medications']
        consent = request.POST.get('consent') == 'on'

        user = CustomUser.objects.create_user(
            username=email, email=email, password=password, role=role,
            age=age, gender=gender, diabetes_type=diabetes_type, medications=medications
        )
        Consent.objects.create(user=user, consent_given=consent)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    if request.user.role == 'patient':
        logs = GlucoseLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
        summary = Summary.objects.filter(user=request.user, date=date.today()).first()
        return render(request, 'dashboard.html', {'logs': logs, 'summary': summary})
    else:
        patients = CustomUser.objects.filter(role='patient')
        return render(request, 'doctor_dashboard.html', {'patients': patients})

@login_required
def log_glucose(request):
    if request.method == 'POST':
        fasting = request.POST.get('fasting')
        postprandial = request.POST.get('postprandial')
        hba1c = request.POST.get('hba1c')
        GlucoseLog.objects.create(
            user=request.user,
            fasting=float(fasting) if fasting else None,
            postprandial=float(postprandial) if postprandial else None,
            hba1c=float(hba1c) if hba1c else None
        )
        # Generate summary
        summary_text = 'Your levels were stable today.'
        if postprandial and float(postprandial) > 180:
            summary_text = 'Slight spike after meal. Consider reducing carbs.'
        elif fasting and float(fasting) < 70:
            summary_text = 'Low fasting glucose. Have a small snack.'
        Summary.objects.create(user=request.user, date=date.today(), text=summary_text)
        return redirect('dashboard')
    return render(request, 'log_glucose.html')


@login_required
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        data = csv_file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(data))
        for row in reader:
            GlucoseLog.objects.create(
                user=request.user,
                timestamp=row['timestamp'],
                fasting=float(row['fasting']) if row['fasting'] else None,
                postprandial=float(row['postprandial']) if row['postprandial'] else None
            )
        return redirect('dashboard')
    return render(request, 'upload_csv.html')


@login_required
def doctor_notes(request, patient_id):
    patient = CustomUser.objects.get(id=patient_id)
    if request.method == 'POST':
        note = request.POST['note']
        DoctorNote.objects.create(doctor=request.user, patient=patient, note=note)
        return redirect('dashboard')
    logs = GlucoseLog.objects.filter(user=patient).order_by('-timestamp')[:10]
    notes = DoctorNote.objects.filter(patient=patient).order_by('-timestamp')
    return render(request, 'doctor_notes.html', {'patient': patient, 'logs': logs, 'notes': notes})


@login_required
def generate_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="glucose_report.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"Glucose Report for {request.user.email}")
    logs = GlucoseLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
    y = 700
    for log in logs:
        p.drawString(100, y,
                     f"{log.timestamp}: Fasting={log.fasting or 'N/A'}, Postprandial={log.postprandial or 'N/A'}")
        y -= 20
    p.showPage()
    p.save()
    return response