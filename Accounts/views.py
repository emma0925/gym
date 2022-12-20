from datetime import datetime, date
from django.conf import settings
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from Accounts.models import Profile, CardInfo, Payment, Subscription, UserSubscription
from django.http import JsonResponse, HttpRequest, HttpResponse, FileResponse


# Create your views here.
from Studios.models import Studio

class Image_Provider(APIView):
    def get(self, request:HttpRequest):
        print(request.user.id)
        try:
            img = Profile.objects.get(user=request.GET.get('t',''))
            #img = Profile.objects.get(user=request.user.id)
            url = str(settings.BASE_DIR) +str(img.avatar.url)
            print(url)
            return FileResponse(open(url,'rb'))
        except Profile.DoesNotExist:
            return HttpResponse(status=404)
        except Profile.MultipleObjectsReturned:
            return HttpResponse(status=500)


class StandardResultsSetPagination(PageNumberPagination):
    """The customized pagination class."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class RegisterView(APIView):

    def get(self, request):
        return JsonResponse({
            "status": 405,
            "message": "HTTP method not supported, the value supported is {POST}.",
        }, status=405)

    def post(self, request):
        """
        Register an account, taking username, password1, password2, email, first_name
        last_name, avatar(optional).
        """
        try:
            username = request.POST.get('username', '')
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            f_name = request.POST.get('first_name', '')
            l_name = request.POST.get('last_name', '')
            avatar = request.FILES.get('avatar', '')
            if pwd1 != pwd2:
                return JsonResponse({
                    "status": 500,
                    "message": "INTERNAL SERVER ERROR: The two passwords doesn't match"
                }, status=500)
            if not username or not email or not pwd1:
                return JsonResponse({
                    "status": 500,
                    "message": "INTERNAL SERVER ERROR: Missing username, email or password"
                }, status=500)
            if User.objects.filter(email=email).count() != 0:
                return JsonResponse({
                    "status": 500,
                    "message": "INTERNAL SERVER ERROR: The provided email is already occupied by another user."
                }, status=500)
            if User.objects.filter(username=username).count() != 0:
                return JsonResponse({
                    "status": 500,
                    "message": "INTERNAL SERVER ERROR: The provided username is already occupied."
                }, status=500)
            user = User.objects.create_user(username=username, password=pwd1, email=email, first_name=f_name,
                                            last_name=l_name)
            if avatar:
                profile = user.profile
                profile.avatar = avatar
                profile.save()
            user.save()
            return JsonResponse({
                "status": 200,
                "message": "User successfully registered.",
                "user": model_to_dict(user)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while registering user.",
                "error": str(e)
            }, status=500)


class GetProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Get a json response of the current information of the user profile."""
        try:
            try:
                profile = Profile.objects.get(user=request.user)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "The user profile is not found in the system."
                }, status=404)
            avatar = profile.avatar
            card = profile.cardInfo
            return JsonResponse({
                "status": 200,
                "message": "The current user's information is as follow:",
                "user": model_to_dict(request.user),
                "avatar": avatar.url if avatar else None,
                "Payment_Method": model_to_dict(card) if card else None
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the user profile.",
                "error": str(e)
            }, status=500)


class UpdateProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Update the user profile, takes user_id, username(optional), password(optional), email(optional),
        first_name(optional), last_name(optional), and avatar(optional).
        """
        user_id = request.POST.get('user_id', '')
        if not user_id:
            user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse({
                "status": 404,
                "message": "The user profile is not found in the system.",
                "user_id": user_id
            }, status=404)
        username, password, email, first_name, last_name, avatar = \
            request.POST.get('username', ''), request.POST.get('password', ''), request.POST.get('email', ''), \
            request.POST.get('first_name', ''), request.POST.get('last_name', ''), \
            request.FILES.get('avatar', '')

        try:
            if username:
                if User.objects.filter(username=username).count() != 0:
                    return JsonResponse({
                        "status": 500,
                        "message": "INTERNAL SERVER ERROR: The provided username is already occupied."
                    }, status=500)
                user.username = username
            if password:
                user.set_password(password)
            if email:
                user.email = email
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if avatar:
                profile = Profile.objects.get(user=user)
                profile.avatar = avatar
                profile.save()
            user.save()
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while updating the user profile.",
                "error": str(e)
            }, status=500)

        return JsonResponse({
            "status": 200,
            "message": "Successfully updated the user profile."
        }, status=200)


class AddCard(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Create a CardInfo, taking card_num and expiry_date.
        """
        try:
            card_num = request.POST.get("card_num")
            expiry_date = request.POST.get("expiry_date")
            if not card_num or not expiry_date:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad Request: Missing card_num and/or expiry_date."
                }, status=400)
            try:
                card = CardInfo.objects.create(card_num=card_num, expiry_date=expiry_date)
            except Exception as e:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad Request: card_num and/or expiry_date is invalid.",
                    "error": str(e)
                }, status=400)
            card.save()
            return JsonResponse({
                "status": 200,
                "message": "Card successfully added.",
                "card": model_to_dict(card)
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while adding the card",
                "error": str(e)
            }, status=500)


