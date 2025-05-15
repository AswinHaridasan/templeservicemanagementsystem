from .models import *
import stripe
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import auth
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.template.loader import get_template
from io import BytesIO
from django.http import FileResponse, Http404
from xhtml2pdf import pisa

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os
from django.conf import settings
from django.core.files import File
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MarriageCertificate, MarriageBooking
from .utils import generate_certificate_pdf  # Ensure this function is correct


def home(request):
    return render(request,'index.html')


def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        mgn = Registration.objects.all()
        for w in mgn:
            if w.user.email == email and w.user_role == 'user':
                messages.success(request, 'You have already registered. Please login')
                return redirect('register')
        psw = request.POST.get('password')
        user_name = request.POST.get('username')
        for t in User.objects.all():
            if t.username == user_name:
                messages.success(request, 'Username taken. Please try another')
                return redirect('register')

        user = User.objects.create_user(username = user_name, email = email, password = psw, first_name = first_name, last_name = last_name)
        user.save()

        reg = Registration()
        reg.password = password
        reg.user_role = 'user'
        reg.user = user
        reg.save()
        messages.success(request, 'You have successfully registered as user')
        return redirect('home')
    else:
        return render(request, 'register.html')



def register_admin(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        mgn = Registration.objects.all()
        for w in mgn:
            if w.user.email == email and w.user_role == 'user':
                messages.success(request, 'You have already registered. Please login')
                return redirect('register_admin')
        psw = request.POST.get('password')
        user_name = request.POST.get('username')
        for t in User.objects.all():
            if t.username == user_name:
                messages.success(request, 'Username taken. Please try another')
                return redirect('register_admin')

        user = User.objects.create_user(username = username, email = email, password = psw, first_name = first_name, last_name = last_name)
        user.save()

        reg = Registration()
        reg.password = password
        reg.user_role = 'admin'
        reg.user = user
        reg.save()
        messages.success(request, 'You have successfully registered as admin')
        return redirect('home')
    else:
        return render(request, 'register_admin.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password=password)
        if user is None:
            messages.success(request,'Invalid credentials')
            return redirect('login')
        auth.login(request, user)
        kmk = Registration.objects.get(user = user)
        jhj = str(kmk.user_role)
        sws = int(kmk.id)
        if jhj == 'user':
            request.session['logg'] = sws
            return redirect('user_home')
        elif jhj == 'admin':
            request.session['logg'] = sws
            return redirect('admin_home')
        else:
            messages.success(request, 'Your access to the website is blocked. Please contact admin')
            return redirect('login')
    return render(request, 'login.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="home")
def user_home(request):
    certificates = MarriageCertificate.objects.filter(user=request.user)  # Fetch all certificates for the logged-in user

    return render(request, 'user_home.html', {'certificates': certificates})




def logout(request):
    auth.logout(request)
    request.session.flush()
    return redirect('home')


@staff_member_required  # Only allows admin users
def admin_home(request):
    return render(request, 'admin_home.html')



def feedback_view(request):
    if request.method == "POST":
        service = request.POST.get("service")
        rating = request.POST.get("rating")
        comments = request.POST.get("comments")

        Feedback.objects.create(service=service, rating=rating, comments=comments)

        return HttpResponse("✅ Feedback submitted successfully!")

    return render(request, "feedback.html")

def birth_star_info(request):
    stars = BirthStar.objects.all()
    return render(request, 'birth_star_info.html', {'stars': stars})


def birth_star_detail(request, star_id):
    star = get_object_or_404(BirthStar, id=star_id)
    return render(request, 'birth_star_detail.html', {'star': star})


def manage_birthstars(request):
    birthstars = BirthStar.objects.all()
    return render(request, 'manage_birthstars.html', {'birthstars': birthstars})


def add_birthstar(request):
    if request.method == "POST":
        nakshathra = request.POST.get('nakshathra', '')
        traits = request.POST.get('traits', '')
        strengths = request.POST.get('strengths', '')
        ritual = request.POST.get('ritual', '')

        # Check if Nakshathra already exists
        if BirthStar.objects.filter(nakshathra=nakshathra).exists():
            return render(request, 'add_birthstar.html', {
                'error_message': f'Birth Star "{nakshathra}" already exists!',
            })

        try:
            BirthStar.objects.create(
                nakshathra=nakshathra, traits=traits, strengths=strengths, ritual=ritual
            )
            return redirect('manage_birthstars')

        except IntegrityError:
            return render(request, 'add_birthstar.html', {
                'error_message': 'An error occurred while saving. Please try again.'
            })

    return render(request, 'add_birthstar.html')


def edit_birthstar(request, birthstar_id):
    birthstar = get_object_or_404(BirthStar, id=birthstar_id)

    if request.method == "POST":
        birthstar.nakshathra = request.POST.get('nakshathra', '')
        birthstar.traits = request.POST.get('traits', '')
        birthstar.strengths = request.POST.get('strengths', '')
        birthstar.ritual = request.POST.get('ritual', '')

        birthstar.save()

        return redirect('manage_birthstars')

    return render(request, 'edit_birthstar.html', {'birthstar': birthstar})


def delete_birthstar(request, birthstar_id):
    birthstar = get_object_or_404(BirthStar, id=birthstar_id)
    birthstar.delete()
    return redirect('manage_birthstars')



@login_required
def manage_rituals(request):
    rituals = Ritual.objects.all()

    if request.method == "POST":
        ritual_name = request.POST.get("ritual")
        amount = request.POST.get("amount")

        if ritual_name and amount:
            Ritual.objects.create(ritual=ritual_name, amount=amount)
            return redirect("manage_rituals")  # Refresh Page

    return render(request, "manage_rituals.html", {"rituals": rituals})


@login_required
def delete_ritual(request, ritual_id):
    ritual = get_object_or_404(Ritual, id=ritual_id)
    ritual.delete()
    return redirect("manage_rituals")

# User: Ritual Booking
@login_required
def ritual_booking(request):
    rituals = Ritual.objects.all()

    if request.method == "POST":
        ritual_id = request.POST.get("ritual_id")

        if ritual_id:
            try:
                selected_ritual = Ritual.objects.get(id=int(ritual_id))

                # Save booking with "Pending" payment status
                booking = RitualBooking.objects.create(
                    user=request.user,
                    ritual=selected_ritual,
                    payment_status="Pending"
                )

                # Store booking details in session
                request.session["selected_ritual"] = selected_ritual.ritual
                request.session["selected_amount"] = str(selected_ritual.amount)
                request.session["payment_status"] = "Pending"

                # Send confirmation email
                subject = "Ritual Booking Confirmation"
                message = f"""
                Dear {request.user.username},

                You have successfully booked the ritual: {selected_ritual.ritual}.
                Amount: ${selected_ritual.amount}
                Payment Status: Pending

                Please complete the payment to confirm your booking.

                Thank you!
                """
                from_email = "aswinharidasan6777@gmail.com"
                recipient_list = [request.user.email]

                send_mail(subject, message, from_email, recipient_list)

                messages.success(request, "Booking successful! A confirmation email has been sent.")
                return redirect("ritual_confirmation")

            except Ritual.DoesNotExist:
                messages.error(request, "Invalid ritual selection.")

    return render(request, "ritual_booking.html", {"rituals": rituals})




@login_required
def pay_ritual(request, booking_id):
    booking = get_object_or_404(RitualBooking, id=booking_id, user=request.user)

    # Update payment status
    booking.payment_status = "Completed"
    booking.save()

    # Update session data
    request.session["payment_status"] = "Completed"

    # Send confirmation email
    subject = "Payment Confirmation - Ritual Booking"
    message = (
        f"Dear {request.user.username},\n\n"
        f"Your payment for the ritual '{booking.ritual.ritual}' has been successfully completed.\n"
        f"Amount Paid: ${booking.ritual.amount}\n\n"
        "Thank you for your booking!\n"
        "Temple Service Team"
    )
    recipient_email = request.user.email  # User's email
    sender_email = settings.DEFAULT_FROM_EMAIL  # Email configured in settings.py

    try:
        send_mail(subject, message, sender_email, [recipient_email])
        messages.success(request, "Payment successful! A confirmation email has been sent.")
    except Exception as e:
        messages.warning(request, "Payment successful, but email could not be sent.")

    return redirect("ritual_confirmation")


def ritual_confirmation(request):
    selected_ritual = request.session.get("selected_ritual", None)
    selected_amount = request.session.get("selected_amount", None)

    booking = RitualBooking.objects.filter(ritual__ritual=selected_ritual).last()

    return render(request, "ritual_confirmation.html", {
        "ritual": selected_ritual,
        "amount": selected_amount,
        "booking": booking
    })




def get_available_slots(request):
    date = request.GET.get("date")

    if not date:
        return JsonResponse({"error": "Date is required"}, status=400)

    all_slots = ["Morning (9:00 to 10:00AM)", "Morning (10:00 to 11:00AM)"]

    # Count bookings for each time slot on the selected date
    booked_slots_count = {}
    for slot in all_slots:
        count = MarriageBooking.objects.filter(date=date, time_slot=slot).count()
        booked_slots_count[slot] = count

    # Keep slots that have less than 2 bookings
    available_slots = [slot for slot, count in booked_slots_count.items() if count < 1]

    # If no slots are available, return "Fully Booked"
    if not available_slots:
        return JsonResponse({"available_slots": ["Fully Booked"]})

    return JsonResponse({"available_slots": available_slots})



@login_required
def book_marriage(request):
    services = OptionalService.objects.all()

    if request.method == "POST":
        bride_name = request.POST.get('bride_name')
        groom_name = request.POST.get('groom_name')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        selected_services = request.POST.getlist('services')

        # Check if the slot is already fully booked (Max 2 bookings per slot)
        existing_bookings = MarriageBooking.objects.filter(date=date, time_slot=time_slot).count()
        if existing_bookings >= 2:
            return JsonResponse({"error": "This time slot is fully booked. Please choose another slot."}, status=400)

        # Prevent user from booking the same slot twice
        if MarriageBooking.objects.filter(user=request.user, date=date, time_slot=time_slot).exists():
            return JsonResponse({"error": "You have already booked this slot on this date."}, status=400)

        try:
            # Create a booking instance
            booking = MarriageBooking.objects.create(
                user=request.user,
                bride_name=bride_name,
                groom_name=groom_name,
                date=date,
                time_slot=time_slot
            )

            # Add selected services and calculate total price
            total_price = 0
            service_details = []
            for service_id in selected_services:
                try:
                    service = OptionalService.objects.get(id=service_id)
                    booking.services.add(service)
                    total_price += service.price
                    service_details.append(f"{service.service_name} - ${service.price}")
                except OptionalService.DoesNotExist:
                    return JsonResponse({"error": f"Service ID {service_id} does not exist."}, status=400)

            # Send confirmation email
            subject = "Marriage Booking Confirmation"
            message = f"""
            Dear {request.user.first_name},

            Your marriage slot has been successfully booked.

            Bride: {bride_name}
            Groom: {groom_name}
            Date: {date}
            Time Slot: {time_slot}

            Selected Services:
            {", ".join(service_details)}

            Total Amount: ${total_price}

            Thank you for booking with us!

            Regards,
            Marriage Registration Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )

            return redirect('payment_page', booking_id=booking.id)

        except IntegrityError:
            return JsonResponse({"error": "Something went wrong. Please try again."}, status=500)

    return render(request, 'book_marriage.html', {'services': services})


@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(MarriageBooking, id=booking_id)

    total_price = sum(service.price for service in booking.services.all())  # Calculate total price

    if request.method == "POST":
        booking.total_amount = total_price
        booking.Payment_status = "Paid"
        booking.save()

        # Send Payment Confirmation Email
        subject = "Payment Confirmation - Marriage Booking"
        message = f"""
        Dear {booking.user.first_name},

        Your payment has been successfully received.

        Bride: {booking.bride_name}
        Groom: {booking.groom_name}
        Date: {booking.date}
        Time Slot: {booking.time_slot}

        Selected Services:
        {", ".join([service.service_name for service in booking.services.all()])}

        Total Amount Paid: ${total_price}

        Thank you for choosing our service!

        Regards,
        Marriage Registration Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            fail_silently=False,
        )

        return JsonResponse({"message": "Payment Successful! Email sent. Redirecting to home page..."})

    return render(request, 'payment.html', {"booking": booking, "total_price": total_price})


@login_required
def marriage_bookings(request):
    bookings = MarriageBooking.objects.all()
    return render(request, 'adm_marriage_bookings.html', {'bookings': bookings})


@login_required
def add_marriage_booking(request):
    services = OptionalService.objects.all()
    if request.method == "POST":
        bride_name = request.POST.get("bride_name")
        groom_name = request.POST.get("groom_name")
        date = request.POST.get("date")
        time_slot = request.POST.get("time_slot")
        selected_services = request.POST.getlist("services")

        booking = MarriageBooking.objects.create(
            user=request.user,
            bride_name=bride_name,
            groom_name=groom_name,
            date=date,
            time_slot=time_slot
        )

        for service_id in selected_services:
            service = OptionalService.objects.get(id=service_id)
            booking.services.add(service)

        return redirect("marriage_bookings")
    return render(request, "adm_add_marriage_booking.html", {"services": services})


@login_required
def edit_marriage_booking(request, booking_id):
    booking = get_object_or_404(MarriageBooking, id=booking_id)
    services = OptionalService.objects.all()
    if request.method == "POST":
        booking.bride_name = request.POST.get("bride_name")
        booking.groom_name = request.POST.get("groom_name")
        booking.date = request.POST.get("date")
        booking.time_slot = request.POST.get("time_slot")
        booking.services.clear()
        selected_services = request.POST.getlist("services")
        for service_id in selected_services:
            service = OptionalService.objects.get(id=service_id)
            booking.services.add(service)
        booking.save()
        return redirect("marriage_bookings")
    return render(request, "adm_edit_marriage_booking.html", {"booking": booking, "services": services})


@login_required
def delete_marriage_booking(request, booking_id):
    booking = get_object_or_404(MarriageBooking, id=booking_id)
    booking.delete()
    return redirect("marriage_bookings")

def service_list(request):
    services = OptionalService.objects.all()
    return render(request, 'service_list.html', {'services': services})

@csrf_exempt
def add_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_name = data.get('service_name')
            price = data.get('price')

            # Check if service already exists
            if OptionalService.objects.filter(service_name=service_name).exists():
                return JsonResponse({"success": False, "error": "Service already exists!"})

            # Create new service
            new_service = OptionalService.objects.create(
                service_name=service_name,
                price=price
            )
            return JsonResponse({"success": True, "id": new_service.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def delete_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_id = data.get('service_id')

            service = OptionalService.objects.get(id=service_id)
            service.delete()

            return JsonResponse({"success": True})
        except OptionalService.DoesNotExist:
            return JsonResponse({"success": False, "error": "Service not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})





def generate_certificate_pdf(certificate):
    template = get_template('certificate_template.html')
    html_content = template.render({'certificate': certificate})

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        print("[ERROR] PDF Generation Failed")  # Debugging
        return None

    certificate_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(certificate_dir, exist_ok=True)

    pdf_path = os.path.join(certificate_dir, f'certificate_{certificate.id}.pdf')

    # Save PDF
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(pdf_buffer.getvalue())

    print("[DEBUG] PDF Saved Successfully at:", pdf_path)  # Debugging
    return pdf_path




def upload_certificate(request):
    """Handles marriage certificate form submission, PDF generation, and email notification."""
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return HttpResponse("You must be logged in to upload a certificate!", status=401)

            # Retrieve form data
            bride_name = request.POST.get('bride_name', '').strip()
            groom_name = request.POST.get('groom_name', '').strip()
            bride_dob = request.POST.get('bride_dob', '').strip()
            groom_dob = request.POST.get('groom_dob', '').strip()
            marriage_date = request.POST.get('marriage_date', '').strip()
            time_slot = request.POST.get('time_slot', '').strip()

            # Validate fields
            if not bride_name or not groom_name or not bride_dob or not groom_dob or not marriage_date:
                return HttpResponse("All fields are required!", status=400)

            # Convert date strings to date objects
            bride_dob = datetime.strptime(bride_dob, '%Y-%m-%d').date()
            groom_dob = datetime.strptime(groom_dob, '%Y-%m-%d').date()
            marriage_date = datetime.strptime(marriage_date, '%Y-%m-%d').date()

            # Check for existing MarriageBooking
            booking = MarriageBooking.objects.filter(
                bride_name=bride_name,
                groom_name=groom_name,
                date=marriage_date,
                time_slot=time_slot
            ).first()

            if not booking:
                return HttpResponse("No matching marriage booking found!", status=404)

            user = booking.user  # Assign the correct user

            # Save certificate data in the database
            certificate = MarriageCertificate.objects.create(
                user=user,
                bride_name=bride_name,
                groom_name=groom_name,
                bride_dob=bride_dob,
                groom_dob=groom_dob,
                marriage_date=marriage_date,
                time_slot=time_slot
            )

            # Generate and save PDF
            pdf_path = generate_certificate_pdf(certificate)

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    certificate.certificate_pdf.save(os.path.basename(pdf_path), File(pdf_file))
                certificate.save()
            else:
                return HttpResponse("Error generating PDF", status=500)

            # 📧 Send Email Notification
            subject = "Your Marriage Certificate is Ready!"
            download_url = request.build_absolute_uri(certificate.certificate_pdf.url)
            message = f"""
            Dear {user.username},
            
            Your marriage certificate has been successfully generated.

            You can download now from your website

            Thank you!
            """
            from_email = "aswinharidasan6777@gmail.com"  # Replace with your email
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, "Certificate uploaded and email sent successfully!")

            return redirect('user_certificates')

        except Exception as e:
            print(f"[ERROR] Exception while saving certificate: {str(e)}")
            return HttpResponse("Internal Server Error", status=500)

    return render(request, 'upload_certificate.html')




def user_certificates(request):
    if not request.user.is_authenticated:
        print("[ERROR] User not authenticated")
        raise Http404("User not authenticated")


    try:
        # Fetch only the certificates for the logged-in user
        certificates = MarriageCertificate.objects.filter(user=request.user)


        if not certificates.exists():
            print(f"[INFO] No certificates found for user: {request.user}")
            certificates = MarriageCertificate.objects.filter()

    except MarriageCertificate.DoesNotExist:
        print(f"[ERROR] No marriage certificates found for user: {request.user}")
        certificates = []

    return render(request, 'user_certificates.html', {'certificates': certificates})


def download_certificate(request, certificate_id):
    if not request.user.is_authenticated:
        print("[ERROR] User not authenticated")
        raise Http404("User not authenticated")

    certificate = get_object_or_404(MarriageCertificate, id=certificate_id) ##

    if not certificate.certificate_pdf:
        print("[ERROR] Certificate file is missing in DB")
        raise Http404("Certificate file not found")

    file_path = os.path.join(settings.MEDIA_ROOT, str(certificate.certificate_pdf))
    print("[DEBUG] File Path:", file_path)  # Debugging

    if not os.path.exists(file_path):
        print("[ERROR] File does not exist at path")  # Debugging
        raise Http404("Certificate file not found")

    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(file_path),
        content_type='application/pdf'
    )

def some_view(request):
    return redirect(reverse('certificate-list'))

from django.shortcuts import render
from temple.models import MarriageCertificate


def view_all_certificates(request):
    if not request.user.is_staff:  # Only allow admins to view all certificates
        return HttpResponse("Access Denied", status=403)

    certificates = MarriageCertificate.objects.all()  # Fetch all certificates
    return render(request, 'view_all_certificates.html', {'certificates': certificates})


def ritual_booking_list(request):
    """View to list all ritual bookings."""
    bookings = RitualBooking.objects.all()  # Fetch all bookings
    return render(request, 'admin_ritual_bookings.html', {'bookings': bookings})


def generate_ritual_report(request, booking_id):
    """Generate and download a PDF report for a ritual booking."""
    booking = get_object_or_404(RitualBooking, id=booking_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ritual_booking_{booking_id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    pdf.drawString(200, 750, "Ritual Booking Report")
    pdf.line(200, 745, 400, 745)

    pdf.drawString(100, 700, f"User: {booking.user.username}")
    pdf.drawString(100, 680, f"Ritual: {booking.ritual.ritual}")
    pdf.drawString(100, 660, f"Booked At: {booking.booked_at.strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(100, 640, f"Payment Status: {booking.payment_status}")

    pdf.showPage()
    pdf.save()

    return response