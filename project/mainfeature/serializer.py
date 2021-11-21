from rest_framework import serializers
from .models import TimeTable

class testserializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTable
        fields = ('start_time', 'end_time', 'date')