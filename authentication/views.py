# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .serializers import *
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.permissions import AllowAny
from authentication.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser 

class NewsletterSubscribeView(APIView):
    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Subscribed successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EditorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "editor":
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        if not user.chapter:
            return Response({"error": "Editor has no chapter assigned"}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(chapter=user.chapter)
        articles = Article.objects.filter(chapter=user.chapter)
        events = Event.objects.filter(chapter=user.chapter)

        return Response({
            "users": UserListSerializer(users, many=True).data,
            "articles": ArticleSerializer(articles, many=True).data,
            "events": EventSerializer(events, many=True).data,
        })
    



class EventRetrieveView(APIView):
    def get_object(self, pk=None, slug=None):
        if slug:
            return get_object_or_404(Event, slug=slug)
        return get_object_or_404(Event, pk=pk)

    def get(self, request, pk=None, slug=None):
        event = self.get_object(pk, slug)
        serializer = EventAllSerializer(event)
        return Response(serializer.data)

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventAllSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response({"detail": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# class EventDetailView(APIView):
#     def get(self, request, pk):
#         return Response({"message": "EventDetailView GET reached"})
    
#     def put(self, request, pk):
#         event = get_object_or_404(Event, pk=pk)
#         serializer = EventAllSerializer(event, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     def delete(self, request, pk):
#         event = get_object_or_404(Event, pk=pk)
#         event.delete()
#         return Response({"detail": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# class EventDetailBySlug(APIView):
#     def get(self, request, slug):
#         event = get_object_or_404(Event, slug=slug)
#         serializer = EventAllSerializer(event)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class EditorEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "editor" and hasattr(user, "chapter"):
            return Event.objects.filter(chapter=user.chapter)
        return Event.objects.none()
    
class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all().order_by('start_datetime')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]  

class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminArticleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class AdminArticleCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminArticleDetailView(APIView):
    print("Details view is hit")

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        print(request,"this is request")
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.delete()
        return Response({"detail": "Article deleted"}, status=status.HTTP_204_NO_CONTENT)

class ArticlePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ArticlePagination  # ✅ Add this

    def get_queryset(self):
        queryset = Article.objects.all()
        request = self.request

        search = request.query_params.get("search", "").strip()
        category = request.query_params.get("category", "").strip()
        sort_by = request.query_params.get("sort_by", "latest").strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(tags__icontains=search)
            )

        if category and category.lower() != "all categories":
            queryset = queryset.filter(category__iexact=category)

        if sort_by == "popular":
            queryset = queryset.order_by("-views")  # Ensure `views` exists
        elif sort_by == "read-time":
            queryset = queryset.order_by("read_time")  # Ensure `read_time` exists
        else:
            queryset = queryset.order_by("-created_at")

        return queryset
# class ArticleListView(generics.ListAPIView):
#     queryset = Article.objects.all().order_by('-created_at')
#     serializer_class = ArticleSerializer
#     permission_classes = [permissions.AllowAny] 

class ArticleWithRelatedView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        article_data = ArticleSerializer(article).data

        # Related articles from the same category, excluding this article
        related_qs = Article.objects.filter(
            category=article.category
        ).exclude(id=article.id)[:5]

        related_data = ArticleSerializer(related_qs, many=True).data

        return Response({
            "article": article_data,
            "related": related_data
        })

class UserSearchView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserListSerializer

    def get(self, request):
        search = request.query_params.get('search', '').strip()
        industry = request.query_params.get('industry', '').strip()
        location = request.query_params.get('location', '').strip()
        experience = request.query_params.get('experience', '').strip()
        verified = request.query_params.get('verified', '').strip().lower() == "true"

        queryset = User.objects.filter(profile__is_public=True)

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(profile__title__icontains=search) |
                Q(profile__company_name__icontains=search) |
                Q(profile__bio__icontains=search) |
                Q(profile__skills__icontains=search)  # Optional: add if skills are a string
            )

        if industry:
            queryset = queryset.filter(profile__industry__iexact=industry)

        if location:
            queryset = queryset.filter(chapter_id=location)

        if experience and experience.lower() != "all levels":
            queryset = queryset.filter(profile__experience_level__iexact=experience)

        if verified:
            queryset = queryset.filter(is_verified=True)

        queryset = queryset.distinct()

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
# class UserSearchView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserListSerializer

