from django.urls import path,include
import temple.views
from temple import views  # Import your views file
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('',temple.views.home,name='home'),
    path('home', temple.views.home, name='home'),
    path('register/', temple.views.register, name='register'),
    path('register_admin/', temple.views.register_admin, name='register_admin'),
    path('login/', temple.views.login_view, name='login'),
    path('user_home', temple.views.user_home, name='user_home'),
    path('admin_home', temple.views.admin_home, name='admin_home'),
    path('Logout', temple.views.logout, name='logout'),
    path("feedback/", temple.views.feedback_view, name="submit_feedback"),
    path('birth-star-info/', temple.views.birth_star_info, name='birth_star_info'),
    path('birth-star-detail/<int:star_id>/', temple.views.birth_star_detail, name='birth_star_detail'),
    path('manage_birthstars/', temple.views.manage_birthstars, name='manage_birthstars'),
    path('add_birthstar/', temple.views.add_birthstar, name='add_birthstar'),
    path('edit_birthstar/<int:birthstar_id>/', temple.views.edit_birthstar, name='edit_birthstar'),
    path('delete_birthstar/<int:birthstar_id>/', temple.views.delete_birthstar, name='delete_birthstar'),
    path('book/', temple.views.ritual_booking, name='ritual_booking'),
    path('confirmation/', temple.views.ritual_confirmation, name='ritual_confirmation'),
    path("manage-rituals/", temple.views.manage_rituals, name="manage_rituals"),
    path("delete-ritual/<int:ritual_id>/", temple.views.delete_ritual, name="delete_ritual"),
    path("ritual-booking/", temple.views.ritual_booking, name="ritual_booking"),
    path('pay_ritual/<int:booking_id>/', temple.views.pay_ritual, name='pay_ritual'),
    path('ritual-confirmation/<int:id>/', temple.views.ritual_confirmation, name='ritual_confirmation'),
    path("book-marriage/", temple.views.book_marriage, name="book_marriage"),
    path("get-available-slots/", temple.views.get_available_slots, name="get_available_slots"),
    path('payment/<int:booking_id>/', temple.views.payment_page, name='payment_page'),
    path('marriage-bookings/', temple.views.marriage_bookings, name='marriage_bookings'),
    path('services/', temple.views.service_list, name='service_list'),
    path('add-service/', temple.views.add_service, name='add_service'),
    path('delete-service/', temple.views.delete_service, name='delete_service'),
    path('marriage-bookings/add/', temple.views.add_marriage_booking, name='add_marriage_booking'),
    path('marriage-bookings/edit/<int:booking_id>/', temple.views.edit_marriage_booking, name='edit_marriage_booking'),
    path('marriage-bookings/delete/<int:booking_id>/', temple.views.delete_marriage_booking, name='delete_marriage_booking'),
    path('upload-marriage-certificate/', temple.views.upload_certificate, name='upload_marriage_certificate'),
    path('upload/', temple.views.upload_certificate, name='upload_certificate'),
    path('certificates/', temple.views.user_certificates, name='user_certificates'),
    path('all-certificates/', temple.views.view_all_certificates, name='view_all_certificates'),
    path('download/<int:certificate_id>/', temple.views.download_certificate, name='download_certificate'),
    path('user_certificates/', temple.views.user_certificates, name='user_certificates'),
    path('download_certificate/<int:certificate_id>/', temple.views.download_certificate, name='download_certificate'),
    path('admin/ritual-bookings/', temple.views.ritual_booking_list, name='ritual_booking_list'),
    path('admin/ritual-report/<int:booking_id>/', temple.views.generate_ritual_report, name='ritual_report'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

