from rest_framework import serializers
from taggit.serializers import(TagListSerializerField, TaggitSerializer)

from .models import Post

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = Post
        fields = ('id', 'slug', 'title', 'cover', 'abstract', 'tags')