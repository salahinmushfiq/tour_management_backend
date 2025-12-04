# payments/views.py
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from rest_framework import viewsets, mixins
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt

from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentSerializer
from bookings.models import Booking
from django.shortcuts import get_object_or_404, redirect
import logging

logger = logging.getLogger(__name__)

# SSLCOMMERZ config
SSLCOMMERZ_STORE_ID = settings.SSLCOMMERZ_STORE_ID
SSLCOMMERZ_STORE_PASSWD = settings.SSLCOMMERZ_STORE_PASSWORD
SSL_SUCCESS_URL = settings.SSL_SUCCESS_URL
SSL_FAIL_URL = settings.SSL_FAIL_URL
SSL_CANCEL_URL = settings.SSL_CANCEL_URL

SSLCOMMERZ_BASE_URL = "https://sandbox.sslcommerz.com" if settings.DEBUG else "https://securepay.sslcommerz.com"


class PaymentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    List / Retrieve payments (role-based).
    Extra actions:
      - POST /payments/initiate/  -> create Payment & initiate gateway session (tourist, sslcommerz)
      - POST /payments/cash/      -> organizer creates cash payment (marked success immediately)
      - PATCH /payments/{id}/verify/ -> admin/organizer mark a payment success (if needed)
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.all()
        if user.role == "admin":
            return qs
        if user.role == "organizer":
            return qs.filter(booking__participant__tour__organizer=user)
        # tourist -> only payments they created or payments for their bookings
        return qs.filter(booking__participant__user=user)

    @action(detail=False, methods=["post"], url_path="initiate")
    def initiate(self, request):
        """
        Tourist initiates an SSLCommerz payment.
        payload: { booking: <id>, amount: "100.00", method: "sslcommerz" }
        Returns Payment id and gateway payload/session info.
        IPN will mark success.
        """
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data["booking"]

        # Only booking owner (tourist) may initiate a gateway payment
        if request.user.role != "tourist" or booking.participant.user != request.user:
            return Response({"detail": "Permission denied."}, status=403)

        # create payment record: processing
        payment = serializer.save(created_by=request.user, status="processing")

        # Build SSLCOMMERZ payload
        tran_id = f"PAY-{payment.id}-{int(timezone.now().timestamp())}"
        post_data = {
            "store_id": SSLCOMMERZ_STORE_ID,
            "store_passwd": SSLCOMMERZ_STORE_PASSWD,
            "total_amount": f"{payment.amount:.2f}",
            "currency": "BDT",
            "tran_id": f"booking_{payment.booking.id}_{payment.id}",
            "success_url": SSL_SUCCESS_URL,
            "fail_url": SSL_FAIL_URL,
            "cancel_url": SSL_CANCEL_URL,
            "cus_name": getattr(request.user, "full_name", None) or request.user.username or "Guest User",
            "cus_email": request.user.email or "guest@example.com",
            "cus_add1": getattr(request.user, "address", None) or "Dhaka",
            "cus_city": getattr(request.user, "city", None) or "Dhaka",
            "cus_country": "Bangladesh",
            "cus_phone": getattr(request.user, "phone_number", None) or "01700000000",
            "shipping_method": "NO",
            "ship_name": getattr(request.user, "full_name", None) or "Guest User",
            "ship_add1": getattr(request.user, "address", None) or "Dhaka",
            "ship_city": getattr(request.user, "city", None) or "Dhaka",
            "ship_postcode": getattr(request.user, "postcode", None) or "1200",
            "ship_country": "Bangladesh",
            "product_name": f"Tour Booking #{payment.booking.id}",
            "product_category": "Tours",
            "product_profile": "non-physical-goods",
            "value_a": str(payment.id),
            "value_b": str(payment.booking.id),
            "value_c": request.user.email,
            "value_d": f"user_{request.user.id}",
        }

        init_url = SSLCOMMERZ_BASE_URL + "/gwprocess/v4/api.php"

        try:
            resp = requests.post(init_url, data=post_data, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            payment.status = "failed"
            payment.gateway_payload = {"error": str(e)}
            payment.save()
            logger.exception("SSLCOMMERZ initiation failed")
            return Response({"detail": "Failed to initiate payment gateway", "error": str(e)}, status=500)

        # persist gateway session and tran_id
        payment.gateway_payload = data
        payment.transaction_id = tran_id
        payment.save()

        return Response({"payment_id": payment.id, "gateway": data}, status=201)

    @action(detail=False, methods=["post"], url_path="cash")
    def create_cash_payment(self, request):
        """
        Organizer records a cash payment for a booking. This action marks payment success immediately.
        """
        if request.user.role != "organizer":
            return Response({"detail": "Only organizers can create cash payments."}, status=403)

        booking_id = request.data.get("booking")
        amount = request.data.get("amount")

        if not booking_id or not amount:
            return Response({"detail": "booking and amount are required."}, status=400)

        booking = get_object_or_404(Booking, id=booking_id)

        if booking.participant.tour.organizer != request.user:
            return Response({"detail": "Not authorized for this booking."}, status=403)

        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({"detail": "Amount must be positive."}, status=400)

        due = booking.amount - (booking.amount_paid or Decimal("0"))
        if amount > due:
            return Response({"detail": f"Amount greater than due ({due})."}, status=400)

        with transaction.atomic():
            payment = Payment.objects.create(
                booking=booking,
                created_by=request.user,
                amount=amount,
                method="cash",
                status="success",
                transaction_id=f"CASH-{booking.id}-{int(timezone.now().timestamp())}",
                verified_by=request.user,
                verified_at=timezone.now(),
            )
            booking.amount_paid = (booking.amount_paid or Decimal("0")) + amount
            if booking.amount_paid >= booking.amount:
                booking.payment_status = "paid"
                booking.paid_at = timezone.now()
            elif booking.amount_paid > 0:
                booking.payment_status = "partial"
            booking.save()

        serializer = PaymentSerializer(payment, context={"request": request})
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["patch"], url_path="verify")
    def verify(self, request, pk=None):
        """
        Admin/Organizer can manually mark an existing payment as success.
        """
        payment = get_object_or_404(Payment, pk=pk)
        user = request.user

        if user.role not in ["admin", "organizer"]:
            return Response({"detail": "Permission denied."}, status=403)
        if user.role == "organizer" and payment.booking.participant.tour.organizer != user:
            return Response({"detail": "Permission denied."}, status=403)
        if payment.status == "success":
            return Response({"detail": "Already success."}, status=400)

        with transaction.atomic():
            payment.mark_success(transaction_id=payment.transaction_id or f"MANUAL-{payment.id}",
                                 payload=payment.gateway_payload)
            payment.verified_by = user
            payment.verified_at = timezone.now()
            payment.save()

        serializer = PaymentSerializer(payment, context={"request": request})
        return Response(serializer.data, status=200)


