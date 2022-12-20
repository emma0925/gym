from datetime import date, time, timedelta, datetime


def date2string(d: date):
    return d.strftime('%Y-%m-%d')


def string2date(d: str):
    return datetime.strptime(d, "%Y-%m-%d")


def string2time(d: str):
    return datetime.strptime(d, '%H-%M-%S').time()

def merge_intervals(intervals):
  print(intervals)
  # Sort the intervals by start time
  intervals.sort(key=lambda x: x[0])

  # Initialize the merged intervals list with the first interval
  merged = [intervals[0]]

  # Loop through the rest of the intervals
  for current in intervals[1:]:
    previous = merged[-1]
    # If the current interval overlaps with the previous one, merge them
    if previous[1] is None or current[0] <= previous[1]:
        previous=list(previous)
    #   previous[1] = max(previous[1], current[1])
        previous[1] =  max(previous[1], current[1]);
        previous = tuple(previous)
        
    else:
      # If they don't overlap, append the current interval to the merged list
      merged.append(current)

  return merged

# Merge_interval 测试
# datetime_str1 = '2022/09/25 13:55'
# datetime_obj1 = datetime.strptime(datetime_str1, '%Y/%m/%d %H:%M')
# datetime_str2 = '2022/12/25 13:55'
# datetime_obj2 = datetime.strptime(datetime_str2, '%Y/%m/%d %H:%M')
# datetime_str3 = '2022/10/8 13:55'
# datetime_obj3 = datetime.strptime(datetime_str3, '%Y/%m/%d %H:%M') #obj3 and obj4 should be 
# datetime_str4 = '2022/10/24 13:55'
# datetime_obj4 = datetime.strptime(datetime_str4, '%Y/%m/%d %H:%M')
# datetime_str5 = '2021/10/8 13:55'
# datetime_obj5 = datetime.strptime(datetime_str5, '%Y/%m/%d %H:%M')
# datetime_str6 = '2023/10/24 13:55'
# datetime_obj6 = datetime.strptime(datetime_str6, '%Y/%m/%d %H:%M')

# a=[(datetime_obj1, datetime_obj2), (datetime_obj3, datetime_obj4), (datetime_obj5, datetime_obj6)]
# print(merge_intervals(a))



def intervalIntersection(firstList, secondList):
        """
        :type firstList: List[List[int]]
        :type secondList: List[List[int]]
        :rtype: List[List[int]]
        """
        i=0
        j=0
        result =[]
        while i<len(firstList) and j<len(secondList):
            first = firstList[i]
            second = secondList[j]
            if second[1] is not None and first[0]>second[1]:
                j+=1
            elif first[1] is not None and second[0]>first[1]:
                i+=1
            elif first[0]>=second[0]:
                if first[1] is None or (second[1] is not None and first[1]>second[1]):
                    result.append([first[0],second[1]])
                    j+=1
                else:
                    result.append([first[0],first[1]])
                    i+=1
            elif second[0]>=first[0]:
                if second[1] is None or (first[1] is not None and second[1]>first[1]):
                    result.append([second[0],first[1]])
                    i+=1
                else:
                    result.append([second[0],second[1]])
                    j+=1
            
        return result

