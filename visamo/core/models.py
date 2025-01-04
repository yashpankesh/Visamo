from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    available_rooms = models.PositiveIntegerField()
    image = models.ImageField(upload_to='hotel_images/', null=True, blank=True)

    def __str__(self):
        return self.name



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    rooms_booked = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = self.rooms_booked * self.hotel.price_per_night
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.username} at {self.hotel.name}"