# ---------- SSLCOMMERZ webhook & return handlers ----------

@csrf_exempt
@api_view(["POST", "GET"])
@authentication_classes([])
@permission_classes([])
def payment_return(request):
    """
    Handles SSLCOMMERZ redirect (success/failure/cancel)
    """
    data = request.POST.dict() or request.GET.dict()
    payment_id = data.get("value_a")

    try:
        payment = Payment.objects.get(id=int(payment_id))
    except (Payment.DoesNotExist, ValueError, TypeError):
        return redirect("https://localhost:5173/dashboard/tourist/payment/failure")

    status_from_gateway = data.get("status", "").lower()
    success_statuses = ["success", "valid", "validated"]

    if status_from_gateway in success_statuses:
        return redirect(f"https://localhost:5173/dashboard/tourist/payment/success?payment_id={payment.id}")
    elif status_from_gateway == "cancelled":
        return redirect("https://localhost:5173/dashboard/tourist/payment/cancelled")
    else:
        return redirect("https://localhost:5173/dashboard/tourist/payment/failure")


@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def payment_ipn(request):
    """
    SSLCOMMERZ IPN Handler with validation
    """
    data = request.POST.dict()
    payment_id = data.get("value_a")
    tran_id = data.get("tran_id")

    if not payment_id or not tran_id:
        return Response({"detail": "Missing reference"}, status=400)

    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(id=int(payment_id))

            if payment.status == "success":
                return Response({"detail": "Already processed"}, status=200)

            store_id = SSLCOMMERZ_STORE_ID
            store_passwd = SSLCOMMERZ_STORE_PASSWD

            validation_url = (
                "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
                if settings.DEBUG else
                "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
            )

            params = {
                "val_id": data.get("val_id", ""),
                "store_id": store_id,
                "store_passwd": store_passwd,
                "format": "json"
            }

            try:
                validation_resp = requests.get(validation_url, params=params, timeout=20)
                validation_resp.raise_for_status()
                validation_data = validation_resp.json()
            except Exception as e:
                payment.gateway_payload = {"ipn": data, "error": str(e)}
                payment.save()
                return Response({"detail": "Validation API error. Will retry.", "error": str(e)}, status=502)

            status_from_gateway = validation_data.get("status", "").lower()
            amount_match = str(validation_data.get("amount")) == str(payment.amount)
            currency_match = validation_data.get("currency") == "BDT"

            if status_from_gateway in ("valid", "validated") and validation_data.get("tran_id") == tran_id and amount_match and currency_match:
                payment.mark_success(transaction_id=tran_id, payload={"ipn": data, "validated": validation_data})
                return Response({"detail": "Payment verified and completed"}, status=200)

            payment.mark_failed(payload={"ipn": data, "validated": validation_data})
            return Response({"detail": "Payment invalid"}, status=400)

    except Payment.DoesNotExist:
        return Response({"detail": "Payment not found"}, status=404)


