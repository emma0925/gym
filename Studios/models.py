import datetime
import heapq
import queue
from typing import List

from django.db import models
from django.conf import settings
from django.db.models import Q
from Studios.helper import *
#from Accounts.models import UserSubscription

# Create your models here.
class Studio(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)

    def _str_(self):
        return self.name


class Images(models.Model):
    studio = models.ForeignKey(to=Studio, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='images/')


class Amenity(models.Model):
    studio = models.ForeignKey(to=Studio, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    quontity = models.SmallIntegerField()


class studio_class(models.Model):
    studio = models.ForeignKey(to=Studio, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    coach = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # start_date = models.DateField()
    # end_date = models.DateField(null=True, blank=True)
    recurseTime = models.IntegerField()
    class_size = models.IntegerField()
    start_Date = models.DateField()
    # Still_offer=models.BooleanField()
    def __lt__(self, other):
        if other is None:
            return True
        return NotImplemented


class Class_instance(models.Model):
    Class = models.ForeignKey(to=studio_class, on_delete=models.CASCADE)
    strat = models.DateField()
    end = models.DateField(null=True,blank=True)


class enrolled(models.Model):
    Class = models.ForeignKey(to=studio_class, on_delete=models.CASCADE)
    strat = models.DateField()
    end = models.DateField(null=True)
    User = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)


class Canceled_class(models.Model):
    Class = models.ForeignKey(to=studio_class, on_delete=models.CASCADE)
    User = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    Date = models.DateField()


class keyWoards(models.Model):
    word = models.CharField(unique=True, max_length=255)


class look_up_keywoard(models.Model):
    thisClass = models.ForeignKey(to=studio_class, on_delete=models.CASCADE)
    word = models.ForeignKey(to=keyWoards, on_delete=models.CASCADE)


class Subscriptions_Plan(models.Model):
    gym = models.ForeignKey(to=Studio, on_delete=models.CASCADE)
    duriation = models.DateTimeField()
    charge = models.FloatField()


class Subscriptions(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    plan = models.ForeignKey(to=Subscriptions_Plan, on_delete=models.CASCADE)


class enrolled_class(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    Class = models.ForeignKey(to=studio_class, on_delete=models.CASCADE)
    start_time = models.DateField(null=True, blank=True)


'''
    u is a user, c is a a class
'''


def enroll(u, c, Date: datetime.date = None):
    if Date == None:
        if not chack_aleliable_after(c, date.today()):
            return False
        e = enrolled.objects.filter(User=u, Class=c,
                                    strat__lte=date.today(),
                                    end__gte=date.today())
        if e:
            e[0].end = None
            e[0].save()
        else:
            enrolled.objects.create(User=u, Class=c,
                                    strat=date.today(),
                                    end=None).save()

        return True
    elif not (enrolled.objects.filter(User=u, Class=c, strat__lt=Date,
                                      end__gt=Date) or
              enrolled.objects.filter(User=u, Class=c, strat__lt=Date,
                                      end=None)):# and check_aleliable_on_date(c,Date):
        enrolled.objects.create(User=u, Class=c, strat=Date, end=Date).save()
        return True
    return False
    # Canceled_class.objects.filter(User=u).filter(Class=c).delete()
    # if Date is None:
    #   enrolled_class.objects.filter(user=u).delete()
    #  enrolled_class.objects.create(user=u, Class=c).save()
    # else:
    #   enrolled_class.objects.create(user=u, Class=c, d=Date).save()


def check_aleliable_on_date(c: studio_class, d: datetime.date):
    q = Class_instance.objects.filter(Class=c, strat__lte=d).filter(
        Q(end__gte=d) | Q(end=None))
    print(q)
    return q and get_number_on_date(c, d) <= c.class_size


def chack_aleliable_after(c: studio_class, d: datetime.date):
    return len(enrolled.objects.filter(Class=c, strat__gt=d,
                                       end=None)) <= c.class_size


def check_has_class(c: studio_class, Date: datetime.date):
    print(Class_instance.objects.filter(Class=c).values())
    q = Class_instance.objects.filter(Class=c, strat__lte=Date). \
        filter(Q(end__gte=Date) | Q(end=None))
    print(q)
    for i in q:
        if ((Date - datetime.combine(i.strat,
                                              datetime.min.time()))
            % timedelta(
                    i.Class.recurseTime)) <= timedelta(1):
            return True
    return False


def drop(c: studio_class, u, Date: date = None):
    if Date is None:
        # the user drop the class
        for i in enrolled.objects.filter(Class=c, User=u). \
                filter(Q(end__gt=date.today()) | Q(end=None)):
            if i.strat < date.today():
                i.end = date.today()
                i.save()
            else:
                i.delete()
    else:
        #if not check_has_class(c, Date):
         #   print('date does not have class',Date)
          #  return
        print('-------------------------------------------------------------------------------------')
        q = enrolled.objects.filter(Class=c, User=u, strat__lte=Date)
        print(enrolled.objects.filter(Class=c,User=u).values())
        for i in q:
            # if ((Date - datetime.datetime.combine(i.strat,
            #                                     datetime.datetime.min.time()))
            #  % datetime.timedelta(
            #         i.Class.recurseTime)) >= datetime.timedelta(1):

            # no class on that day
            # continue
            # print(last_occurence)
            print(i)
            if i.end is None or datetime.combine(i.end,datetime.min.time()) > Date + timedelta(
                    i.Class.recurseTime):
                enrolled.objects.create(Class=i.Class, User=u,
                                        strat=Date + timedelta(
                                            i.Class.recurseTime),
                                        end=i.end).save()
            if (Date - datetime.combine(i.strat,
                                                 datetime.min.time())) \
                    >= timedelta(i.Class.recurseTime):
                i.end = Date - timedelta(i.Class.recurseTime)
                i.save()
            else:
                i.delete()


'''
    u is a user, c is a a class
'''


def cancel(c: studio_class, u=None, Date: datetime.date = None):
    print('1')
    if Date is None:
        if u is None:
            # deleate the class
            print(Class_instance.objects.filter(Class=c). \
                  filter(Q(end__gte=datetime.date.today()) | Q(end=None)))
            for i in Class_instance.objects.filter(Class=c). \
                    filter(Q(end__gte=datetime.date.today()) | Q(end=None)):
                print(i.strat)
                if i.strat <= datetime.date.today():
                    l = ((datetime.date.today() - i.strat) % datetime.timedelta(
                        i.Class.recurseTime))
                    i.end = datetime.date.today() - l
                    i.save()
                else:
                    print(i.id)
                    i.delete()
            # c.end_date = datetime.date.today()
            # c.save()
        else:
            # the user drop the class
            for i in enrolled.objects.filter(Class=c, User=u,
                                             strat__lt=datetime.date.today()). \
                    filter(Q(end__gt=datetime.date.today()) | Q(end=None)):
                if i.strat < datetime.date.today():
                    i.end = datetime.date.today()
                    i.save()
                else:
                    i.delete()
    else:
        # Canceled_class.objects.create(Class=c, User=u, Date=Date)
        print('2')
        if u is None:
            q = Class_instance.objects.filter(Class=c, strat__lte=Date). \
                filter(Q(end__gt=Date) | Q(end=None))
        else:
            print('3')
            q = enrolled.objects.filter(Class=c, User=u, strat__lte=Date). \
                filter(Q(end__gt=datetime.date.today()) | Q(end=None))
        for i in q:
            if ((Date - datetime.datetime.combine(i.strat,
                                                  datetime.datetime.min.time()))
                % datetime.timedelta(
                        i.Class.recurseTime)) >= datetime.timedelta(1):
                # no class on that day
                continue
            # print(last_occurence)
            print(i.end)
            print(Date + datetime.timedelta(i.Class.recurseTime))
            print(Date)

            if i.end is None or datetime.datetime.combine(i.end,
                                                          datetime.datetime.min.time()) > Date + datetime.timedelta(
                    i.Class.recurseTime):
                Class_instance.objects.create(Class=i.Class,
                                              strat=Date + datetime.timedelta(
                                                  i.Class.recurseTime),
                                              end=i.end).save()
            if (Date - datetime.datetime.combine(i.strat,
                                                 datetime.datetime.min.time())) >= datetime.timedelta(
                i.Class.recurseTime):
                i.end = Date - datetime.timedelta(i.Class.recurseTime)
                i.save()
            else:
                i.delete()


def get_cancled(u=None):
    if u is None:
        return Canceled_class.objects.filter(User=None)
    return Canceled_class.objects.filter(User__in=[None, u])


def add_key_word(key_words: List[str], c):
    kws = keyWoards.objects.filter(word__in=key_words)
    for kw in kws:
        if len(look_up_keywoard.objects.filter(word=kw).filter(
                thisClass=c)) == 0:
            look_up_keywoard.objects.create(thisClass=c, word=kw).save()


def get_number_on_date(c: studio_class, d: datetime.date):
    return len(enrolled.objects.filter(Class=c, strat__lt=d). \
               filter(Q(end__gt=d) | Q(end=None)))


def get_number_after(c: studio_class, start: datetime.date):
    a = enrolled.objects.filter(Class=c, strat__gt=start). \
        filter(Q(end__gt=start) | Q(end=None)).order_by(start)
    if len(a) > 0:
        curr = [a[0].end]
        for i in a:
            if i.strat < a[0]:
                heapq.heappop(curr)
            heapq.heappush(curr, i.end)
        return max(len(curr), get_number_on_date(c, start))
    return 0


def get_enrolled(u):
    q = enrolled.objects.filter(User=u)
    p = Class_instance.objects.filter(Class__in=q.values('Class'))
    d = {}
    for i in q:
        if not i.Class.id in d.keys():
            d[i.Class.id] = (i.Class.name, [(i.strat, i.end)], [])
        else:
            d[i.Class.id][1].append((i.strat, i.end))
    # print(d)
    for i in p:
        d[i.Class.id][-1].append((i.strat, i.end))
    # print(d)
    return d



def get_all_class_instance(c:Studio,amount:int):
    classes = studio_class.objects.filter(studio=c)
    print(classes.values(),date.today())
    e = Class_instance.objects.filter(Class__in=classes).filter(Q(end__gte=date.today())|Q(end=None))
    all_classes = {}
    for i in e:
        if not i.Class in all_classes:
            all_classes[i.Class]=[]
        all_classes[i.Class].append((i.strat,i.end))
    result = {}
    print("r",all_classes)
    for i in all_classes.keys():
        result[i]=merge_intervals(all_classes[i])
    return get_all_occurence(result,amount,date.today())




def get_all_occurence(c:dict[studio_class,List[tuple[date,date]]], amount:int,start_date=None,end_date=None):
    result = []
    all =[]
    print(c)
    for i in c.keys():
        for j in c[i]:
            heapq.heappush(all,(caulate_first(i,j[0]),i.id,i,j[1]))
    print(all)
    while (len(all)>0) and len(result)<=amount:
        t,id,h, q = heapq.heappop(all)
        print('tttttttttttttttt',t,end_date)
        if end_date is not None and t>end_date:
            return result
        if not start_date or t>=start_date:
            result.append((t,class_serilizer(h)))
        
        print('wwwwww',t,start_date)
        print(t+timedelta(h.recurseTime))
        #print(q+timedelta(days=0))
        print("all",all)
        if q is None or t+timedelta(h.recurseTime)<=q+timedelta(days=0):
            print((t+timedelta(h.recurseTime),id,h,q))
            heapq.heappush(all,(t+timedelta(h.recurseTime),id,h,q))
    return result

def class_serilizer(c:studio_class):
    return {'id':c.id,'name':c.name,'start_time':c.start_time,'end_time':c.end_time}

def get_occurence_in_interval(c:List[studio_class],interval:tuple[date,date],amount:int):
    result = []
    all =[]
    for i in c:
        heapq.heappush((caulate_first(i,interval[0]),c))
    while (interval[1] is None or all[0][0]<=interval[1]) and len(result)<=amount:
        t,h = heapq.heappop(all)
        heapq.heappush((t+h.recurseTime,h))
        result.append((t,h))
    return result

def caulate_first(c:studio_class,d:datetime):
    return (d-(d - c.start_Date) % timedelta(c.recurseTime))+timedelta(c.recurseTime)


def get_occurence_in_intervals(c:List[studio_class],intervals:List[tuple[date,date]],amount:int):
    result =[]
    for i in intervals:
        result=result+get_occurence_in_interval(c,i,amount-len(result))
    return result




def get_user_enrolled_class_instance(u,subscription:dict,amount:int, c:studio_class=None):
    e = get_enrolled2(u)
    print(e)
    result={}
    for i in e:
        print(i.studio.id)
        if i.studio.id in subscription.keys():
            result[i]=intervalIntersection(intervalIntersection(merge_intervals(e[i][1]),merge_intervals(e[i][2])),subscription[i.studio.id])
    print(result)
        #s = subscription[i]
        #lst = []
        #for j in s:
         #   lst.append([j.start_time,j.end_time])
        #e[i]=intervalIntersection(lst,e[i])
    return get_all_occurence(result,amount,date.today())



def get_enrolled2(u):
    q = enrolled.objects.filter(User=u)
    p = Class_instance.objects.filter(Class__in=q.values('Class')).order_by('strat')
    d = {}
    for i in q:
        if not i.Class in d.keys():
            d[i.Class] = (i.Class.name, [(i.strat, i.end)], [])
        else:
            d[i.Class][1].append((i.strat, i.end))
    # print(d)
    for i in p:
        d[i.Class][-1].append((i.strat, i.end))
    # print(d)
    return d



def get_user_enrolled_class_history(u,subscription:dict,amount:int, c:studio_class=None):
    e = get_enrolled2(u)
    print(e)
    result={}
    for i in e:
        print(i.studio.id)
        if i.studio.id in subscription.keys():
            result[i]=intervalIntersection(intervalIntersection(merge_intervals(e[i][1]),merge_intervals(e[i][2])),subscription[i.studio.id])
    print(result)
        #s = subscription[i]
        #lst = []
        #for j in s:
         #   lst.append([j.start_time,j.end_time])
        #e[i]=intervalIntersection(lst,e[i])
    return get_all_occurence(result,amount,end_date=date.today())