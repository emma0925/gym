from django.urls import path

from Studios.views import *

# from Studios.admin import Webadmin_site

app_name = 'studios'

urlpatterns = [
    #query prameater: latitude, longitude,index
    path('<id>/',Stodio_Detail_View.as_view()),
    path('<studio_id>/images/',Image_view.as_view()),
    path('images/<i>',get_image_by_id),
    path('<c>/enrolled/',check_enrolled.as_view()),
    path('<studio_id>/amenities/',Amenities_view.as_view()),
    path('<studio_id>/classes/',stodio_class_view.as_view()),
    path('classes/deleat_class/',class_edit.as_view()),
    path('classes/<class_id>/<d>/',User_Enroll_class_view.as_view()),
    path('/',Stodio_View.as_view()),
    path('search/class/byname',GetClass_name.as_view()),
    path('search/class/bydate',GetClass_time.as_view()),
    path('search/class/bydaterange',GetClass_range.as_view()),
    path('search/class/bycoach',GetClass_coach.as_view()),
    path('search/studio/byclass',GetStudio_class.as_view()),
    path('search/studio/byamentities',GetStudio_amentities.as_view()),
    path('search/studio/bycoach',GetStudio_coach.as_view()),
    path('search/studio/name',GetStudio_name.as_view()),
    # path('admin/', Webadmin_site.urls)
]
