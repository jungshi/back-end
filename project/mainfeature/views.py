from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .validators import validate_str, validate_date_list, validate_time
from .processors import GroupRetrieveProcessor, GroupCreateProcessor


class GroupAPIView(APIView):

    def get(self, request):
        group_id = request.query_params.get('group_id')
        context = GroupRetrieveProcessor(group_id)
        if context.has_error:
            return Response(context.error, status=status.HTTP_400_BAD_REQUEST)
        return Response(context.data, status.HTTP_200_OK)

    def post(self, request):
        data = request.data

        group_name = data.get('group_name')
        dates = data.get('dates')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        context = GroupCreateProcessor(group_name, dates, start_time, end_time)
        if context.has_error:
            return Response(context.error, status=status.HTTP_400_BAD_REQUEST)
        return Response(context.data, status=status.HTTP_201_CREATED)
