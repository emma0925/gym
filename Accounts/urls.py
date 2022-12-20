from django.urls import path
# from Accounts.admin import Webadmin_site
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from Accounts.views import AddCard, CreatePayment, ManageSubscription, EditSubscription, \
    DeleteSubscription, PaymentHistory, RegisterView, \
    UpdatePayment, \
    UpdateProfile, GetProfile, ManageUserSubscription, EditUserSubscription

from Accounts.views import NextPayment

from Accounts.views import Image_Provider

app_name = 'Accounts'

urlpatterns = [
   # path('/admin', Webadmin_site.urls),
    path('register/', RegisterView.as_view()),
    path('updateprofile/', UpdateProfile.as_view()),
    path('getprofile/', GetProfile.as_view()),
    path('addcard/', AddCard.as_view()),
    path('updatepayment/', UpdatePayment.as_view()),
    path('createpayment/', CreatePayment.as_view()),
    path('manageusersubscription/', ManageUserSubscription.as_view()),
    path('editusersubscription/', EditUserSubscription.as_view()),
    path('managesubscription/', ManageSubscription.as_view()),
    path('editsubscription/', EditSubscription.as_view()),
    path('deletesubscription/', DeleteSubscription.as_view()),
    path('paymenthistory/', PaymentHistory.as_view()),
    path('futurepayment/', NextPayment.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('image/', Image_Provider.as_view())
]
