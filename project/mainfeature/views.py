from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .processors import GroupRetrieveProcessor, GroupCreateProcessor, \
                        MemberPostProcessor, TimesetProcessor


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


class MemberAPIView(APIView):

    def post(self, request):
        group_id = request.data.get('group_id')
        name = request.data.get('name')
        context = MemberPostProcessor(group_id, name)
        if context.has_error:
            return Response(context.error, status=status.HTTP_400_BAD_REQUEST)
        elif context.data['status'] == 200:
            return Response(context.data, status=status.HTTP_200_OK)
        elif context.data['status'] == 201:
            return Response(context.data, status=status.HTTP_201_CREATED)


class TimesetAPIView(APIView):

    def post(self, request):
        data = request.data

        member_pk = data.get('member_pk')
        first_order = data.get('first_order')
        last_order = data.get('last_order')
        dates = data.get('dates')
        change_to = data.get('change_to')
        group_id = data.get('group_id')

        context = TimesetProcessor(member_pk, first_order, last_order,
                                   dates, change_to, group_id)

        if context.has_error:
            return Response(context.error, status=status.HTTP_400_BAD_REQUEST)
        return Response(context.data, status=status.HTTP_200_OK)
