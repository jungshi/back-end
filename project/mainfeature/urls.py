from django.urls import path

from .views import GroupAPIView, MemberAPIView

urlpatterns = [
    path('groups/', GroupAPIView.as_view(), name='group'),
    path('members/', MemberAPIView.as_view(), name='member')
]
