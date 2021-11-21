from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Group, TimeBlock, TimeTable
from .serializer import testserializer
from .validators import validate_str, validate_date_list, validate_time

from datetime import datetime, timedelta
import uuid


class GroupAPIView(APIView):
    
    def post(self, request):
        data = request.data
        # 각 필드 유효성 검사 / 알맞게 데이터 파싱
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
        
        # start_time < end_time
        start_time_cal = int(start_time.data.split(':')[0])
        end_time_cal = int(end_time.data.split(':')[0])
        if end_time_cal < start_time_cal:
            context= {
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
