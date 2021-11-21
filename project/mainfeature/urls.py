from django.urls import path

from .views import GroupAPIView

urlpatterns = [
    path('group/', GroupAPIView.as_view(), name='group')
]
