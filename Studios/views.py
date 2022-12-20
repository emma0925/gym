from django.shortcuts import render
from django.views.generic import FormView
from datetime import date
from django.db.models import Q

from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

# Date Formate: '2002-09-25' substirng by index str[0:4] -> year, str[4:7] -> month
# Create your views here.
from Studios.models import Studio, Images, Amenity, get_all_class_instance, get_user_enrolled_class_history, get_user_enrolled_class_instance, keyWoards, look_up_keywoard, \
    studio_class, Canceled_class, enroll, cancel, get_cancled, add_key_word, \
    Class_instance, enrolled, drop, get_enrolled
from typing import Dict, List
from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse, FileResponse
from datetime import date, time, timedelta, datetime
from django.contrib.auth.models import User
from Studios.helper import *
from Accounts.models import Subscription, UserSubscription, get_user_sub
from Studios.models import check_has_class
from math import acos, sin, cos
from django.conf import settings

amount = 5

def studio_serilization(a):
    stu_obj={}
    stu_obj["name"] = a.name;
    stu_obj["address"] = a.address;
    stu_obj["latitude"] = a.latitude;
    stu_obj["longitude"] = a.longitude;
    stu_obj["postal_code"] = a.postal_code;
    stu_obj["phone_number"] = a.phone_number;
    return stu_obj;

def class_serilization(a):
    stu_obj={}
    stu_obj["id"] = a.id;
    stu_obj["studio_id"] = a.studio_id;
    stu_obj["name"] = a.name;
    stu_obj["description"] = a.description;
    stu_obj["coach_id"] = a.coach_id;
    stu_obj["start_time"] = a.start_time;
    stu_obj["end_time"] = a.end_time;
    stu_obj["start_time"] = a.start_time;
    stu_obj["recurseTime"] = a.recurseTime;
    stu_obj["start_Date"] = a.start_Date;
    stu_obj["class_size"] = a.class_size;
    return stu_obj;



