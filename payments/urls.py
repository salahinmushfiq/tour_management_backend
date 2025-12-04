# payments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, SSLCommerzSuccessView, payment_ipn

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Public webhook/return endpoints — outside the router
    path("payments/success/", SSLCommerzSuccessView.as_view(), name="payment-success"),
    path("payments/ipn/", payment_ipn, name="payment-ipn"),

    # All authenticated ViewSet endpoints
    path("", include(router.urls)),
]



# payments/urls.py

# # payments/urls.py
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import PaymentViewSet, payment_return, payment_ipn, SSLCommerzSuccessView
#
# router = DefaultRouter()
# router.register(r'payments', PaymentViewSet, basename='payment')
#
# urlpatterns = [
#     # DRF viewset routes: list, retrieve, initiate, cash, verify
#     path('', include(router.urls)),
#
#     # Public return endpoint (frontend redirect after payment)
#     path('payments/return/', payment_return, name='payment-return'),
#
#     # Public IPN endpoint (server-to-server notification)
#     path('payments/ipn/', payment_ipn, name='payment-ipn'),
#
#     # Optional: unified success/cancel/failure view (alternative to payment_return)
#     path('payments/ssl-success/', SSLCommerzSuccessView.as_view(), name='ssl-success'),
# ]
