from datetime import datetime
import uuid

from .models import Group, TimeTable, TimeBlock
from .validators import validate_str, validate_date_list, validate_time, \
                        validate_times

from django.db.models import Count, Max


class GroupContext:

    def __init__(self):
        self.error = {'status': 400, 'success': False}
        self.data = {'status': 200, 'success': True}
        self.has_error = True


def GroupRetrieveProcessor(group_id):
    context = GroupContext()
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
        context = GroupContext()

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
            name=group_name.data,
            group_id=group_id
        )
        # timetable 생성
        for date in dates.data:
            timetable = TimeTable.objects.create(
                date=date,
                start_time=start_time.data,
                end_time=end_time.data,
                group=group
            )
            # timeblock 생성
            for i in range(1, block_quantity.data+1):
                TimeBlock.objects.create(
                    order=i,
                    timetable=timetable
                )
        context.data['data'] = {
                'id': group.pk,
                "group_name": group_name.data,
                "group_id": group_id,
                "dates": dates.data,
                "start_time": start_time.data,
                "end_time": end_time.data
                }
        context.data['status'] = 201
        context.has_error = False
        context.error = None
        return context
