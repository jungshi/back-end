import re


class DataContext:
    def __init__(self, data=None):
        self.data = data
        self.error_msg = None
        self.has_error = True


def validate_str(data):
    context = DataContext(data)
    if not data:
        context.error_msg = 'str형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        context.data = None
        return context
    elif not (type(data) == str):
        context.error_msg = f'`{data}`는 str 타입이 아닙니다.'
        context.data = None
        return context
    elif not (len(data) <= 255):
        context.error_msg = f'`{data}`의 길이가 255자를 초과합니다.'
        context.data = None
        return context

    context.has_error = False
    return context


def validate_date_list(data):
    context = DataContext()
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    if not data:
        context.error_msg = 'date형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        return context
    if type(data) == list:
        data = str(data)
    date_list = re.findall(date_pattern, data)
    if not date_list:
        context.error_msg = '날짜가 포함되지 않았거나, 포함되었지만 형식에서 벗어납니다.'
        return context
    for date in date_list:
        separate_date = date.split('-')
        year = int(separate_date[0])
        month = int(separate_date[1])
        day = int(separate_date[2])
        if not ((1900 <= year <= 2999) and
                (1 <= month <= 12) and
                (1 <= day <= 31)):
            context.error_msg = f'{date}은(는) 올바른 날짜가 아닙니다.'
            return context

    context.data = date_list
    context.has_error = False
    return context


def validate_time(data):
    context = DataContext(data)
    time_format = re.compile('\d{2}:\d{2}') # noqa
    if not data:
        context.error_msg = 'time형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        context.data = None
        return context
    if not (time_format.match(data)):
        context.error_msg = f'`{data}`을(를) `HH:MM` 형식에 맞춰주세요.'
        context.data = None
        return context

    separate_time = data.split(':')
    hour = int(separate_time[0])
    minute = int(separate_time[1])
    if not ((0 <= hour <= 24) and (0 <= minute <= 59)) \
       or (hour == 24 and minute > 0):
        context.error_msg = f'{data}은(는) 올바른 시간이 아닙니다.'
        context.data = None
        return context

    context.has_error = False
    return context


def validate_times(start_time, end_time):
    context = DataContext()

    start_time_cal = int(start_time.data.split(':')[0])
    end_time_cal = int(end_time.data.split(':')[0])
    if end_time_cal < start_time_cal:
        context.error_msg = 'end_time은 start_time보다 작을 수 없습니다.'
        return context

    time_gap = end_time_cal - start_time_cal
    block_quantity = time_gap * 4

    context.data = block_quantity
    context.has_error = False
    return context
