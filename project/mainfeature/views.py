from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Group, TimeBlock, TimeTable
from .validators import validate_str, validate_date_list, validate_time

import uuid
from datetime import datetime


class GroupAPIView(APIView):

    def get(self, request):
        context = {'status': 400, 'success': False}
        group_id = request.query_params.get('group_id')
        if not group_id:
            context['msg'] = 'group_id 쿼리스트링을 포함하여 요청을 보내주세요.'
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        group = Group.objects.filter(group_id=group_id)
        if not group:
            context['msg'] = '유효하지 않은 group_id입니다.'
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        context['timetables'] = []

        timetables = group[0].timetables.all()
        for table in timetables:
            table_data = {}
            table_data['id'] = table.pk
            table_data['date'] = table.date
            table_data['day'] = datetime.strptime(table.date, '%Y-%m-%d'
                                       ).strftime('%a')
            table_data['start_time'] = table.start_time
            table_data['end_time'] = table.end_time
            table_data['timeblocks'] = []

            member_list = group[0].members.all().values_list('name')
            member_list = [name[0] for name in member_list]
            timeblocks = table.timeblocks.all()
            for block in timeblocks:
                avail_list = block.avail_members.all().values_list('name')
                avail_list = [name[0] for name in avail_list]
                unavails = set(member_list) - set(avail_list)
                block_data = {
                    'id': block.pk,
                    'order': block.order,
                    'avail_members': list(avail_list),
                    'unavail_members': list(unavails),
                    'avail_count': len(avail_list)
                    }
                table_data['timeblocks'].append(block_data)
            context['timetables'].append(table_data)

        context['status'] = 200
        context['success'] = True
        return Response(context, status.HTTP_200_OK)


        

    def post(self, request):
        print(set(TimeTable.objects.first().timeblocks.all()))
        data = request.data
        # 각 필드 유효성 검사 / 알맞게 데이터 변환
        group_name = validate_str(data.get('group_name'))
        dates = validate_date_list(data.get('dates'))
        start_time = validate_time(data.get('start_time'))
        end_time = validate_time(data.get('end_time'))
        if group_name.has_error:
            return Response(group_name.error,
                            status=status.HTTP_400_BAD_REQUEST)
        elif dates.has_error:
            return Response(dates.error,
                            status=status.HTTP_400_BAD_REQUEST)
        elif start_time.has_error:
            return Response(start_time.error,
                            status=status.HTTP_400_BAD_REQUEST)
        elif end_time.has_error:
            return Response(end_time.error,
                            status=status.HTTP_400_BAD_REQUEST)

        start_time_cal = int(start_time.data.split(':')[0])
        end_time_cal = int(end_time.data.split(':')[0])
        if end_time_cal < start_time_cal:
            context = {
                'status': 400,
                'success': False,
                'msg': 'end_time은 start_time보다 작을 수 없습니다.'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        time_gap = end_time_cal - start_time_cal
        block_quantity = time_gap * 4

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
            for i in range(1, block_quantity+1):
                TimeBlock.objects.create(
                    order=i,
                    timetable=timetable
                )
        context = {
            "status": 201,
            "success": True,
            "data": {
                "group_name": group_name.data,
                "group_id": group_id,
                "dates": dates.data,
                "start_time": start_time.data,
                "end_time": end_time.data
                }
            }
        return Response(context, status=status.HTTP_200_OK)
