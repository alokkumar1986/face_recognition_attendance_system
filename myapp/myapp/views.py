from  django.shortcuts import redirect, render
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from django.db.models import Q, DateField
from django.db.models.functions import Cast
from datetime import datetime

import pdb

from members.models import Members, Attendance 

def home(request):
    return render(request, 'login.html', {})

def signup(request):
    return render(request, 'sign-up.html', {})

def forgotpassword(request):
    return render(request, 'forgotpassword.html', {})


def register(request):
    name = request.POST['name']
    email = request.POST['email']
    password = '123456'
    phone = request.POST['phone']
    
    if Members.objects.filter(mobile=phone).exists():
        messages.error(request, "This Phone is already in use. Please choose a different mobile number.")
        return redirect('./sign-up')
    else:
        user = Members(name=name, email=email, password=password, mobile=phone)
        user.save()
        messages.success(request, "User is Signed up successfully.")
        return redirect('./sign-up')
    
def login(request):
    password = request.POST['password']
    phone = request.POST['phone']
    if Members.objects.filter(mobile=phone, password=password).exists():
        user = Members.objects.filter(mobile=phone).values().first()
        # print(user)
        # pdb.set_trace()
        if(user):
            request.session['id'] = user['id']
            request.session['name'] = user['name']
            request.session['email'] = user['email']
            request.session['mobile'] = phone
        return redirect('./dashboard')
    else:
       messages.error(request, "Login Failed. Invalid Credentials.")
       return redirect('./') 
   
def logout(request):
    request.session.flush()
    messages.error(request, "You are logged out successfully.")
    return redirect('./') 
   
def dashboard(request):
    if(request.session.get('id')):
      return render(request, 'dashboard.html', {}) 
    else:
      messages.error(request, "Your session is expired or lost.")
      return redirect('./')
  
def setting(request):
    if(request.session.get('id')):
        folder_path = "C:/Users/alok.nayak/Desktop/django project/Face_recognition_based_attendance_system/Attendance" 
        try:
         excel_file_names = get_excel_file_names(folder_path)
        except Exception as e:
         return render(request, "setting.html", {"message": f"Error reading folder: {e}"})
        return render(request, "setting.html", {"excel_data": excel_file_names})
    else:
        messages.error(request, "Your session is expired or lost.")
        return redirect('./')
    
def get_excel_file_names(folder_path):
    excel_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx") or f.endswith(".xls") or f.endswith(".csv")]
    return excel_files

def generate_attendance_report(request):
    if not request.session.get('id'):
        messages.error(request, "Your session is expired or lost.")
        return redirect('./')

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # Convert adate to YYYY-MM-DD format for filtering
    attendance_data = Attendance.objects.filter(
        Q(adate__gte=start_date) &
        Q(adate__lte=end_date)
    )
    # print(Attendance.objects.filter(
    #     Q(adate__gte=datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')) &
    #     Q(adate__lte=datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d'))
    # ).query)    
    
    # print(attendance_data)
    
    if 'download' in request.POST:
        # Create an Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance Report"

        # Add headers
        ws.append(["Serial No", "Date", "Time", "Name"])

        # Add data rows
        for record in attendance_data:
            ws.append([record.serialno, record.adate, record.atime, record.name])

        # Save workbook to a BytesIO stream
        response_stream = BytesIO()
        wb.save(response_stream)
        response_stream.seek(0)

        # Return as a downloadable file
        response = FileResponse(response_stream, as_attachment=True, filename="attendance_report.xlsx")
        return response

    return render(request, "setting.html", {"attendance_data": attendance_data, "fdate": start_date, "tdate": end_date})