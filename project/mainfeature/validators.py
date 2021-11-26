import re


class DataContext:
    def __init__(self, data=None):
        self.value = data
        self.error_msg = None
        self.has_error = True


def validate_str(data):
    context = DataContext(data)
    if not data:
        context.error_msg = 'str형 데이터 중 한 가지가 포함되지 않았거나 형식이 잘못됐습니다.'
        context.value = None
        return context
    elif not (type(data) == str):
        context.error_msg = f'`{data}`는 str 타입이 아닙니다.'
        context.value = None
        return context
    elif not (len(data) <= 255):
        context.error_msg = f'`{data}`의 길이가 255자를 초과합니다.'
        context.value = None
        return context

    context.has_error = False
    return context


def validate_int(data):
    context = DataContext(data)
    if not data:
        context.error_msg = 'int형 데이터 중 한 가지가 포함되지 않았거나 형식이 잘못됐습니다.'
        context.value = None
        return context
    elif not (type(data) == int):
        context.error_msg = f'`{data}`는 int 타입이 아닙니다.'
        context.value = None
        return context

    context.has_error = False
    return context


def validate_date_list(data):
    context = DataContext()
    date_pattern = re.compile('\d{4}-\d{2}-\d{2}') # noqa
    if not data:
        context.error_msg = 'date list가 포함되지 않았습니다.'
        return context
    elif not type(data) == list:
        context.error_msg = 'date를 list에 담아주세요.'
        return context
    date_list = data
    # if type(data) == list:
    #     data = str(data)
    # date_list = re.findall(date_pattern, data)
    # if not date_list:
    #     context.error_msg = '날짜가 포함되지 않았거나, 포함되었지만 형식에서 벗어납니다.'
    #     return context
    for date in date_list:
        if not date_pattern.match(date):
            context.error_msg = f'`{date}`는 올바른 날짜 형식이 아닙니다.'
            return context
        separate_date = date.split('-')
        year = int(separate_date[0])
        month = int(separate_date[1])
        day = int(separate_date[2])
        if not ((1900 <= year <= 2999) and
                (1 <= month <= 12) and
                (1 <= day <= 31)):
            context.error_msg = f'`{date}`은(는) 올바른 날짜가 아닙니다.'
            return context

    context.value = date_list
    context.has_error = False
    return context


def validate_time(data):
    context = DataContext(data)
    time_pattern = re.compile('\d{2}:\d{2}') # noqa
    if not data:
        context.error_msg = 'time형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        context.value = None
        return context
    if not (time_pattern.match(data)):
        context.error_msg = f'`{data}`을(를) `HH:MM` 형식에 맞춰주세요.'
        context.value = None
        return context

    separate_time = data.split(':')
    hour = int(separate_time[0])
    minute = int(separate_time[1])
    if not ((0 <= hour <= 24) and (0 <= minute <= 59)) \
       or (hour == 24 and minute > 0):
        context.error_msg = f'{data}은(는) 올바른 시간이 아닙니다.'
        context.value = None
        return context

    context.has_error = False
    return context


def validate_times(start_time, end_time):
    context = DataContext()

    start_time_cal = int(start_time.value.split(':')[0])
    end_time_cal = int(end_time.value.split(':')[0])
    start_time_min = int(start_time.value.split(':')[1])
    end_time_min = int(start_time.value.split(':')[1])
    if end_time_cal <= start_time_cal:
        msg = 'end_time의 hour은 start_time의 hour보다 작거나 같을 수 없습니다.'
        context.error_msg = msg
        return context
    if not (start_time_min == 0 and end_time_min == 0):
        context.error_msg = 'start_time과 end_time의 minute은 항상 0이어야 합니다.'
        return context

    time_gap = end_time_cal - start_time_cal
    block_quantity = time_gap * 4

    context.value = block_quantity
    context.has_error = False
    return context


def validate_orders(first_order, last_order, group):
    context = DataContext()

    group_last_order = group.timetables.first().timeblocks.last().order
    if group_last_order < last_order:
        msg = 'last_order가 해당 group의 timeblock의 마지막 순서보다 클 수 없습니다.'
        context.error_msg = msg
        return context
    elif first_order < last_order:
        context.value = range(first_order, last_order+1)
        context.has_error = False
        return context
    elif last_order == first_order:
        context.value = range(first_order, first_order+1)
        context.has_error = False
        return context
    elif last_order < first_order:
        context.error_msg = 'first_order는 last_order보다 클 수 없습니다.'
        return context
