from rest_framework import serializers
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Comment
from author.models import AuthorProfile
from taggit.serializers import TagListSerializerField, TaggitSerializer

User = get_user_model()

# --- SERIALIZERS FOR NESTED DATA (READ ONLY) ---

class UserMiniSerializer(serializers.ModelSerializer):
    """
    Minified User serializer for showing user info in other objects (comments, posts).
    """
    class Meta:
        model = User
        fields = ['id', 'nama', 'email', 'img_user', 'role']
        read_only_fields = fields

class CategoryMiniSerializer(serializers.ModelSerializer):
    """
    Simple category serializer.
    """
    class Meta:
        model = Category
        fields = ['id', 'title_cat', 'slug_cat']
        read_only_fields = fields

# --- MAIN SERIALIZERS ---

class AuthorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for AuthorProfile, including nested User data.
    """
    user = UserMiniSerializer(read_only=True)
    
    class Meta:
        model = AuthorProfile
        fields = ['id', 'user', 'bio', 'social_media', 'slug_author']
        read_only_fields = ['slug_author', 'user']

class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Main Post Serializer for Listing and retrieving details.
    Includes nested data for Category and User.
    """
    category = CategoryMiniSerializer(read_only=True)
    user = UserMiniSerializer(read_only=True)
    tags = TagListSerializerField()
    
    # Custom fields for counts or formatted dates could go here
    formatted_publish = serializers.DateTimeField(source='publish', format="%d %B %Y", read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'category', 'title_post', 'slug_post',
            'fill', 'images_post', 'tags', 'status', 'views',
            'publish', 'formatted_publish', 'update'
        ]
        read_only_fields = ['id', 'slug_post', 'views', 'publish', 'update', 'user']

class PostWriteSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Serializer optimized for Creating and Updating posts.
    Accepts category_id instead of nested category object.
    """
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = [
            'id', 'title_post', 'fill', 'images_post', 
            'category_id', 'tags', 'status'
        ]

    def create(self, validated_data):
        # Assign the user from context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comments.
    """
    user = UserMiniSerializer(read_only=True)
    post_slug = serializers.SlugRelatedField(
        read_only=True, slug_field='slug_post', source='post'
    )

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'post_slug', 'comments', 'timestamp', 'reply']
        read_only_fields = ['id', 'timestamp', 'user']
        extra_kwargs = {'post': {'write_only': True}}
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

# --- DASHBOARD SPECIFIC SERIALIZERS ---

class DashboardStatsSerializer(serializers.Serializer):
    total_posts = serializers.IntegerField(default=0)
    total_draft = serializers.IntegerField(default=0)
    total_published = serializers.IntegerField(default=0)

class GlobalDashboardSerializer(serializers.Serializer):
    """
    Aggregates data for the dashboard view.
    """
    stats = DashboardStatsSerializer()
    comment_count = serializers.IntegerField()
    recent_comments = CommentSerializer(many=True)
    total_views = serializers.DictField()