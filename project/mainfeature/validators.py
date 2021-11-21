import re


class Context:
    def __init__(self, data=None):
        self.data = data
        self.error = {'status': 400, 'success': False}
        self.has_error = True


def validate_str(data):
    context = Context()
    if not data:
        context.error['msg'] = 'str형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        return context
    elif not (type(data) == str):
        context.error['msg'] = f'`{data}`는 str 타입이 아닙니다.'
        return context
    elif not (len(data) <= 255):
        context.error['msg'] = f'`{data}`의 길이가 255자를 초과합니다.'
        return context
    context.data = data
    context.error = None
    context.has_error = False
    return context


def validate_date_list(data):
    context = Context()
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    if not data:
        context.error['msg'] = 'date형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        return context
    date_list = re.findall(date_pattern, data)
    print(date_list)
    if not date_list:
        context.error['msg'] = '날짜가 포함되지 않았거나, 포함되었지만 형식에서 벗어납니다.'
        return context
    for date in date_list:
        separate_date = date.split('-')
        year = int(separate_date[0])
        month = int(separate_date[1])
        day = int(separate_date[2])
        if not ((1900 <= year <= 2999) and
                (1 <= month <= 12) and
                (1 <= day <= 31)):
            context.error['msg'] = f'{date}은(는) 올바른 날짜가 아닙니다.'
            return context
    context.data = date_list
    context.error = None
    context.has_error = False
    return context


def validate_time(data):
    context = Context()
    time_format = re.compile('\d{2}:\d{2}') # noqa
    if not data:
        context.error['msg'] = 'time형 데이터 중 최소 한 가지가 포함되지 않았습니다.'
        return context
    if not (time_format.match(data)):
        context.error['msg'] = f'`{data}`을(를) `HH:MM` 형식에 맞춰주세요.'
        return context
    separate_time = data.split(':')
    hour = int(separate_time[0])
    minute = int(separate_time[1])
    if not ((0 <= hour <= 24) and (0 <= minute <= 59)) \
       or (hour == 24 and minute > 0):
        context.error['msg'] = f'{data}은(는) 올바른 시간이 아닙니다.'
        return context
    context.data = data
    context.error = None
    context.has_error = False
    return context
