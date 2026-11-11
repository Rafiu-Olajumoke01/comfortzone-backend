import hashlib
import hmac
import json
import uuid
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from bookings.serializers import BookingSerializer

from bookings.models import Booking

from .models import Payment, PaymentAccount
from .serializers import PaymentAccountSerializer

PAYSTACK_URL = "https://api.paystack.co"


def paystack_headers():
    return {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}


def mark_success(payment):
    if payment.status != Payment.Status.SUCCESS:
        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])


class PaymentAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        account = PaymentAccount.objects.filter(is_active=True).first()
        if not account:
            return Response({"detail": "No payment account has been set."}, status=404)
        return Response(PaymentAccountSerializer(account).data)


class InitializePaymentView(APIView):
    def post(self, request):
        booking = get_object_or_404(Booking, pk=request.data.get("booking"), customer=request.user)
        if booking.status == Booking.Status.CANCELLED:
            return Response({"detail": "This booking is cancelled."}, status=400)
        if booking.payments.filter(status=Payment.Status.SUCCESS).exists():
            return Response({"detail": "This booking is already paid."}, status=400)

        amount = booking.service.price
        reference = f"CZ-{booking.id}-{uuid.uuid4().hex[:10]}"
        try:
            res = requests.post(
                f"{PAYSTACK_URL}/transaction/initialize",
                headers=paystack_headers(),
                json={
                    "email": request.user.email,
                    "amount": int(amount * 100),
                    "reference": reference,
                    "callback_url": f"{settings.FRONTEND_URL}/payment/verify",
                },
                timeout=20,
            )
            data = res.json()
        except (requests.RequestException, ValueError):
            return Response({"detail": "Could not reach Paystack."}, status=502)

        if not res.ok or not data.get("status"):
            return Response({"detail": data.get("message", "Could not start payment.")}, status=502)

        Payment.objects.create(booking=booking, reference=reference, amount=amount)
        return Response(
            {"authorization_url": data["data"]["authorization_url"], "reference": reference}
        )


class QuickPayView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        email = str(request.data.get("email", "")).strip()
        phone = str(request.data.get("phone", "")).strip()

        try:
            amount = Decimal(str(request.data.get("amount", "")))
        except InvalidOperation:
            return Response({"detail": "Enter a valid amount."}, status=400)

        if not name or not email:
            return Response({"detail": "Name and email are required."}, status=400)
        if amount < 100:
            return Response({"detail": "Minimum amount is ₦100."}, status=400)

        reference = f"CZ-QP-{uuid.uuid4().hex[:12]}"
        try:
            res = requests.post(
                f"{PAYSTACK_URL}/transaction/initialize",
                headers=paystack_headers(),
                json={
                    "email": email,
                    "amount": int(amount * 100),
                    "reference": reference,
                    "callback_url": f"{settings.FRONTEND_URL}/pay/verify",
                },
                timeout=20,
            )
            data = res.json()
        except (requests.RequestException, ValueError):
            return Response({"detail": "Could not reach Paystack."}, status=502)

        if not res.ok or not data.get("status"):
            return Response({"detail": data.get("message", "Could not start payment.")}, status=502)

        Payment.objects.create(
            reference=reference,
            amount=amount,
            payer_name=name,
            payer_email=email,
            payer_phone=phone,
        )
        return Response(
            {"authorization_url": data["data"]["authorization_url"], "reference": reference}
        )


class VerifyPaymentView(APIView):
    def get(self, request, reference):
        payment = get_object_or_404(Payment, reference=reference, booking__customer=request.user)
        if payment.status != Payment.Status.SUCCESS:
            try:
                res = requests.get(
                    f"{PAYSTACK_URL}/transaction/verify/{reference}",
                    headers=paystack_headers(),
                    timeout=20,
                )
                data = res.json()
            except (requests.RequestException, ValueError):
                return Response({"detail": "Could not reach Paystack."}, status=502)

            info = data.get("data") or {}
            if info.get("status") == "success" and info.get("amount") == int(payment.amount * 100):
                mark_success(payment)
            elif info.get("status") in ("failed", "abandoned"):
                payment.status = Payment.Status.FAILED
                payment.save(update_fields=["status"])

        return Response(
            {
                "status": payment.status,
                "reference": payment.reference,
                "amount": payment.amount,
                "booking": BookingSerializer(payment.booking).data,
            }
        )


class QuickVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, reference):
        payment = get_object_or_404(Payment, reference=reference, booking__isnull=True)
        if payment.status != Payment.Status.SUCCESS:
            try:
                res = requests.get(
                    f"{PAYSTACK_URL}/transaction/verify/{reference}",
                    headers=paystack_headers(),
                    timeout=20,
                )
                data = res.json()
            except (requests.RequestException, ValueError):
                return Response({"detail": "Could not reach Paystack."}, status=502)

            info = data.get("data") or {}
            if info.get("status") == "success" and info.get("amount") == int(payment.amount * 100):
                mark_success(payment)
            elif info.get("status") in ("failed", "abandoned"):
                payment.status = Payment.Status.FAILED
                payment.save(update_fields=["status"])

        return Response(
            {
                "status": payment.status,
                "reference": payment.reference,
                "amount": payment.amount,
                "name": payment.payer_name,
            }
        )


@csrf_exempt
def paystack_webhook(request):
    if not settings.PAYSTACK_SECRET_KEY:
        return HttpResponse(status=401)
    signature = request.headers.get("x-paystack-signature", "")
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(), request.body, hashlib.sha512
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return HttpResponse(status=401)

    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)

    if event.get("event") == "charge.success":
        info = event.get("data", {})
        payment = Payment.objects.filter(reference=info.get("reference")).first()
        if payment and info.get("amount") == int(payment.amount * 100):
            mark_success(payment)
    return HttpResponse(status=200)

class PaymentListView(APIView):
    def get(self, request):
        if request.user.role != "admin":
            return Response({"detail": "Not allowed."}, status=403)
        payments = Payment.objects.select_related("booking__customer").order_by("-created_at")
        data = []
        for p in payments:
            customer = p.booking.customer if p.booking else None
            data.append(
                {
                    "id": p.id,
                    "reference": p.reference,
                    "amount": p.amount,
                    "status": p.status,
                    "created_at": p.created_at,
                    "paid_at": p.paid_at,
                    "booking": p.booking_id,
                    "name": (customer.get_full_name() or customer.username) if customer else p.payer_name,
                    "phone": customer.phone if customer else p.payer_phone,
                }
            )
        return Response(data)