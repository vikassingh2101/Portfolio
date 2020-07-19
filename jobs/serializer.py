from rest_framework import serializers
from .models import Job
import datetime

class JobSerializer(serializers.ModelSerializer):
    summary = serializers.CharField(min_length=2,max_length=Job._meta.get_field('summary').max_length)
    id = serializers.IntegerField(required=False, min_value=1)
    image = serializers.ImageField(default = None)

    class Meta:
        model = Job
        fields = ('id','image','summary',)
