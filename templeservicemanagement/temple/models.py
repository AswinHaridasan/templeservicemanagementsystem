from django.contrib.auth.models import User
from django.db import models
from django.views.generic import ListView, DetailView, CreateView


class Registration(models.Model):
    password = models.CharField(max_length=200, null=True)
    user_role = models.CharField(max_length=200, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)



class Feedback(models.Model):
    SERVICE_CHOICES = [
        ("ritual", "Ritual"),
        ("marriage_booking", "Marriage Booking"),
        ("overall_experience", "Overall Experience"),
    ]

    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service} - {self.rating} Stars"



class BirthStar(models.Model):
    nakshathra = models.CharField(max_length=255, unique=True)
    traits = models.TextField(blank=True, null=True)   # Added Traits
    strengths = models.TextField(blank=True, null=True)  # Added Strengths
    ritual = models.TextField(blank=True, null=True)  # Added Ritual

    def __str__(self):
        return self.nakshathra



class Ritual(models.Model):
    ritual = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.ritual

class RitualBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Store the user who booked
    ritual = models.ForeignKey(Ritual, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Completed", "Completed"), ("Failed", "Failed")],
        default="Pending"
    )  # Reintroducing the payment status

    def __str__(self):
        return f"{self.user.username} - {self.ritual.ritual} - {self.payment_status}"


class OptionalService(models.Model):
    service_name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.service_name


class MarriageBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bride_name = models.CharField(max_length=100)
    groom_name = models.CharField(max_length=100)
    date = models.DateField()
    time_slot = models.CharField(max_length=50)
    services = models.ManyToManyField(OptionalService, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Save total amount
    Payment_status = models.CharField(max_length=200, null=True, default="Pending")

    class Meta:
        unique_together = None

    def __str__(self):
        return f"Marriage Booking: {self.bride_name} & {self.groom_name} on {self.date} at {self.time_slot}"


class MarriageCertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bride_name = models.CharField(max_length=255)
    groom_name = models.CharField(max_length=255)
    bride_dob = models.DateField()
    groom_dob = models.DateField()
    marriage_date = models.DateField()
    time_slot = models.CharField(max_length=50, null=True, blank=True)
    certificate_pdf = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"{self.bride_name} & {self.groom_name} - {self.marriage_date} at {self.time_slot}"