class StandardResultsSetPagination(PageNumberPagination):
    """The customized pagination class."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


def getAllStudio(lat: float, lon: float, i: int, amount: int):
    all_stodius = Studio.objects.all().values()
    if i < len(all_stodius):
        result = list(all_stodius)
        result.sort(key=lambda s: pority(lat, lon, s))
        a = [r for r in result]
        print(a)
        return result[i:min(amount + i, len(result))]
    return []


def pority(lat: float, lon: float, s):
    la = float(s['latitude'])
    lo = float(s['longitude'])
    return -acos(sin(lat) * sin(la) + cos(lat) * cos(la) * cos(lon - lo))


class Stodio_View(APIView):

    def get(self, request):
        lat = (request.GET.get("latitude", ''))
        lon = (request.GET.get('longitude', ''))
        index = (request.GET.get("index", ''))
        try:
            return JsonResponse(
                getAllStudio(float(lat), float(lon), int(index), amount),
                safe=False)
        except ValueError:
            return HttpResponse(status=400)

    def post(self, request: HttpRequest):
        if request.user.is_staff:
            print(request.POST)
            name = request.POST.get('name', '')
            address = request.POST.get('address', None)
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')

            postal_code = request.POST.get('postal_code', None)
            if not latitude == '' and not longitude == '':
                obj = Studio.objects.create(name=name, address=address,
                                            latitude=latitude,
                                            longitude=longitude,
                                            postal_code=postal_code,
                                            phone_number=None)
                p = request.POST.get('phone_number', '')
                if p.isnumeric():
                    obj.phone_number = p
                    obj.save()
                return JsonResponse({"id": obj.id})
            return HttpResponse(status=400)
        return HttpResponse(status=403)


# <id>
class Stodio_Detail_View(APIView):
    def get(self, request, id):
        try:
            s = Studio.objects.get(id=id)
            return JsonResponse({
                'name': s.name,
                "address": s.address,
                'latitude': s.latitude,
                'longitude': s.longitude,
                'postal_code': s.postal_code,
                'phone_number': s.phone_number
            })
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned:
            return HttpResponse(status=500)

    def post(self, request: HttpRequest, id):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        try:
            s = Studio.objects.get(id=id)
            name = request.POST.get("name", '')
            address = request.POST.get("address", '')
            latitude = request.POST.get("latitude", '')
            longitude = request.POST.get("longitude", '')
            postal_code = request.POST.get("postal_code", '')
            phone_number = request.POST.get("phone_number", '')
            if not name == '':
                s.name = name
            if not address == '':
                s.address = address
            float(latitude)
            if latitude:
                s.latitude = latitude
            float(longitude)
            if longitude:
                s.longitude = longitude
            if not postal_code == '':
                s.postal_code = postal_code
            if not phone_number == '' and phone_number.isnumeric():
                s.phone_number = phone_number
            s.save()
            return HttpResponse(status=200)
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned:
            return HttpResponse(status=500)
        except ValueError:
            return HttpResponse(status=400)


# <studio_id>
class Image_view(APIView):
    def get(self, request, studio_id):
        try:
            s = Studio.objects.get(id=studio_id)
            return JsonResponse(
                list(
                    Images.objects.filter(studio=s).values('id')),safe=False)
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned:
            return HttpResponse(status=500)

    def post(self, request: HttpRequest, studio_id):
        try:
            img = Images.objects.get(id=(request.POST.get('img_id', '')))
            img.delete()
            return HttpResponse(status=200)
        except Images.DoesNotExist:
            return HttpResponse(status=404)
        except Images.MultipleObjectsReturned:
            return HttpResponse(status=500)

    def put(self, request: HttpRequest, studio_id):
        try:
            s = Studio.objects.get(id=studio_id)
            # print(request.POST)
            Images.objects.create(studio=s, img=request.FILES.get('image', ''))
            return HttpResponse(status=200)
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned:
            return HttpResponse(status=500)

def get_image_by_id(request:HttpRequest, i):
    try:
        img = Images.objects.get(id=i)
        url = str(settings.BASE_DIR) +str(img.img.url)
        print(url)
        return FileResponse(open(url,'rb'))
    except Images.DoesNotExist:
        return HttpResponse(status=404)
    except Images.MultipleObjectsReturned:
        return HttpResponse(status=500)



class check_enrolled(APIView):
    def get(self,request:HttpRequest, c:int):
        u=request.user
        try:
            d = string2date(request.GET.get('date',''))
            print(c)
            cls = studio_class.objects.filter(id=c)
            print(cls.values())
            print(u)
            print('2',enrolled.objects.filter(User=u,Class__in=cls).values())
            result = len(enrolled.objects.filter(User=u,strat__lte=d,Class__in=cls).filter(Q(end__gte=d)|Q(end=None)))>0
            return JsonResponse(result,safe=False)
        except ValueError or studio_class.DoesNotExist:
            return HttpResponse(status = 400)
    


# <studio_id>
class Amenities_view(APIView):
    def get(self, request, studio_id):
        try:
            s = Studio.objects.get(id=studio_id)
            return JsonResponse({"Amenity": list(Amenity.objects.filter(
                studio=s).values('type', 'quontity'))})
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned:
            return HttpResponse(status=500)

    # def delete(self, request):
    #    try:
    #       aId = Amenity.objects.get(id=self.kwargs.get('id'))
    #      Images.objects.delete(id=aId)
    # except Images.DoesNotExist:
    #    return HttpResponse(status=404)
    # except Images.MultipleObjectsReturned:
    #   return HttpResponse(status=500)

    def post(self, request: HttpRequest, studio_id):
        try:
            s = Studio.objects.get(id=studio_id)
            t = request.POST.get('type', 'unknown amenity')
            q = request.POST.get('amount', '')
            if not q.isnumeric():
                return HttpResponse(status=400)
            try:
                a = Amenity.objects.get(studio=s, type=t)
                if int(q) == 0:
                    a.delete()
                else:
                    a.quontity = q
                    a.save()
                return HttpResponse(status=200)
            except Amenity.DoesNotExist:
                if int(q) > 0:
                    Amenity.objects.create(studio=s, type=t, quontity=q)
                    return HttpResponse(status=200)
                return HttpResponse(status=400)
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned or Amenity.MultipleObjectsReturned:
            return HttpResponse(status=500)

    # def put(self, request: HttpRequest):
    #   try:
    #      s = Studio.objects.get(id=int(self.kwargs.get('studio_id')))
    #     a = Amenity.objects.get(studio=s, type=self.kwargs.get('type', ''))
    #    a.quontity = self.kwargs.get('quontity')
    # except Studio.DoesNotExist or Amenity.DoesNotExist:
    #   return HttpResponse(status=404)
    # except Studio.MultipleObjectsReturned or Amenity.MultipleObjectsReturned:
    #   return HttpResponse(status=500)


# <stodu_id>
class stodio_class_view(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request: HttpRequest, studio_id):
        try:
            
            s = Studio.objects.get(id=studio_id)
            '''
            classes = studio_class.objects.filter(studio=s)
            class_instances = Class_instance.objects.filter(
                Class__in=classes)
            related_classes = studio_class.objects.filter(
                id__in=class_instances.values('Class')).values()
            # print(related_classes.values())
            id_dic = {}
            for i in related_classes:
                id_dic[i['id']] = i
            # print(id_dic)
            result = list(class_instances.values())
            for i in result:
                #print(i)
                i.update(id_dic[i['Class_id']])
            #print(result)
            '''
            ind=0
            print(ind)
            if request.GET.get('index','').isalnum():
                ind=int(request.GET.get('index',''))
            print(s)
            amount=5
            print(ind)
            if request.GET.get('amount','').isalnum():
                amount=int(request.GET.get('amount',''))
            print(s)

            result = get_all_class_instance(s,ind+amount)[ind:]
            
            return JsonResponse(result,safe=False)
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned:
            return HttpResponse(status=500)

    def post(self, request: HttpRequest, studio_id):
        try:
            s = Studio.objects.get(id=studio_id)
            coach_id = request.POST.get('coach', '')
            try:
                coach = User.objects.get(id=coach_id)
            except ValueError or User.DoesNotExist:
                return HttpResponse(status=400)
            class_name = request.POST.get("name", '')
            class_discription = request.POST.get('description', '')
            start_time = request.POST.get('start_time', '')
            try:
                Start_time = string2time(start_time)
            except ValueError:
                Start_time = datetime.now().time()
            end_time = request.POST.get('end_time', '')
            try:
                End_time = string2time(end_time)
            except ValueError:
                End_time = datetime.now().time()
            start_date = request.POST.get('start_date', '')
            try:
                Start_date = string2date(start_date)
            except ValueError:
                Start_date = date.today()
            end_date = request.POST.get('end_date', '')
            try:
                End_date = string2date(end_date)
            except ValueError:
                End_date = None
            recurse_time = request.POST.get('recurse_time', '7')
            max_size = request.POST.get('max_size', '0')
            sc = studio_class.objects.create(
                studio=s,
                name=class_name,
                description=class_discription,
                coach=coach,
                start_time=Start_time,
                end_time=End_time,
                recurseTime=recurse_time,
                class_size=max_size,
                start_Date = Start_date)
            sc.save()

            add_key_word(request.POST.get('key_word', '').split(','), sc)
            ci = Class_instance.objects.create(Class=sc, strat=Start_date,
                                               end=End_date)
            ci.save()
            return JsonResponse({'class_id': sc.id, 'class_instance_id': ci.id},
                                status=200)
        # except User.DoesNotExist:
        #   return JsonResponse({'msg': 'enter a valid coach'}, status=400)
        except Studio.DoesNotExist:
            return HttpResponse(status=404)
        except Studio.MultipleObjectsReturned or User.MultipleObjectsReturned:
            return HttpResponse(status=500)


class class_edit(APIView):
    # permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    page_size=10
    def post(self, request: HttpRequest):
        print('a')
        if not request.user.is_staff:
            return HttpResponse(status=403)
        Class = request.POST.get('class_id', '')
        try:
            clas = studio_class.objects.get(id=Class)
            d = request.POST.get('date', '')
            if d == '':
                cancel(c=clas)
            else:
                cancel(clas, Date=string2date(d))
            return HttpResponse(status=200)
        except ValueError:
            return HttpResponse(status=400)
        except studio_class.DoesNotExist:
            return HttpResponse(status=404)
        except studio_class.MultipleObjectsReturned:
            return HttpResponse(status=500)

    def get(self, request: HttpRequest):
        
        s=0
        print(s)
        if request.GET.get('index','').isalnum():
            s=int(request.GET.get('index',''))
        print(s)
        sub = get_user_sub(request.user)
        print('sub',sub)
        
        if request.GET.get('h','')=='':
            result = get_user_enrolled_class_instance(request.user,sub,s+self.page_size)[s:]
        else:
            result=get_user_enrolled_class_history(request.user,sub,s+self.page_size)[s:]
        return JsonResponse(result, safe=False, status=200)


# <class_id>/<date>
class User_Enroll_class_view(APIView):
    def put(self, request: HttpRequest, class_id, d):
        user = request.user
        try:
            clas = studio_class.objects.get(id=class_id)
            if not check_Subscription(user, clas.studio):
                return HttpResponse(status=403)
            if d == 'all':
                enroll(user, clas)
            else:
                enroll(user, clas, string2date(d))
            return HttpResponse(status=200)
        except studio_class.DoesNotExist:
            return HttpResponse(status=404)
        except studio_class.MultipleObjectsReturned:
            return HttpResponse(status=500)

    def delete(self, request: HttpRequest, class_id, d):
        user = request.user

        try:
            clas = studio_class.objects.get(id=class_id)
            if not check_Subscription(user, clas.studio):
                return HttpResponse(status=403)
            if d == 'all':
                drop(clas, user)
            else:
                drop(clas, user, string2date(d))
            return HttpResponse(status=200)
        except studio_class.DoesNotExist:
            return HttpResponse(status=404)
        except studio_class.MultipleObjectsReturned:
            return HttpResponse(status=500)


def check_Subscription(user, studio):
    planes = Subscription.objects.filter(studio=studio)
    return len(
        UserSubscription.objects.filter(
            user=user, subscription__in=planes).
        filter(start_time__lte=datetime.now()). \
        filter(end_time__gte=datetime.now())) > 0


# For search and filter
class GetClass_name(APIView):

    def get(self, request):
        """Get a json response of the Studio Class."""
        # try:
        print('111');
        name_input = request.GET.get("name")
        ind = request.GET.get('index','')
        index=0
        if ind.isalnum():
            index=int(ind)
        amo = request.GET.get('amount','')
        amount=0
        if amo.isalnum():
            amount=int(ind)
        result = list(studio_class.objects.filter(name=name_input).values())
        # classes=studio_class.objects.filter(name=name_input)
        print(result)
        # currentday= date.today()
        # print(currentday)

        return JsonResponse({
            "status": 200,
            "message": "The current search's information is as follow:",
            "qualified_class": list(result)[index,min(len(result),index+amount)]
        }, status=200)
        # except Exception as e:
        #     return JsonResponse({
        #         "status": 500,
        #         "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
        #         "error": str(e)
        #     }, status=500)


# For search and filter
class GetClass_time(View):

    def get(self, request):
        """Get a json response of the Studio Class."""
        try:
            time_input = request.GET.get("time").replace("-", "")
            print(type(time_input))
            result = []
            d_input = datetime.strptime(str(time_input),'%Y%m%d')
            print(type(d_input))
            print(d_input)
            # d_input = date(int(time_input[0:4]), int(time_input[4:6]),
            #                int(time_input[6:]))
            
            print(1)
            # temp1 = Class_instance.objects.filter(Q(end__gte=time_input) | Q(end=None) | Q(start__))
            # temp2 = Class_instance.objects.filter(Q(end__gte=None) | Q(end=None))
            # for c in temp1:
            #     year = c.start_date[0:5]
            #     month = c.start_date[5:7]
            #     day = c.start_date[7:]
            #     d_start = date(int(year), int(month), int(day))
            #     delta = d_input - d_start
            #     if (delta % 7 == 0):
            #         result.append(c)
            # for c2 in temp2:
            #     year = c.start_date[0:5]
            #     month = c.start_date[5:7]
            #     day = c.start_date[7:]
            #     d_start = date(int(year), int(month), int(day))
            #     delta = d_input - d_start

            #     if (delta % c2. == 0):
            #         result.append(c2)
            for i in studio_class.objects.all():
                if (check_has_class(i, d_input)):
                    result.append(class_serilization(i))

            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": list(result)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)


class GetClass_range(View):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Get a json response of the Studio Class."""
        try:
            print(1)
            time_input = request.GET.get("time").replace('-', '')
            time_start = time_input[0:8]
            time_end = time_input[9:]
            
            i_start = date(int(time_start[0:4]), int(time_start[4:6]), int(time_start[6:]))
            i_end = date(int(time_end[0:4]), int(time_end[4:6]), int(time_end[6:]))
            if (i_start > i_end):
                return JsonResponse({
                    "status": 403,
                    "message": "Start day must be before or same as the end date"
                })
            

            result = list(studio_class.objects.filter(start_Date__gt=i_start,
                                                      start_Date__lte=i_end).values())
            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": list(result)
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)


