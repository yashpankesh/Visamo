from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.shortcuts import render, get_object_or_404
from .models import Hotel,Booking
from .forms import BookingForm
# import paypalrestsdk
from django.conf import settings
import razorpay



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'registration/profile.html')



def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotels/hotel_list.html', {'hotels': hotels})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, 'hotels/hotel_detail.html', {'hotel': hotel})

def about_us(request):
    return render(request, 'about_us.html')

# paypalrestsdk.configure({
#     "mode": "sandbox",  # Use "live" for production
#     "client_id": "AekIjuwYzYKy9_Ph3w1kQEYrB16rSrQqPt0GWReudvY8u68YuGZ6-QtSgWO--VtmrvXl3fGgUoLIJ34o",
#     "client_secret": "EGchlrV6TU9dx5bnkMjwsEZimG-sno9jLs-CLMAfYjw-xN739DsW1A0YXz0N4do9OZHDhBPVhbTSuT9o"
# })

# PAYPAL_CLIENT_ID = 'AekIjuwYzYKy9_Ph3w1kQEYrB16rSrQqPt0GWReudvY8u68YuGZ6-QtSgWO--VtmrvXl3fGgUoLIJ34o'
# PAYPAL_SECRET = 'EGchlrV6TU9dx5bnkMjwsEZimG-sno9jLs-CLMAfYjw-xN739DsW1A0YXz0N4do9OZHDhBPVhbTSuT9o'
# PAYPAL_MODE = 'sandbox'  # Use 'live' for production

@login_required
def book_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel

            if booking.rooms_booked > hotel.available_rooms:
                messages.error(request, "Not enough rooms available!")
            else:
                hotel.available_rooms -= booking.rooms_booked
                hotel.save()
                booking.save()

                # Create Razorpay Order
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                order_amount = int(booking.total_price * 100)  # Convert to paisa
                order_currency = 'INR'
                order_receipt = f"booking_{booking.id}"

                razorpay_order = client.order.create({
                    "amount": order_amount,
                    "currency": order_currency,
                    "receipt": order_receipt,
                    "payment_capture": 1  # Auto-capture payment
                })

                # Save the order ID in the booking
                booking.razorpay_order_id = razorpay_order['id']
                booking.save()

                messages.success(request, "Booking successful! Proceed to payment.")
                return redirect('process_payment', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'booking/book_hotel.html', {'form': form, 'hotel': hotel})

@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    context = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': booking.razorpay_order_id,
        'booking': booking,
        'amount': int(booking.total_price * 100)  # Convert to paisa
    }
    return render(request, 'payment/razorpay_checkout.html', context)

@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    try:
        payment = razorpay_client.payment.fetch(payment_id)
        booking = Booking.objects.get(razorpay_order_id=payment['order_id'])

        if payment['status'] == 'captured':
            booking.status = 'Paid'
            booking.save()
            messages.success(request, "Payment successful!")
        else:
            messages.error(request, "Payment verification failed.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('hotel_list')










# # PayPal Configuration
# paypalrestsdk.configure({
#     "mode": settings.PAYPAL_MODE,  # sandbox or live
#     "client_id": settings.PAYPAL_CLIENT_ID,
#     "client_secret": settings.PAYPAL_SECRET,
# })

# @login_required
# def book_hotel(request, hotel_id):
#     hotel = Hotel.objects.get(id=hotel_id)
#     if request.method == 'POST':
#         form = BookingForm(request.POST)
#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.user = request.user
#             booking.hotel = hotel
#             if booking.rooms_booked > hotel.available_rooms:
#                 messages.error(request, "Not enough rooms available!")
#             else:
#                 hotel.available_rooms -= booking.rooms_booked
#                 hotel.save()
#                 booking.save()
#                 messages.success(request, "Your booking was successful!")
#                 return redirect('book_hotel', hotel_id=hotel.id)
#     else:
#         form = BookingForm()

#     return render(request, 'booking/book_hotel.html', {'form': form, 'hotel': hotel})

# @login_required
# def process_payment(request, booking_id):
#     booking = Booking.objects.get(id=booking_id)

#     # Create PayPal Payment
#     payment = paypalrestsdk.Payment({
#         "intent": "sale",
#         "payer": {
#             "payment_method": "paypal"
#         },
#         "redirect_urls": {
#             "return_url": request.build_absolute_uri('/payment/success/'),
#             "cancel_url": request.build_absolute_uri('/payment/cancel/')
#         },
#         "transactions": [{
#             "amount": {
#                 "total": str(booking.total_price),
#                 "currency": "INR"
#             },
#             "description": f"Booking at {booking.hotel.name}"
#         }]
#     })

#     if payment.create():
#         for link in payment.links:
#             if link.rel == "approval_url":
#                 approval_url = link.href
#                 return redirect(approval_url)
#     else:
#         messages.error(request, "Payment creation failed.")
#         return redirect('hotel_list')

# @login_required
# def payment_success(request):
#     payment_id = request.GET.get('paymentId')
#     payer_id = request.GET.get('PayerID')
#     payment = paypalrestsdk.Payment.find(payment_id)

#     if payment.execute({"payer_id": payer_id}):
#         booking = Booking.objects.get(id=payment.transactions[0].invoice_number)
#         booking.status = 'Paid'
#         booking.save()
#         messages.success(request, "Payment successful!")
#         return redirect('hotel_list')
#     else:
#         messages.error(request, "Payment execution failed.")
#         return redirect('hotel_list')

# @login_required
# def payment_cancel(request):
#     messages.error(request, "Payment was canceled.")
#     return redirect('hotel_list')
