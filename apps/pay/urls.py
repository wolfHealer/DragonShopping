from django.urls import path
from apps.pay.views import PayUrlView,PaymentStatusView

urlpatterns = [
    path('payment/status/',PaymentStatusView.as_view()),
    path('payment/<order_id>/',PayUrlView.as_view()),

]

