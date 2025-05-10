from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from .models import User, Doctor, Appointment, Response, OTP
from django.contrib.auth.hashers import make_password, check_password
import logging
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import requests
from django.conf import settings
from django.http import JsonResponse

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'homepage.html')

def signup(request):
    if request.method == 'POST':
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        email = request.POST['email']
        phone = request.POST['phone']
        dob = request.POST['dob']
        password = request.POST['password']
        username = email

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email address already exists!')
            logger.warning(f"Signup failed: Email {email} already exists.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists! Please use a different email.')
            logger.warning(f"Signup failed: Username {username} already exists.")
            return redirect('signup')

        hashed_password = make_password(password)
        try:
            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                dob=dob,
                password=hashed_password
            )
            user.save()
            messages.success(request, 'Account created successfully!')
            logger.info(f"User {email} signed up successfully.")
            return redirect('login')
        except IntegrityError as e:
            messages.error(request, 'An error occurred during signup. Please try again.')
            logger.error(f"IntegrityError during signup for {email}: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')

def generate_otp():
    return str(random.randint(100000, 999999))

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.filter(email=email).first()
        if user:
            logger.debug(f"User found: {email}, stored hash: {user.password}")
            if check_password(password, user.password):
                request.session['pending_user_id'] = user.id
                otp = generate_otp()
                expires_at = timezone.now() + timedelta(minutes=5)
                OTP.objects.create(user=user, otp=otp, expires_at=expires_at)
                send_mail(
                    'Your OTP Code',
                    f'Your OTP is {otp}. It is valid for 5 minutes.',
                    'your-email@gmail.com',
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'OTP sent to your email.')
                logger.info(f"OTP sent to user {email}.")
                return redirect('send_otp', user_type='patient')
            else:
                messages.error(request, 'Invalid password.')
                logger.warning(f"Password mismatch for {email}.")
        else:
            messages.error(request, 'User not found.')
            logger.warning(f"Login failed: No user with email {email}.")
        return redirect('login')

    return render(request, 'login.html')

def doctor_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        doctor = Doctor.objects.filter(email=email).first()
        if doctor:
            logger.debug(f"Doctor found: {email}, stored hash: {doctor.password}")
            if check_password(password, doctor.password):
                request.session['pending_doctor_id'] = doctor.id
                otp = generate_otp()
                expires_at = timezone.now() + timedelta(minutes=5)
                OTP.objects.create(doctor=doctor, otp=otp, expires_at=expires_at)
                send_mail(
                    'Your OTP Code',
                    f'Your OTP is {otp}. It is valid for 5 minutes.',
                    'your-email@gmail.com',
                    [doctor.email],
                    fail_silently=False,
                )
                messages.success(request, 'OTP sent to your email.')
                logger.info(f"OTP sent to doctor {email}.")
                return redirect('send_otp', user_type='doctor')
            else:
                messages.error(request, 'Invalid password.')
                logger.warning(f"Password mismatch for {email}.")
        else:
            messages.error(request, 'Doctor not found.')
            logger.warning(f"Doctor login failed: No doctor with email {email}.")
        return redirect('doclog')

    return redirect('doclog')

def send_otp(request, user_type):
    if user_type not in ['patient', 'doctor']:
        messages.error(request, 'Invalid user type.')
        logger.warning(f"Invalid user_type in send_otp: {user_type}")
        return redirect('index')

    if request.method == 'POST':
        if user_type == 'patient' and 'pending_user_id' in request.session:
            user = User.objects.get(id=request.session['pending_user_id'])
            otp = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            OTP.objects.create(user=user, otp=otp, expires_at=expires_at)
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}. It is valid for 5 minutes.',
                'your-email@gmail.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'OTP resent to your email.')
            logger.info(f"OTP resent to user {user.email}.")
        elif user_type == 'doctor' and 'pending_doctor_id' in request.session:
            doctor = Doctor.objects.get(id=request.session['pending_doctor_id'])
            otp = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            OTP.objects.create(doctor=doctor, otp=otp, expires_at=expires_at)
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}. It is valid for 5 minutes.',
                'your-email@gmail.com',
                [doctor.email],
                fail_silently=False,
            )
            messages.success(request, 'OTP resent to your email.')
            logger.info(f"OTP resent to doctor {doctor.email}.")
        return redirect('verify_otp', user_type=user_type)

    return render(request, 'send_otp.html', {'user_type': user_type})

