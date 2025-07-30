from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.utils.text import slugify

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'email', 'subscribed_at']
        
class EventAllSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Event
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["id", "created_by", "updated_at"]

class ProfileSerializer(serializers.ModelSerializer):
    chapter = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "title", "company_name", "bio", "industry", "location",
            "skills", "profile_image", "is_public", "status", "chapter"
        ]

class UserPublicSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'chapter', 'profile']

# serializers.py



class ArticleSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all()) 

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'content_body', 'video_url',
            'tags', 'category', 'author', 'created_at', 'chapter'  
        ]

class RegisterSerializer(serializers.ModelSerializer):

    title = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    bio = serializers.CharField(write_only=True)
    industry = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True)
    skills = serializers.JSONField(write_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    is_public = serializers.BooleanField(default=True)
    status = serializers.ChoiceField(choices=Profile.STATUS_CHOICES)
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), required=False)
    password2 = serializers.CharField(write_only=True)
    experience = serializers.CharField(write_only=True, required=False)
    certifications = serializers.JSONField(write_only=True, required=False)
    faqs = serializers.JSONField(write_only=True, required=False)
    website = serializers.URLField(required=False, allow_null=True)
    linkedin = serializers.URLField(required=False, allow_null=True)
    twitter = serializers.URLField(required=False, allow_null=True)
    contact = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    whatsapp = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "password", "password2","skills", 
            "title", "company_name", "bio", "industry", "location","profile_image",
             "is_public", "status", "chapter", 'role', 'is_superuser', 'is_staff','experience',
            'contact','twitter','linkedin','website','certifications','faqs','whatsapp'
        ]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_status(self, value):
        return value.upper()

    def create(self, validated_data):
        certifications = validated_data.pop("certifications", {})
        faqs = validated_data.pop("faqs", {})

        profile_data = {
            key: validated_data.pop(key,None)
            for key in [
                "title", "company_name", "bio", "industry", "location",
                "skills", "profile_image", "is_public", "status","experience",
                "website", "linkedin", "twitter", "contact","whatsapp"
            ]
        }
        validated_data.pop("password2")
        raw_password = validated_data.pop("password")

        user = User.objects.create(
            **validated_data,
            password=make_password(raw_password),
            is_verified=False,
            # role='member'
        )
        base_slug = slugify(profile_data["title"])
        slug = base_slug
        counter = 1
        while Profile.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        profile_data["user"] = user
        profile_data["slug"] = slug
        profile=Profile.objects.create(**profile_data)

        profile.certifications = certifications
        profile.faqs = faqs
        profile.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_verified:
            raise serializers.ValidationError("Account is not verified.")
        data["user"] = user
        return data

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'name', 'slug']

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user']  

class UserListSerializer(serializers.ModelSerializer):
    profile = FieldSerializer(read_only=True)  
    chapter = ChapterSerializer(read_only=True)  

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'is_superuser', 'created_at', 'profile', 'chapter'
        ]
        


class CurrentUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "email", "role",
            "is_verified", "profile"
        ]

    def get_profile(self, user):
        try:
            field = Profile.objects.get(user=user)
            return ProfileSerializer(field).data
        except Profile.DoesNotExist:
            return None

# class UserMiniSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'last_name', 'email']    
            
# class ChapterSerializer(serializers.ModelSerializer):
#     editor = UserMiniSerializer(read_only=True)

#     class Meta:
#         model = Chapter
#         fields = ['id', 'name']


class ChapterContentSerializer(serializers.Serializer):
    users = UserListSerializer(many=True, read_only=True)
    articles = ArticleSerializer(many=True, read_only=True)
    events = EventSerializer(many=True, read_only=True)
