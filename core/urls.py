from django.urls import path
from core import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('log-glucose/', views.log_glucose, name='log_glucose'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('doctor-notes/<int:patient_id>/', views.doctor_notes, name='doctor_notes'),
    path('report/', views.generate_pdf, name='generate_pdf'),
]