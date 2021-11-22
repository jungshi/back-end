from django.db import models


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=255)
    group_id = models.CharField(max_length=255, unique=True)


class Member(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              related_name='members')
    
    def __str__(self):
        return self.name


class TimeTable(models.Model):
    date = models.CharField(max_length=20)
    start_time = models.CharField(max_length=10)
    end_time = models.CharField(max_length=10)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              related_name='timetables')


class TimeBlock(models.Model):
    order = models.IntegerField()
    avail_members = models.ManyToManyField(Member, related_name='timeblocks')
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE,
                                  related_name='timeblocks')