class UpdatePayment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Take the card_num, update user's payment method to this card.
        """
        try:
            user_id = request.user.id
            card_num = request.POST.get("card_num")
            if not card_num:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad Request: Card_num is missing."
                }, status=400)
            try:
                user = User.objects.get(id=user_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "User not found.",
                    "user_id": user_id
                }, status=404)
            user_profile = user.profile
            try:
                card = CardInfo.objects.get(card_num=card_num)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Card not found.",
                    "card_num": card_num
                }, status=404)
            user_profile.cardInfo = card
            user_profile.save()
            return JsonResponse({
                "status": 200,
                "message": "Payment method successfully updated."
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while updating payment method",
                "error": str(e)
            }, status=500)


class CreatePayment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Create a new payment and save it to the database.
        Takes amount, card_num, time(optional, default is the current time) and
        user_id(optional, default is the user of the request).
        """
        try:
            amount = request.POST.get("amount")
            card_num = request.POST.get("card_num")
            time = request.POST.get("time")
            user_id = request.POST.get("user_id")
            if not amount or not card_num:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad request: missing one of amount, card_num."
                }, status=400)
            if not user_id:
                user_id = request.user.id
            if not time:
                time = datetime.now()
            try:
                user = User.objects.get(id=user_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "User not found.",
                    "user_id": user_id
                }, status=404)
            try:
                card = CardInfo.objects.get(card_num=card_num)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Card not found.",
                    "card_num": card_num
                }, status=404)
            new_payment = \
                Payment.objects.create(amount=amount, CardInfo=card, time=time, user=user)
            new_payment.save()
            return JsonResponse({
                "status": 200,
                "message": "Payment successfully created.",
                "Payment": model_to_dict(new_payment)
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while creating payment",
                "error": str(e)
            }, status=500)


class EditUserSubscription(APIView):
    """
    Post: Update the corresponding plan with the given information.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Take a user_sub_id, start_time, end_time, auto_renew and update the subscription
        accordingly."""
        try:
            sub_id = request.POST.get("user_sub_id")
            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")
            auto_renew = request.POST.get("auto_renew")
            if not sub_id:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad Request: Missing user_sub_id."
                }, status=400)
            try:
                subscription = UserSubscription.objects.get(id=sub_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "User Subscription not found.",
                    "user_sub_id": sub_id
                }, status=404)

            if start_time:
                subscription.start_time = start_time
            if end_time:
                subscription.end_time = end_time
            if auto_renew:
                if auto_renew not in ("True", "False"):
                    return JsonResponse({
                        "status": 400,
                        "message": "Bad request: <auto_renew> is not valid. Has to be 'True' or 'False'."
                    }, status=400)
                subscription.auto_renew = bool(auto_renew)
            subscription.save()
            return JsonResponse({
                "status": 200,
                "message": " User Subscription successfully edited.",
                "Subscription after modified": model_to_dict(subscription)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while updating user subscription",
                "error": str(e)
            }, status=500)


class ManageUserSubscription(APIView):
    """
    Get: Get all the subscription plan of the current user.
    Post: Create a user subscription plan for the current user.
    """
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        try:
            subscriptions = list(UserSubscription.objects.filter(user=request.user).values())
            return JsonResponse({
                "status": 200,
                "message": "User's subscriptions successfully retrieved.",
                "user": model_to_dict(request.user),
                "Subscriptions": subscriptions
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving user subscriptions.",
                "error": str(e)
            }, status=500)

    def post(self, request):
        """
        Take a start_time, end_time, plan_id, and auto_renew of 'True' or 'False'.
        """
        try:
            user = request.user
            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")
            auto_renew = request.POST.get("auto_renew")
            plan_id = request.POST.get("plan_id")
            if not start_time or not end_time or not plan_id or not auto_renew:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad request: Missing one of the following: "
                               "<start_time>, <end_time>, <plan_id>."
                }, status=400)
            try:
                plan = Subscription.objects.get(id=plan_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Plan not found.",
                    "plan_id": plan_id
                }, status=404)
            if auto_renew not in ("True", "False"):
                return JsonResponse({
                    "status": 400,
                    "message": "Bad request: <auto_renew> is not valid. Has to be 'True' or 'False'."
                }, status=400)
            new_subscription = UserSubscription.objects.create(subscription=plan, user=user,
                                                               start_time=start_time, end_time=end_time,
                                                               auto_renew=auto_renew)
            new_subscription.save()
            return JsonResponse({
                "status": 200,
                "message": "User Subscription successfully created.",
                "Payment": model_to_dict(new_subscription)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while creating Subscription",
                "error": str(e)
            }, status=500)


