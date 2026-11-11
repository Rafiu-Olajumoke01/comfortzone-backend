from django.urls import path

from .views import (
    InitializePaymentView,
    PaymentAccountView,
    PaymentListView,
    QuickPayView,
    QuickVerifyView,
    VerifyPaymentView,
    paystack_webhook,
)

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("account/", PaymentAccountView.as_view(), name="payment-account"),
    path("initialize/", InitializePaymentView.as_view(), name="payment-initialize"),
    path("verify/<str:reference>/", VerifyPaymentView.as_view(), name="payment-verify"),
    path("quick/", QuickPayView.as_view(), name="payment-quick"),
    path("quick/verify/<str:reference>/", QuickVerifyView.as_view(), name="payment-quick-verify"),
    path("webhook/", paystack_webhook, name="payment-webhook"),
]