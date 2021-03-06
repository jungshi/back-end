from datetime import datetime
import uuid

from .models import Group, TimeTable, TimeBlock, Member
from .validators import validate_str, validate_date_list, validate_time, \
                        validate_times, validate_int, validate_orders

from django.db.models import Count, Max


class Context:

    def __init__(self):
        self.error = {}
        self.data = {}
        self.has_error = True


def GroupRetrieveProcessor(group_id):
    context = Context()

    if not (type(group_id) == str):
        msg = 'group_id가 쿼리스트링으로 포함되지 않았거나, 형식이 잘못되었습니다.'
        context.error['msg'] = msg
        context.data = None
        return context

    group = Group.objects.filter(group_id=group_id)
    if not group:
        msg = '유효하지 않은 group_id입니다.'
        context.error['msg'] = msg
        context.data = None
        return context

    timetables = group[0].timetables.all()
    block_count = timetables.first().timeblocks.count()
    context.data['block_count'] = block_count
    context.data['timetables'] = []
    for table in timetables:
        table_data = {}
        table_data['id'] = table.pk
        table_data['date'] = table.date
        table_data['day'] = datetime.strptime(table.date, '%Y-%m-%d'
                                              ).strftime('%a')
        table_data['start_time'] = table.start_time
        table_data['end_time'] = table.end_time

        table_data['timeblocks'] = []
        timeblocks = table.timeblocks.all()
        member_list = group[0].members.all().values_list('name')
        member_list = [name[0] for name in member_list]
        for block in timeblocks:
            avail_list = block.avail_members.all().values_list('name')
            avail_list = [name[0] for name in avail_list]
            unavail_list = list(set(member_list) - set(avail_list))
            block_data = {
                'id': block.pk,
                'order': block.order,
                'avail_members': avail_list,
                'unavail_members': unavail_list,
                'avail_count': len(avail_list)
                }
            table_data['timeblocks'].append(block_data)
        context.data['timetables'].append(table_data)

    context.data['member_count'] = len(member_list)
    timeblocks = TimeBlock.objects.filter(timetable__group=group[0])
    timeblocks = timeblocks.annotate(avails_count=Count('avail_members'))
    max_count = timeblocks.aggregate(max_count=Max('avails_count')
                                     )['max_count']
    context.data['avails_max_count'] = max_count
    context.error = None
    context.has_error = False
    return context


def GroupCreateProcessor(group_name, dates, start_time, end_time):
    context = Context()

    group_name = validate_str(group_name)
    dates = validate_date_list(dates)
    start_time = validate_time(start_time)
    end_time = validate_time(end_time)

    validate_list = [group_name, dates, start_time, end_time]
    for value in validate_list:
        if value.has_error:
            context.error['msg'] = value.error_msg
            context.data = None
            return context

    block_quantity = validate_times(start_time, end_time)
    if block_quantity.has_error:
        context.error['msg'] = block_quantity.error_msg
        context.data = None
        return context

    # group 생성
    group_id = uuid.uuid4()
    group = Group.objects.create(
        name=group_name.value,
        group_id=group_id
    )
    # timetable 생성
    for date in dates.value:
        timetable = TimeTable.objects.create(
            date=date,
            start_time=start_time.value,
            end_time=end_time.value,
            group=group
        )
        # timeblock 생성
        for i in range(1, block_quantity.value+1):
            TimeBlock.objects.create(
                order=i,
                timetable=timetable
            )

    context.data['id'] = group.pk
    context.data['group_name'] = group_name.value
    context.data['group_id'] = group_id
    context.data['dates'] = dates.value
    context.data['start_time'] = start_time.value
    context.data['end_time'] = end_time.value
    context.has_error = False
    context.error = None
    return context


def MemberPostProcessor(group_id, name):
    context = Context()

    group_id = validate_str(group_id)
    name = validate_str(name)

    validate_list = [group_id, name]
    for value in validate_list:
        if value.has_error:
            context.error['msg'] = value.error_msg
            context.data = None
            return context

    group = Group.objects.filter(group_id=group_id.value)
    if not group:
        context.error['msg'] = '잘못된 group_id입니다.'
        context.data = None
        return context

    member = group[0].members.filter(name=name.value)
    if member:
        context.data['timetables'] = []
        for table in group[0].timetables.all():
            table_data = {'timeblocks': []}
            table_data['id'] = table.pk
            table_data['date'] = table.date
            for block in table.timeblocks.all():
                block_data = {}
                block_data['order'] = block.order
                block_data['avail'] = member[0] in block.avail_members.all()
                table_data['timeblocks'].append(block_data)
            context.data['timetables'].append(table_data)
        context.data['member_id'] = member[0].pk
        context.has_error = False
        context.error = None
        return context

    member = Member.objects.create(
        group=group[0],
        name=name.value
    )
    context.data['member_id'] = member.pk
    context.data['msg'] = f'멤버 {member.name}이(가) 성공적으로 생성되었습니다.'
    context.has_error = False
    context.error = None
    return context


def TimesetProcessor(member_id, first_order, last_order,
                     table_pk_list, change_to, group_id):
    context = Context()

    if not ((change_to == 'avail') or (change_to == 'unavail')):
        msg = '`change_to`의 값은 `avail` 혹은 `unavail`이어야 합니다.'
        context.error['msg'] = msg
        context.data = None
        return context
    
    if not (table_pk_list and type(table_pk_list) == list):
        msg = 'table_pk_list가 없거나, 올바른 형식이 아닙니다.'
        context.error['msg'] = msg
        context.data = None
        return context

    member_id = validate_int(member_id)
    first_order = validate_int(first_order)
    last_order = validate_int(last_order)
    group_id = validate_str(group_id)

    validate_list = [member_id, first_order, last_order, group_id]
    for value in validate_list:
        if value.has_error:
            context.error['msg'] = value.error_msg
            context.data = None
            return context

    group = Group.objects.filter(group_id=group_id.value)
    if not group:
        context.error['msg'] = '잘못된 group_id입니다.'
        context.data = None
        return context

    member = group[0].members.filter(pk=member_id.value)
    if not member:
        context.error['msg'] = '잘못된 member_id입니다.'
        context.data = None
        return context

    order_range = validate_orders(first_order.value, last_order.value,
                                  group[0])
    if order_range.has_error:
        context.error['msg'] = order_range.error_msg
        context.data = None
        return context

    timetables = group[0].timetables.all()
    real_pk_set = {table.pk for table in timetables}
    is_valid_tables = set(table_pk_list) <= real_pk_set
    if not is_valid_tables:
        msg = 'table_pk_list에 올바르지 않은 pk가 포함되어 있습니다.'
        context.error['msg'] = msg
        context.data = None
        return context

    if change_to == 'avail':
        for pk in table_pk_list:
            timeblocks = TimeBlock.objects.filter(timetable__group=group[0])
            timeblocks = timeblocks.filter(timetable__pk=pk)
            for order in order_range.value:
                timeblock = timeblocks.get(order=order)
                timeblock.avail_members.add(member[0])
                timeblock.save()
    elif change_to == 'unavail':
        for pk in table_pk_list:
            timeblocks = TimeBlock.objects.filter(timetable__group=group[0])
            timeblocks = timeblocks.filter(timetable__pk=pk)
            for order in order_range.value:
                timeblock = timeblocks.get(order=order)
                timeblock.avail_members.remove(member[0])
                timeblock.save()
    context.data['msg'] = '성공적으로 반영되었습니다.'
    context.has_error = False
    context.error = None
    return context