def verify_otp(request, user_type):
    if user_type not in ['patient', 'doctor']:
        messages.error(request, 'Invalid user type.')
        logger.warning(f"Invalid user_type in verify_otp: {user_type}")
        return redirect('index')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if user_type == 'patient' and 'pending_user_id' in request.session:
            user = User.objects.get(id=request.session['pending_user_id'])
            try:
                otp_obj = OTP.objects.filter(user=user, otp=entered_otp).latest('created_at')
                if otp_obj.is_expired():
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    logger.warning(f"Expired OTP for user {user.email}.")
                    return redirect('send_otp', user_type='patient')
                login(request, user)
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                request.session.pop('pending_user_id', None)
                otp_obj.delete()
                messages.success(request, 'Logged in successfully!')
                logger.info(f"User {user.email} logged in after OTP verification.")
                return redirect('patient_page')
            except OTP.DoesNotExist:
                messages.error(request, 'Invalid OTP.')
                logger.warning(f"Invalid OTP for user {user.email}.")
        elif user_type == 'doctor' and 'pending_doctor_id' in request.session:
            doctor = Doctor.objects.get(id=request.session['pending_doctor_id'])
            try:
                otp_obj = OTP.objects.filter(doctor=doctor, otp=entered_otp).latest('created_at')
                if otp_obj.is_expired():
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    logger.warning(f"Expired OTP for doctor {doctor.email}.")
                    return redirect('send_otp', user_type='doctor')
                request.session['doctor_id'] = doctor.id
                request.session.pop('pending_doctor_id', None)
                otp_obj.delete()
                messages.success(request, 'Logged in successfully!')
                logger.info(f"Doctor {doctor.email} logged in after OTP verification.")
                return redirect('doctor_book')
            except OTP.DoesNotExist:
                messages.error(request, 'Invalid OTP.')
                logger.warning(f"Invalid OTP for doctor {doctor.email}.")
        else:
            messages.error(request, 'Session expired. Please try logging in again.')
            logger.warning(f"Session expired for {user_type} OTP verification.")
            return redirect('login' if user_type == 'patient' else 'doclog')

    return render(request, 'verify_otp.html', {'user_type': user_type})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        request.session.flush()
        messages.info(request, 'You have been logged out successfully.')
        logger.info("User logged out.")
        return HttpResponse('', status=204)
    return redirect('index')

@login_required
def patient_page(request):
    user = request.user
    return render(request, 'patientpage.html', {'user': user})

@login_required
def searchbar(request):
    query = request.GET.get('query', '')
    location = request.GET.get('location', 'York, PA 17403')
    sort_by = request.GET.get('sort_by', '')
    rating_filter = request.GET.get('rating_filter', '')
    new_patients = request.GET.get('new_patients', '')

    doctors = Doctor.objects.all()
    if query:
        doctors = doctors.filter(
            Q(speciality__icontains=query) |
            Q(name__icontains=query)
        )
    if rating_filter:
        try:
            doctors = doctors.filter(rating__gte=float(rating_filter))
        except ValueError:
            logger.warning(f"Invalid rating_filter value: {rating_filter}")
            messages.error(request, 'Invalid rating filter.')

    if sort_by == 'distance':
        doctors = doctors.order_by('distance')
    elif sort_by == 'rating':
        doctors = doctors.order_by('-rating')
    elif sort_by == 'relevance':
        pass

    context = {
        'query': query,
        'location': location,
        'doctors': doctors,
        'sort_by': sort_by,
        'rating_filter': rating_filter,
        'new_patients': new_patients,
    }
    logger.debug(f"Searchbar query: {query}, location: {location}, doctors found: {doctors.count()}")
    return render(request, 'searchbar.html', context)

