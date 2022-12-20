import datetime
from typing import Dict, List
from datetime import date, time, timedelta, datetime


def get_Class_instance(Data: Dict, canceled, cirrtime):
    return Class_instance(canceled, Data['start_date'] + Data['start_time'],
                          Data['recurseTime'], cirrtime, Data,
                          Data['end_date'])


class Class_instance:
    canceled = []
    next_section = None
    period = None
    end_time = None
    data = None


    def __init__(self, canceled: List, start_time: datetime, recursion_time,
                 currtime, Data, end_time=None):
        self.data = Data
        self.canceled = list(filter(lambda s: s >= currtime, canceled))
        self.next_section = timedelta(recursion_time) - (
                (datetime.now() - start_time) % timedelta(
            recursion_time)) + datetime.now()
        self.period = recursion_time
        self.end_time = end_time
        if self.end_time is not None and self.next_section > self.end_time:
            self.next_section = None
    def check(self):
        if self.end_time is not None and self.next_section > self.end_time:
            self.next_section = None
        if len(list(filter(lambda s: s - self.next_section < timedelta(1),
                           self.canceled))):
            self.next()
    def next(self):
        self.next_section = self.next_section + self.period
        if self.end_time is not None and self.next_section > self.end_time:
            self.next_section = None

    def __lt__(self, other):
        assert type(other) == type(self)
        if self.next_section is None:
            return False
        if other.next_section is None:
            return True
        return self.next_section < other.next_section

    def __gt__(self, other):
        assert type(other) == type(self)
        if self.next_section is None:
            return True
        if other.next_section is None:
            return False
        return self.next_section > other.next_section


def parent(index: int):
    if index <= 0:
        return 0
    return (index - 1) // 2


class class_heap:
    data: List[Class_instance]

    def __init__(self):
        self.data = []

    def left(self, index: int):
        result = 2 * index + 1
        if result >= len(self.data):
            return None
        return result

    def right(self, index: int):
        result = 2 * index + 2
        if result >= len(self.data):
            return None
        return result

    def fix_up(self, index: int):
        if index <= 0:
            return
        i = parent(index)
        if self.data[i] > self.data[index]:
            self.data[i], self.data[index] = self.data[index], self.data[i]
            self.fix_up(i)

    def fix_down(self, index: int):
        if index >= len(self.data) / 2:
            return
        left = self.left(index)
        minimum = index
        if left is not None and self.data[left] < self.data[minimum]:
            minimum = left
        right = self.right(index)
        if right is not None and self.data[right] < self.data[minimum]:
            minimum = right
        if not minimum == index:
            self.data[minimum], self.data[index] = self.data[index], self.data[
                minimum]
            self.fix_down(minimum)

    def insert(self, element: Class_instance):
        self.data.append(element)
        self.fix_up(len(self.data) - 1)

    def get_next(self):
        result = (self.data[0].data, self.data[0].next_section)
        self.data[0].next()
        self.fix_down(0)
        return result


def get(input: List[Dict], canceled: List[Dict], t: datetime = None):
    if t is None:
        t = datetime.now()
    c = {}
    for i in input:
        c[i['id']] = []
    for i in canceled:
        if i['Class'] in c.keys():
            c[i].append(i['Date'])
    ch = class_heap()
    for i in input:
        class_id = i['id']
        ch.insert(get_Class_instance(i,c[class_id],t))
    return ch



#return class description
#