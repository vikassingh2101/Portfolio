from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from django.core.cache import cache

from .serializer import JobSerializer
from .models import Job

class JobPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100            #Maximum size of page that can be set by an API client.


class JobList(ListAPIView):
    '''The ListAPIView handling the response.'''
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('id',)
    search_fields = ('summary',)
    pagination_class = JobPagination

    def get_queryset(self):
        id = self.request.query_params.get('id',None)
        if id is None:
            return super().get_queryset()
        id = int(id)
        queryset = Job.objects.all()
        return queryset.filter(id=id)


class JobCreate(CreateAPIView):
    serializer_class = JobSerializer

    def create(self, request, *args, **kwargs):
        imagePath = request.data.get('image')
        summary = request.data.get('summary')
        if imagePath is None or summary is None:
            raise ValidationError({'Image/Summary' : 'Cannot be Empty'})
        if len(summary) > Job._meta.get_field('summary').max_length:
            raise ValidationError({'Summary' : 'Length cannot exceed 200 characters'})
        return super().create(request, *args, **kwargs)


class JobRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    lookup_field = 'id'
    serializer_class = JobSerializer

    def delete(self, request, *args, **kwargs):
        job_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            cache.delete('Job_data_{}'.format(job_id))
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            job = response.data
            cache.set('Job_data_{}'.format(job['id']) ,
            {
            'image' : job['image'],
            'summary' : job['summary'],
            })
        return response
