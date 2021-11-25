from django.urls import path

from .views import GroupAPIView, MemberAPIView, TimesetAPIView

urlpatterns = [
    path('groups/', GroupAPIView.as_view(), name='group'),
    path('members/', MemberAPIView.as_view(), name='member'),
    path('time/', TimesetAPIView.as_view(), name='timeset')
]