class ManageSubscription(APIView):
    """
    Post: Create a new subscription plan.
    Get: Retrieve the subscription plan with the given studio_id.
    """
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def post(self, request):
        """
        Take a studio_id, type of 'Monthly' or 'Yearly', rate.
        Create the corresponding subscription plan
        """
        if not request.user.is_staff:
            return JsonResponse({
                "status": 403,
                "message": "Access Denied: Must be a web admin to create subscription"
            }, status=403)
        try:

            studio_id = request.POST.get("studio_id")
            sub_type = request.POST.get("type")
            rate = request.POST.get("rate")
            if not (studio_id and sub_type and rate):
                return JsonResponse({
                    "status": 400,
                    "message": "Bad request: Missing one of the following: "
                               "<studio_id>,"
                               "<type>, <rate>."
                }, status=400)

            try:
                studio = Studio.objects.get(id=studio_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Studio of given studio_id is not found.",
                    "studio_id": studio_id
                }, status=404)
            if sub_type not in ("Monthly", "Yearly"):
                return JsonResponse({
                    "status": 400,
                    "message": "Bad request: <type> is not valid. Has to be 'Monthly' or 'Yearly'."
                }, status=400)

            new_subscription = Subscription.objects.create(studio=studio, subscription_type=sub_type, rate=rate)
            new_subscription.save()
            return JsonResponse({
                "status": 200,
                "message": "Subscription Plan successfully created.",
                "Subscription": model_to_dict(new_subscription)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while creating Subscription",
                "error": str(e)
            }, status=500)

    def get(self, request):
        """
        Take a studio_id, return a json response containing the subscription plans of it.
        """
        try:
            studio_id = request.GET.get("studio_id")
            try:
                studio = Studio.objects.get(id=studio_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Studio of given studio_id is not found.",
                    "studio_id": studio_id
                }, status=404)
            subscription = list(Subscription.objects.filter(studio=studio).values())
            return JsonResponse({
                "status": 200,
                "message": "Subscription Plans successfully retrieved.",
                "subscriptions": subscription
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while getting Subscription",
                "error": str(e)
            }, status=500)


class DeleteSubscription(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Take a sub_id, delete it from the system.
        """
        if not request.user.is_staff:
            return JsonResponse({
                "status": 403,
                "message": "Access Denied: Must be a web admin to delete subscription"
            }, status=403)
        try:
            sub_id = request.POST.get("sub_id")
            if not sub_id:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad Request: Missing sub_id."
                }, status=400)
            try:
                subscription = Subscription.objects.get(id=sub_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Subscription not found in the system.",
                    "Subscription id": sub_id
                }, status=404)
            info = model_to_dict(subscription)
            Subscription.objects.filter(id=sub_id).delete()
            return JsonResponse({
                "status": 200,
                "message": "Subscription successfully deleted.",
                "Deleted Subscription": info
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while deleting Subscription",
                "error": str(e)
            }, status=500)


class EditSubscription(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Update the subscription of the given subscription_id.
        Take a sub_id, type of 'Monthly' or 'Yearly'(optional), rate(optional).
        """
        if not request.user.is_staff:
            return JsonResponse({
                "status": 403,
                "message": "Access Denied: Must be a web admin to edit subscription"
            }, status=403)
        try:
            sub_id = request.POST.get("sub_id")
            if not sub_id:
                return JsonResponse({
                    "status": 400,
                    "message": "Bad Request: Missing sub_id."
                }, status=400)
            try:
                subscription = Subscription.objects.get(id=sub_id)
            except:
                return JsonResponse({
                    "status": 404,
                    "message": "Subscription not found in the system.",
                    "sub_id": sub_id
                }, status=404)
            sub_type = request.POST.get("type")
            rate = request.POST.get("rate")
            if sub_type:
                if sub_type not in ("Monthly", "Yearly"):
                    return JsonResponse({
                        "status": 400,
                        "message": "Bad request: <type> is not valid. Has to be 'Monthly' or 'Yearly'."
                    }, status=400)
                subscription.subscription_type = sub_type
            if rate:
                subscription.rate = rate
            subscription.save()
            return JsonResponse({
                "status": 200,
                "message": "Subscription successfully edited.",
                "Subscription after modified": model_to_dict(subscription)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while editing Subscription",
                "error": str(e)
            }, status=500)


class NextPayment(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Return the json response containing the future
        payments of the current user."""
        try:
            subscriptions = UserSubscription.objects.filter(user=request.user)\
                .filter(auto_renew=True)
            result = []
            for sub in subscriptions:
                if sub.end_time > date.today():
                    price = sub.subscription.rate
                    plan = sub.subscription.id
                    result.append({'Payment_time': sub.end_time,
                                   'price': price,
                                   'plan_id': plan})
            result.sort(key=lambda x: x['Payment_time'])
            return JsonResponse({
                "status": 200,
                "message": "Future Payments successfully retrieved.",
                "user": model_to_dict(request.user),
                "Future_Payments": result
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving future payment.",
                "error": str(e)
                }, status=500)
class PaymentHistory(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Return the json response containing all the payment history."""
        try:
            payments = list(Payment.objects.filter(user=request.user).values())
            payments.sort(key=lambda x: x['time'])
            return JsonResponse({
                "status": 200,
                "message": "Payment history successfully retrieved.",
                "user": model_to_dict(request.user),
                "Payment": payments
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving payment history.",
                "error": str(e)
            }, status=500)

    def post(self, request):
        return JsonResponse({
            "status": 405,
            "message": "HTTP method not supported, the value supported is {GET}.",
        }, status=405)
