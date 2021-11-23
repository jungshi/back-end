from datetime import datetime
import uuid

from .models import Group, TimeTable, TimeBlock, Member
from .validators import validate_str, validate_date_list, validate_time, \
                        validate_times

from django.db.models import Count, Max


class Context:

    def __init__(self):
        self.error = {'status': 400, 'success': False}
        self.data = {'status': 200, 'success': True, 'data': {}}
        self.has_error = True


def GroupRetrieveProcessor(group_id):
    context = Context()
    if not group_id:
        context.data = None
        context.error['msg'] = 'group_id 쿼리스트링을 포함하여 요청을 보내주세요.'
        return context

    group = Group.objects.filter(group_id=group_id)
    if not group:
        context.data = None
        context.error['msg'] = '유효하지 않은 group_id입니다.'
        return context

    timetables = group[0].timetables.all()
    block_count = timetables.first().timeblocks.count()
    context.data['data']['block_count'] = block_count
    context.data['data']['timetables'] = []
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
        context.data['data']['timetables'].append(table_data)

    context.data['data']['member_count'] = len(member_list)
    timeblocks = TimeBlock.objects.filter(timetable__group=group[0])
    timeblocks = timeblocks.annotate(avails_count=Count('avail_members'))
    max_count = timeblocks.aggregate(max_count=Max('avails_count')
                                                  )['max_count']
    context.data['data']['avails_max_count'] = max_count
    context.error = None
    context.has_error = False
    return context


def GroupCreateProcessor(group_name, dates, start_time, end_time):
        context = Context()

        group_name = validate_str(group_name)
        dates = validate_date_list(dates)
        start_time = validate_time(start_time)
        end_time = validate_time(end_time)

        if group_name.has_error:
            context.error['msg'] = group_name.error_msg
            context.data = None
            return context
        elif dates.has_error:
            context.error['msg'] = dates.error_msg
            context.data = None
            return context
        elif start_time.has_error:
            context.error['msg'] = start_time.error_msg
            context.data = None
            return context
        elif end_time.has_error:
            context.error['msg'] = end_time.error_msg
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

        context.data['data']['id'] = group.pk
        context.data['data']['group_name'] = group_name.value
        context.data['data']['group_id'] = group_id
        context.data['data']['dates'] = dates.value
        context.data['data']['start_time'] = start_time.value
        context.data['data']['end_time'] = end_time.value
        context.data['status'] = 201
        context.has_error = False
        context.error = None
        return context


def MemberPostProcessor(group_id, name):
    context = Context()

    group_id = validate_str(group_id)
    name = validate_str(name)
    if group_id.has_error:
        context.error['msg'] = group_id.error_msg
        context.data = None
        return context
    if name.has_error:
        context.error['msg'] = name.error_msg
        context.data = None
        return context

    group = Group.objects.filter(group_id=group_id.value)
    if not group:
        context.error['msg'] = '잘못된 group_id입니다.'
        context.data = None
        return context
    
    member = group[0].members.filter(name=name.value)
    if member:
        context.data['data']['timetables'] = []
        for table in group[0].timetables.all():
            table_data = {}
            table_data['id'] = table.pk
            table_data['date'] = table.date
            order_list = member[0].timeblocks.filter(timetable=table
                                                    ).values_list('order')
            order_list = [order[0] for order in order_list]
            table_data['avail_orders'] = order_list
            context.data['data']['timetables'].append(table_data)
        context.has_error = False
        context.error = None
        return context

    member = Member.objects.create(
        group=group[0],
        name=name.value
    )
    context.data['data']['msg'] = f'멤버 {member.name}이(가) 성공적으로 생성되었습니다.'
    context.data['status'] = 201
    context.has_error = False
    context.error = None
    return context