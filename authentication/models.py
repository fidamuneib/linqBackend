import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.utils.text import slugify


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)
    
class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  # <== slug field
    content_body = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    author = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='articles')
    chapter = models.ForeignKey('authentication.Chapter', on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    
class Chapter(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.CharField( primary_key=True, max_length=36, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.id})"
    
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='created_events')
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title
    
class Profile(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('PENDING', 'Pending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE, related_name='profile')
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    bio = models.TextField()
    industry = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    skills = models.JSONField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True,null=True, max_length=120)
    certifications = models.JSONField(default=dict, blank=True, null=True)
    faqs = models.JSONField(default=dict, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return f"{self.title} ({self.user.email})"


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager() 
    ROLE_CHOICES = [
        ('admin', 'admin'),
        ('member', 'member'),
        ('moderator', 'moderator'),
        ('editor', 'editor'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    chapter = models.ForeignKey('Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    def __str__(self):
        return self.email