class SSLCommerzSuccessView(APIView):
    authentication_classes = []
    permission_classes = []

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def handle_request(self, request):
        data = request.POST.dict() or request.GET.dict()
        payment_id = data.get("value_a")

        try:
            payment = Payment.objects.get(id=int(payment_id))
        except (Payment.DoesNotExist, ValueError, TypeError):
            return redirect("https://localhost:5173/dashboard/tourist/payment/failure")

        raw_status = data.get("status", "")
        status_from_gateway = raw_status.lower()
        success_statuses = ["valid", "validated", "success"]

        if status_from_gateway in success_statuses:
            if payment.status != "success":
                payment.status = "success"
                payment.verified_at = timezone.now()
                payment.save()

                booking = payment.booking
                paid_amount = Decimal(str(payment.amount))
                booking.amount_paid = (booking.amount_paid or 0) + paid_amount
                booking.update_status()
                booking.paid_at = timezone.now()
                booking.save()

            return redirect(f"https://localhost:5173/dashboard/tourist/payment/success?payment_id={payment.id}")
        elif status_from_gateway == "cancelled":
            payment.status = "cancelled"
            payment.save()
            return redirect("https://localhost:5173/dashboard/tourist/payment/cancelled")
        else:
            payment.status = "failed"
            payment.save()
            return redirect("https://localhost:5173/dashboard/tourist/payment/failure")


