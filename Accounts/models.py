from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from Studios.models import Studio


# Create your models here.


class CardInfo(models.Model):
    card_num = models.CharField(max_length=255, primary_key=True)
    expiry_date = models.DateField(null=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    avatar = models.ImageField(upload_to='avatars', null=True)
    cardInfo = models.ForeignKey(CardInfo, on_delete=models.SET_NULL, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Hook profile with default user model.
    Create a profile when a user is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Hook profile with default user model.
    Save profile when user object is saved"""
    instance.profile.save()


class Subscription(models.Model):

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    types = [("Monthly", "Monthly"), ("Yearly", "Yearly")]
    subscription_type = models.CharField(choices=types, max_length=255)
    rate = models.IntegerField()


class UserSubscription(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateField(null=False)
    end_time = models.DateField(null=False)
    auto_renew = models.BooleanField(default=False)


class Payment(models.Model):
    amount = models.IntegerField()
    CardInfo = models.ForeignKey(CardInfo, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField(null=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


def get_user_sub(u:User):
    sub = UserSubscription.objects.filter(user=u)
    print(sub)
    result={}
    for a in sub:
        print(a)
        if a.subscription.studio not in result.keys():
            print(a.subscription.studio)
            result[a.subscription.studio.id]=[]
        result[a.subscription.studio.id].append((a.start_time,None if a.auto_renew else a.end_time))
        print(result)
    return result