def doctordes(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    context = {'doctor': doctor}
    logger.debug(f"Viewing doctor profile: {doctor.name} (ID: {doctor_id})")
    return render(request, 'doctordes.html', context)

@login_required
def request_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        requested_date = request.POST.get('requested_date')
        if doctor_id and requested_date:
            try:
                appointment = Appointment(
                    patient=request.user,
                    doctor_id=doctor_id,
                    requested_date=requested_date,
                    status='Pending'
                )
                appointment.save()
                messages.success(request, 'Appointment requested successfully!')
                logger.info(f"Appointment requested: User {request.user.email}, Doctor ID {doctor_id}, Date {requested_date}")
                return redirect('patient_page')
            except Exception as e:
                messages.error(request, 'Failed to request appointment.')
                logger.error(f"Appointment request failed: {str(e)}")
        else:
            messages.error(request, 'Invalid request data.')
            logger.warning(f"Invalid appointment request: doctor_id={doctor_id}, requested_date={requested_date}")
    return redirect('searchbar')

@login_required
def user_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).select_related('patient')
    return render(request, 'user_appointments.html', {'appointments': appointments})

def doclog(request):
    return render(request, 'logindoctorpage.html')

def register_doctor(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST.get('name', '')
        speciality = request.POST.get('speciality', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        experience = request.POST.get('experience', 0)
        rating = request.POST.get('rating', 0.0)
        rating_count = request.POST.get('rating_count', 0)
        virtual_visit = request.POST.get('virtual_visit', False)
        image_url = request.POST.get('image_url', 'images/d10.jpg')
        distance = request.POST.get('distance', 0.0)

        if Doctor.objects.filter(email=email).exists():
            messages.error(request, 'Doctor with this email already exists!')
            logger.warning(f"Doctor registration failed: Email {email} already exists.")
            return redirect('register_doctor')

        hashed_password = make_password(password)
        try:
            doctor = Doctor(
                email=email,
                password=hashed_password,
                name=name,
                speciality=speciality,
                address=address,
                phone=phone,
                experience=experience,
                rating=rating,
                rating_count=rating_count,
                virtual_visit=virtual_visit,
                image_url=image_url,
                distance=distance
            )
            doctor.save()
            messages.success(request, 'Doctor registered successfully!')
            logger.info(f"Doctor {email} registered successfully.")
            return redirect('doclog')
        except Exception as e:
            messages.error(request, 'Failed to register doctor.')
            logger.error(f"Doctor registration failed: {str(e)}")
            return redirect('register_doctor')

    return render(request, 'register_doctor.html')

def doctor_book(request):
    if 'doctor_id' not in request.session:
        messages.error(request, 'You need to log in first!')
        logger.warning("Doctor book access denied: Not logged in.")
        return redirect('doclog')

    appointments = Appointment.objects.select_related('patient').all()
    return render(request, 'doctor_book.html', {'appointments': appointments})

def doctor_logout(request):
    request.session.pop('doctor_id', None)
    messages.info(request, 'You have been logged out successfully.')
    logger.info("Doctor logged out.")
    return redirect('doclog')

@login_required
def update_appointment(request, appointment_id):
    if 'doctor_id' not in request.session:
        messages.error(request, 'You need to log in as a doctor first!')
        logger.warning("Update appointment access denied: Not logged in as doctor.")
        return redirect('doclog')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        new_date = request.POST.get('new_date')

        appointment.status = status
        if status == 'Rescheduled' and new_date:
            appointment.new_date = new_date
        else:
            appointment.new_date = None

        try:
            appointment.save()
            messages.success(request, 'Appointment updated successfully!')
            logger.info(f"Appointment {appointment_id} updated: status={status}, new_date={new_date}")
            Response.objects.create(
                status=status,
                new_date=new_date or '',
                appointment=appointment
            )

            # If appointment is accepted, generate and send lab report
            if status == 'Accepted':
                doctor = Doctor.objects.get(id=appointment.doctor_id)
                form_data = {
                    'patient_email': appointment.patient.email,
                    'doctor_id': str(appointment.doctor_id),
                    'doctor_speciality': doctor.speciality
                }
                try:
                    flask_api_url = 'http://localhost:5002/submit_lab_report'
                    response = requests.post(flask_api_url, data=form_data)
                    if response.status_code == 200:
                        logger.info(f"Lab report generated for patient {appointment.patient.email}, doctor {doctor.name}")
                    else:
                        logger.error(f"Failed to generate lab report: {response.text}")
                        messages.error(request, 'Failed to generate lab report.')
                except requests.RequestException as e:
                    logger.error(f"Lab report API request failed: {str(e)}")
                    messages.error(request, 'Lab report API request failed.')

            return redirect('doctor_book')
        except Exception as e:
            messages.error(request, 'Failed to update appointment.')
            logger.error(f"Failed to update appointment {appointment_id}: {str(e)}")
            return redirect('doctor_book')

    return render(request, 'update_appointment.html', {'appointment': appointment})

def response_view(request):
    status = request.GET.get('status')
    new_date = request.GET.get('new_date')

    if status and new_date:
        try:
            response = Response(status=status, new_date=new_date)
            response.save()
            logger.info(f"Response created: status={status}, new_date={new_date}")
        except Exception as e:
            logger.error(f"Failed to create response: {str(e)}")

    return render(request, 'response.html', {'status': status, 'new_date': new_date})

def About_Us(request):
    return render(request, 'About_Us.html')

def Contact_us(request):
    if request.method == 'POST':
        try:
            logger.info("Received POST request to contact_us")
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            message = request.POST.get('message')
            agree_terms = request.POST.get('agreeTerms') == 'on'

            logger.debug(f"Form data: name={name}, email={email}, phone={phone}, address={address}, message={message}, agree_terms={agree_terms}")

            if not all([name, email, phone, address, agree_terms]):
                logger.warning("Validation failed: Missing required fields")
                return JsonResponse({'error': 'All required fields must be filled'}, status=400)

            form_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'message': message,
                'agreeTerms': 'on' if agree_terms else ''
            }

            flask_api_url = 'http://localhost:5001/submit_contact'
            logger.info(f"Sending POST request to {flask_api_url}")
            response = requests.post(flask_api_url, data=form_data)

            if response.status_code == 200:
                logger.info("Successfully saved contact via Flask API")
                subject = 'Thank You for Contacting Swift Care'
                email_message = (
                    f"Dear {name},\n\n"
                    "Thanks for contacting us, we will get in touch with you soon.\n\n"
                    "Best regards,\nSwift Care Team"
                )
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]

                send_mail(
                    subject,
                    email_message,
                    email_from,
                    recipient_list,
                    fail_silently=False,
                )
                logger.info(f"Confirmation email sent to {email}")

                return JsonResponse({'message': 'Contact information submitted and email sent successfully'})
            else:
                logger.error(f"Flask API error: {response.text}")
                return JsonResponse({'error': response.json().get('error', 'Failed to save contact information')}, status=response.status_code)

        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"Error in contact_us: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    logger.info("Rendering Contact_Us.html")
    return render(request, 'Contact_Us.html')

@login_required
def lab_reports(request):
    try:
        flask_api_url = f'http://localhost:5002/get_lab_reports/{request.user.email}'
        response = requests.get(flask_api_url)
        if response.status_code == 200:
            lab_reports = response.json().get('lab_reports', [])
            logger.info(f"Retrieved {len(lab_reports)} lab reports for user {request.user.email}")
            return render(request, 'lab_reports.html', {'lab_reports': lab_reports})
        else:
            logger.error(f"Failed to retrieve lab reports: {response.text}")
            messages.error(request, 'Failed to retrieve lab reports.')
            return render(request, 'lab_reports.html', {'lab_reports': []})
    except requests.RequestException as e:
        logger.error(f"Lab reports API request failed: {str(e)}")
        messages.error(request, 'Failed to retrieve lab reports.')
        return render(request, 'lab_reports.html', {'lab_reports': []})