# payments/views.py
# import requests
# from decimal import Decimal
# from django.conf import settings
# from django.utils import timezone
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect
#
# from rest_framework import viewsets, mixins, status
# from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from django.views.decorators.csrf import csrf_exempt
#
# from .models import Payment
# from .serializers import PaymentCreateSerializer, PaymentSerializer
# from bookings.models import Booking
#
# SSLCOMMERZ_BASE_URL = "https://sandbox.sslcommerz.com" if settings.DEBUG else "https://securepay.sslcommerz.com"
#
#
# class PaymentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
#     """
#     Payment actions:
#       - initiate: tourist creates SSLCommerz payment
#       - cash: organizer creates cash payment
#       - verify: admin/organizer manually verifies
#     """
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         user = self.request.user
#         qs = Payment.objects.all()
#         if user.role == "admin":
#             return qs
#         if user.role == "organizer":
#             return qs.filter(booking__participant__tour__organizer=user)
#         # tourist
#         return qs.filter(booking__participant__user=user)
#
#     @action(detail=False, methods=["post"], url_path="initiate")
#     def initiate(self, request):
#         """
#         Tourist initiates an SSLCommerz payment.
#         payload: { booking: <id>, amount: "100.00", method: "sslcommerz" }
#         """
#         serializer = PaymentCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         booking = serializer.validated_data["booking"]
#
#         if request.user.role != "tourist" or booking.participant.user != request.user:
#             return Response({"detail": "Permission denied."}, status=403)
#
#         payment = serializer.save(created_by=request.user, status="processing")
#
#         # Consistent transaction ID
#         tran_id = f"PAY-{payment.id}-{int(timezone.now().timestamp())}"
#         payment.transaction_id = tran_id
#         payment.save(update_fields=["transaction_id"])
#
#         post_data = {
#             "store_id": settings.SSLCOMMERZ_STORE_ID,
#             "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
#             "total_amount": f"{payment.amount:.2f}",
#             "currency": "BDT",
#             "tran_id": tran_id,
#             "success_url": "https://localhost:5173/dashboard/tourist/payment/success",
#             "fail_url": "https://localhost:5173/dashboard/tourist/payment/failure",
#             "cancel_url": "https://localhost:5173/dashboard/tourist/payment/cancelled",
#             "cus_name": getattr(request.user, "full_name", None) or request.user.username or "Guest User",
#             "cus_email": request.user.email or "guest@example.com",
#             "cus_add1": getattr(request.user, "address", None) or "Dhaka",
#             "cus_city": getattr(request.user, "city", None) or "Dhaka",
#             "cus_country": "Bangladesh",
#             "cus_phone": getattr(request.user, "phone_number", None) or "01700000000",
#             "shipping_method": "NO",
#             "ship_name": getattr(request.user, "full_name", None) or "Guest User",
#             "ship_add1": getattr(request.user, "address", None) or "Dhaka",
#             "ship_city": getattr(request.user, "city", None) or "Dhaka",
#             "ship_postcode": getattr(request.user, "postcode", None) or "1200",
#             "ship_country": "Bangladesh",
#             "product_name": f"Tour Booking #{payment.booking.id}",
#             "product_category": "Tours",
#             "product_profile": "non-physical-goods",
#             "value_a": str(payment.id),
#             "value_b": str(payment.booking.id),
#             "value_c": request.user.email,
#             "value_d": f"user_{request.user.id}",
#         }
#
#         try:
#             resp = requests.post(f"{SSLCOMMERZ_BASE_URL}/gwprocess/v4/api.php", data=post_data, timeout=15)
#             data = resp.json()
#         except Exception as e:
#             payment.status = "failed"
#             payment.gateway_payload = {"error": str(e)}
#             payment.save()
#             return Response({"detail": "Failed to initiate payment gateway", "error": str(e)}, status=500)
#
#         payment.gateway_payload = data
#         payment.save(update_fields=["gateway_payload"])
#         return Response({"payment_id": payment.id, "gateway": data}, status=201)
#
#     @action(detail=False, methods=["post"], url_path="cash")
#     def create_cash_payment(self, request):
#         if request.user.role != "organizer":
#             return Response({"detail": "Only organizers can create cash payments."}, status=403)
#
#         booking_id = request.data.get("booking")
#         amount = request.data.get("amount")
#         if not booking_id or not amount:
#             return Response({"detail": "booking and amount are required."}, status=400)
#
#         booking = get_object_or_404(Booking, id=booking_id)
#         if booking.participant.tour.organizer != request.user:
#             return Response({"detail": "Not authorized for this booking."}, status=403)
#
#         amount = Decimal(str(amount))
#         if amount <= 0:
#             return Response({"detail": "Amount must be positive."}, status=400)
#
#         due = booking.amount - (booking.amount_paid or Decimal("0"))
#         if amount > due:
#             return Response({"detail": f"Amount greater than due ({due})."}, status=400)
#
#         with transaction.atomic():
#             payment = Payment.objects.create(
#                 booking=booking,
#                 created_by=request.user,
#                 amount=amount,
#                 method="cash",
#                 status="success",
#                 transaction_id=f"CASH-{booking.id}-{int(timezone.now().timestamp())}",
#                 verified_by=request.user,
#                 verified_at=timezone.now(),
#             )
#             booking.amount_paid = (booking.amount_paid or Decimal("0")) + amount
#             if booking.amount_paid >= booking.amount:
#                 booking.payment_status = "paid"
#                 booking.paid_at = timezone.now()
#             elif booking.amount_paid > 0:
#                 booking.payment_status = "partial"
#             booking.save()
#
#         serializer = PaymentSerializer(payment, context={"request": request})
#         return Response(serializer.data, status=201)
#
#     @action(detail=True, methods=["patch"], url_path="verify")
#     def verify(self, request, pk=None):
#         payment = get_object_or_404(Payment, pk=pk)
#         user = request.user
#
#         if user.role not in ["admin", "organizer"]:
#             return Response({"detail": "Permission denied."}, status=403)
#
#         if user.role == "organizer" and payment.booking.participant.tour.organizer != user:
#             return Response({"detail": "Permission denied."}, status=403)
#
#         if payment.status == "success":
#             return Response({"detail": "Already success."}, status=400)
#
#         with transaction.atomic():
#             payment.mark_success(transaction_id=payment.transaction_id or f"MANUAL-{payment.id}", payload=payment.gateway_payload)
#             payment.verified_by = user
#             payment.verified_at = timezone.now()
#             payment.save()
#
#         serializer = PaymentSerializer(payment, context={"request": request})
#         return Response(serializer.data, status=200)
#
#
# # ---------- Public Endpoints ----------
#
# @csrf_exempt
# @api_view(["POST", "GET"])
# @authentication_classes([])
# @permission_classes([])
# def payment_return(request):
#     """Handle SSLCOMMERZ frontend redirect"""
#     data = request.POST.dict() or request.GET.dict() or request.data
#     payment_id = data.get("value_a")
#     frontend = settings.FRONTEND_URL
#
#     try:
#         payment = Payment.objects.get(id=int(payment_id))
#     except (Payment.DoesNotExist, ValueError, TypeError):
#         return redirect("https://localhost:5173/dashboard/tourist/payment/failure")
#
#     status_from_gateway = (data.get("status") or "").lower()
#     if status_from_gateway in ["valid", "validated", "success"]:
#         return redirect("https://localhost:5173/dashboard/tourist/payment/success")
#     elif status_from_gateway == "cancelled":
#         return redirect("https://localhost:5173/dashboard/tourist/payment/cancelled")
#     else:
#         return redirect("https://localhost:5173/dashboard/tourist/payment/failure")
#
#
# @csrf_exempt
# @api_view(["POST"])
# @authentication_classes([])
# @permission_classes([])
# def payment_ipn(request):
#     """Handle SSLCOMMERZ server-to-server IPN"""
#     data = request.POST.dict() or request.data
#     payment_id = data.get("value_a")
#     tran_id = data.get("tran_id")
#
#     if not payment_id or not tran_id:
#         return Response({"detail": "Missing reference"}, status=400)
#
#     try:
#         payment = Payment.objects.get(id=int(payment_id))
#     except Payment.DoesNotExist:
#         return Response({"detail": "Payment not found"}, status=404)
#
#     status_from_gateway = (data.get("status") or "").lower()
#     success_statuses = ["valid", "validated", "success"]
#
#     with transaction.atomic():
#         if status_from_gateway in success_statuses and payment.status != "success":
#             payment.mark_success(transaction_id=tran_id, payload=data)
#             payment.verified_at = timezone.now()
#             payment.save()
#         elif status_from_gateway == "cancelled":
#             payment.status = "cancelled"
#             payment.save()
#         else:
#             payment.status = "failed"
#             payment.save()
#
#     return Response({"detail": "IPN processed"}, status=200)
#
#
# class SSLCommerzSuccessView(APIView):
#     """Unified success/cancel/failure handler"""
#     authentication_classes = []
#     permission_classes = []
#
#     @csrf_exempt
#     def get(self, request, *args, **kwargs):
#         return self.handle_request(request)
#
#     @csrf_exempt
#     def post(self, request, *args, **kwargs):
#         return self.handle_request(request)
#
#     def handle_request(self, request):
#         data = request.POST.dict() or request.GET.dict() or request.data
#         payment_id = data.get("value_a")
#         frontend = settings.FRONTEND_URL
#
#         try:
#             payment = Payment.objects.get(id=int(payment_id))
#         except (Payment.DoesNotExist, ValueError, TypeError):
#             redirect("https://localhost:5173/dashboard/tourist/payment/failure")
#
#         status_from_gateway = (data.get("status") or "").lower()
#         success_statuses = ["valid", "validated", "success"]
#
#         if status_from_gateway in success_statuses:
#             if payment.status != "success":
#                 payment.status = "success"
#                 payment.verified_at = timezone.now()
#                 payment.save()
#             return redirect("https://localhost:5173/dashboard/tourist/payment/success")
#         elif status_from_gateway == "cancelled":
#             payment.status = "cancelled"
#             payment.save()
#             redirect("https://localhost:5173/dashboard/tourist/payment/cancelled")
#         else:
#             payment.status = "failed"
#             payment.save()
#             redirect("https://localhost:5173/dashboard/tourist/payment/failure")
