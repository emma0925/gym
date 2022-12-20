from django.contrib import admin

# Register your models here.
from Studios.models import studio_class, Studio, Subscriptions, Amenity,Class_instance,enrolled,Images

# class websiteadmin(admin.AdminSite):
#     site_header= 'Website Admin Area'
# Webadmin_site = websiteadmin(name='WebAdmin')
# Webadmin_site.register(studio_class)

admin.site.register(studio_class)
admin.site.register(Amenity)
admin.site.register(Studio)
admin.site.register(Class_instance)
admin.site.register(enrolled)
admin.site.register(Images)
