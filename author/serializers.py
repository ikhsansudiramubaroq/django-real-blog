from rest_framework import serializers
from django.contrib.auth import get_user_model
from blog.models import Post, Category
from taggit.models import Tag

User = get_user_model()

class DashboardStatsSerializer(serializers.Serializer):
    total_posts = serializers.IntegerField()
    total_draft = serializers.IntegerField()
    total_published = serializers.IntegerField()


class DashboardDataSerializer(serializers.Serializer):
    stats = DashboardStatsSerializer()
    comment_count = serializers.IntegerField()
    recent_comment = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    total_views = serializers.DictField()


class PostCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['title_post', 'fill', 'images_post', 'category', 'tags']
        extra_kwargs = {
            'images_post': {'required': False}
        }

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        category_id = validated_data.pop('category_id')

        # Get the category
        category = Category.objects.get(id=category_id)

        # Create the post
        post = Post(
            **validated_data,
            category=category,
            user=self.context['request'].user  # Assign the current user
        )
        post.save()  # This will trigger the slug generation and any other save logic

        # Add tags if provided
        if tag_names:
            post.tags.set(tag_names)

        return post