#     def get(self, request):
#         search = request.query_params.get('search', '').strip()
#         industry = request.query_params.get('industry', '').strip()
#         location = request.query_params.get('location', '').strip()

#         queryset = User.objects.filter(profile__is_public=True)

#         if search:
#             queryset = queryset.filter(
#                 Q(first_name__icontains=search) |
#                 Q(last_name__icontains=search) |
#                 Q(profile__title__icontains=search) |
#                 Q(profile__company_name__icontains=search) |
#                 Q(profile__bio__icontains=search)
#             )

#         if industry:
#             queryset = queryset.filter(profile__industry__iexact=industry)

#         if location:
#             queryset = queryset.filter(chapter_id=location)

#         queryset = queryset.distinct()

#         serializer = UserListSerializer(queryset, many=True)
#         return Response(serializer.data)
    
    
class ChapterListView(generics.ListAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [AllowAny]  # Or customize for auth


class SignupView(APIView):
    parser_classes = [MultiPartParser, FormParser,JSONParser ]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # 🔐 Generate access & refresh tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            login(request, user)  # optional

            return Response({
                "message": "Login successful",
                "access": access_token,
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_superuser": user.role == "admin" or user.role == "editor",
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EditorArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Only allow editors to access their chapter's articles
        if user.role == "editor" and hasattr(user, "chapter"):
            return Article.objects.filter(chapter=user.chapter)
        return Article.objects.none()  # deny others or unauthenticated access
    
class AllUsersPagination(PageNumberPagination):
    page_size = 10  # default
    page_size_query_param = 'page_size'
    max_page_size = 100

class AllUsersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        search = request.query_params.get("search", "").strip()
        users = User.objects.all().order_by("-created_at")

        if search:
            search_terms = search.split()
            query = Q()
            for term in search_terms:
                query |= Q(first_name__icontains=term)
                query |= Q(last_name__icontains=term)
                query |= Q(email__icontains=term)
            users = users.filter(query)
            
        paginator = AllUsersPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserListSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)
# class AllUsersView(APIView):
#     permission_classes = [AllowAny]  # Public access

#     def get(self, request):
#         users = User.objects.all()
#         serializer = UserListSerializer(users, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class UpdateUserView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.chapter_id = request.data.get("chapter", user.chapter_id)
        user.role=request.data.get("role", user.role)
        if(user.role == "admin" or user.role == "editor"):
            print("user  is a suepr user")
            user.is_superuser = True
            user.is_staff=True
        else:
            print("user  is not  a suepr user")

            user.is_superuser = False
            user.is_staff=False
        user.save()

        # Update profile
        profile_data = {
            "title": request.data.get("title"),
            "company_name": request.data.get("company_name"),
            "bio": request.data.get("bio"),
            "industry": request.data.get("industry"),
            "location": request.data.get("location"),
            "skills": request.data.get("skills"),
            "profile_image": request.data.get("profile_image"),
            "is_public": request.data.get("is_public"),
            "status": request.data.get("status"),
        }

        profile = getattr(user, "profile", None)
        if profile:
            for key, value in profile_data.items():
                if value is not None:
                    setattr(profile, key, value)
            profile.save()

        return Response({"message": "User updated successfully."}, status=200)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        def to_list(value):
            """
            Returns a list:
            - if already a list, return as-is
            - if dict w/ numeric keys, return values sorted by key
            - if JSON string, parse (if list)
            - else []
            """
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                # numeric-key dict or normal dict of objects
                try:
                    keys = sorted(value.keys(), key=lambda k: int(k)) if all(k.isdigit() for k in value.keys()) else value.keys()
                    return [value[k] for k in keys]
                except Exception:
                    return list(value.values())
            if isinstance(value, str):
                import json
                try:
                    parsed = json.loads(value)
                    return parsed if isinstance(parsed, list) else []
                except Exception:
                    return []
            return []
        def profile_image_url(p):
            if p and p.profile_image:
                try:
                    return request.build_absolute_uri(p.profile_image.url)
                except Exception:
                    # Fallback: string path
                    return str(p.profile_image)
            return None
        user = request.user
        try:
            field = Profile.objects.get(user=user)
            print(field.profile_image,"this is profile image")
        except Profile.DoesNotExist:
            field = None

        data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "profile": {
                "title": field.title if field else "",
                "company_name": field.company_name if field else "",
                "bio": field.bio if field else "",
                "industry": field.industry if field else "",
                "location": field.location if field else "",
                "skills": field.skills if field else [],
                "status": field.status if field else "",
                "is_public": field.is_public if field else True,
                "chapter": user.chapter_id if user and user.chapter_id else None,
                "profile_image": profile_image_url(field),
                "faqs": to_list(field.faqs) if field else [],
                "certifications": to_list(field.certifications) if field else [],
                "experience": field.experience if field else "",
                "created_at":field.created_at if field else ""
            }
        }
        return Response(data)

# class CurrentUserView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         user = request.user
#         try:
#             field = Profile.objects.get(user=user)
#         except Profile.DoesNotExist:
#             field = None
#         print(user.chapter,"this is user")
#         data = {
#             "id": user.id,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#             "role": user.role,
#             "is_verified": user.is_verified,
#             "profile": {
#                 "title": field.title if field else "",
#                 "company_name": field.company_name if field else "",
#                 "bio": field.bio if field else "",
#                 "industry": field.industry if field else "",
#                 "location": field.location if field else "",
#                 "skills": field.skills if field else [],
#                 "status": field.status if field else "",
#                 "profile_image": field.profile_image if field and field.profile_image else "",
#                 "is_public": field.is_public if field else True,
#                 "chapter": user.chapter_id if user and user.chapter_id else None,
#                 "profile_image":user.profile_image,
#             }
#         }
#         return Response(data)
    
import json

class CurrentUserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        # Update basic user fields
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.save()

        # Profile updates
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.title = request.data.get("title", profile.title)
        profile.company_name = request.data.get("company_name", profile.company_name)
        profile.bio = request.data.get("bio", profile.bio)
        profile.industry = request.data.get("industry", profile.industry)
        profile.location = request.data.get("location", profile.location)
        profile.experience = request.data.get("experience", profile.experience)

        # Handle profile_image
        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        # Parse JSON fields
        try:
            profile.skills = json.loads(request.data.get("skills", "[]"))
        except json.JSONDecodeError:
            profile.skills = []

        try:
            profile.faqs = json.loads(request.data.get("faqs", "[]"))
        except json.JSONDecodeError:
            profile.faqs = []

        try:
            profile.certifications = json.loads(request.data.get("certifications", "[]"))
        except json.JSONDecodeError:
            profile.certifications = []

        profile.save()

        serializer = CurrentUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class CurrentUserUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request):
#         user = request.user
#         data = request.data

#         # Update User fields
#         user.first_name = data.get("first_name", user.first_name)
#         user.last_name = data.get("last_name", user.last_name)
#         user.email = data.get("email", user.email)
#         user.save()

#         # Update Profile fields
#         profile_data = data.get("profile", {})
#         profile, _ = Profile.objects.get_or_create(user=user)

#         profile.bio = profile_data.get("bio", profile.bio)
#         profile.location = profile_data.get("location", profile.location)
#         profile.title = profile_data.get("title", profile.title)  # if field exists
#         profile.company_name = profile_data.get("company_name", profile.company_name)
#         profile.experience = profile_data.get("experience", profile.experience)
#         profile.industry = profile_data.get("industry", profile.industry)

#         # Update FAQs (overwrite)
#         faqs = profile_data.get("faqs")
#         if isinstance(faqs, list):
#             profile.faqs = faqs  # assumed to be stored as JSONField or TextField with serialization

#         # Update Certifications (overwrite)
#         certifications = profile_data.get("certifications")
#         if isinstance(certifications, list):
#             profile.certifications = certifications  # also assumed to be JSONField or similar

#         profile.save()

#         serializer = CurrentUserSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
