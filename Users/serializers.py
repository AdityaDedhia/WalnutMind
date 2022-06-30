from rest_framework import serializers
from taggit.serializers import(TagListSerializerField, TaggitSerializer)

from .models import Profile

class ProfileSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    user = serializers.CharField(source='user.username') #Retrieve username from user field

    class Meta:
        model = Profile
        fields = ('user', 'avatar', 'interests', 'tags', 'blog')