class GetClass_coach(View):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Get a json response of the Studio Class."""
        try:
            coach = request.GET.get("coach")
            result = list(studio_class.objects.filter(coach=coach).values())

            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": result
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)


class GetStudio_name(View):
    def get(self, request):
        """Get a json response of the Studio Class."""
        try:
            name = request.GET.get("name")
            name_input = request.GET.get("name")
            ind = request.GET.get('index','')
            index=0
            if ind.isalnum():
                index=int(ind)
            amo = request.GET.get('amount','')
            
            amount=5
            if amo.isalnum():
                amount=int(amount)
            print(index)
            print(Studio.objects.filter(name=name).values())
            result = list(Studio.objects.filter(name=name).values())
            print(result)
            print(min(len(result),index+amount))
            print(len(result))
            print(index+amount)
            print(amo)
            if min(len(result),index+amount)<index:
                return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": []
            }, status=200)
            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": result[index:min(len(result),index+amount)]
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)


class GetStudio_amentities(View):
    pagination_class = StandardResultsSetPagination

    def get(self, request:HttpRequest):
        """Get a json response of the Studio Class."""
        try:
            ame = request.GET.get("amentities")
            ind = request.GET.get('index','')
            index=0
            if ind.isalnum():
                index=int(ind)
            amo = request.GET.get('amount','')
            
            amount=5
            if amo.isalnum():
                amount=int(amount)
            print(index)
            result = list(Amenity.objects.filter(type=ame).values("studio"))
            print("result:", result)
            temp2=[]
            
            for i in result:
                temp=Studio.objects.filter(id=i['studio'])[0]
                temp2.append(temp)

            temp2=list(set(temp2))
            final_result=[]
            for k in temp2:
                final_result.append(studio_serilization(k))
            print(final_result)
            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": final_result[index,min(len(result),index+amount)]
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)


class GetStudio_coach(View):
    def get(self, request):
        """Get a json response of the Studio Class."""
        try:
            ind = request.GET.get('index','')
            index=0
            if ind.isalnum():
                index=int(ind)
            amo = request.GET.get('amount','')
            
            amount=5
            if amo.isalnum():
                amount=int(amount)
            print(index)
            coach = request.GET.get("coach")
            temp = list(studio_class.objects.filter(coach=coach))
            temp2=[];
            for i in temp:
                temp2.append(i.studio);
            temp2 = list(set(temp2))
            result=[]
            for c in temp2:
                result.append(studio_serilization(c))
            
            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": result
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)


class GetStudio_class(View):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Get a json response of the Studio Class."""
        try:
            cla = request.GET.get("class")
            temp = list(studio_class.objects.filter(name=cla))
            temp2=[];
            for i in temp:
                temp2.append(i.studio);
            temp2 = list(set(temp2))
            result=[]
            for c in temp2:
                result.append(studio_serilization(c))
            return JsonResponse({
                "status": 200,
                "message": "The current search's information is as follow:",
                "qualified_class": result
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "INTERNAL SERVER ERROR: Unexpected error happened while retrieving the search result",
                "error": str(e)
            }, status=500)

