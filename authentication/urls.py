# urls.py
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path("user/all/", AllUsersView.as_view(), name="all-users"),
    path("user/delete/<uuid:user_id>/", DeleteUserView.as_view(), name="delete-user"),
    path('user/update/<uuid:id>/', UpdateUserView.as_view()),
    path('user/me/', CurrentUserView.as_view(), name='current-user'),
    path('user/update/me/', CurrentUserUpdateView.as_view(), name='user-update-me'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('chapters/', ChapterListView.as_view(), name='chapter-list'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', ArticleWithRelatedView.as_view(), name='article-detail'),
    path('create/articles/', AdminArticleCreateView.as_view()),
    path('update/articles/<uuid:pk>/', AdminArticleDetailView.as_view()),
    path('events/create/', CreateEventView.as_view(), name='create-event'),
    path('events/', EventListAPIView.as_view(), name='event-list'),
    # path('events/<uuid:pk>/', EventDetailView.as_view(), name='event-detail'),
    # path('events/<slug:slug>/', EventDetailBySlug.as_view(), name='event-detail-by-slug'),
    path('articles/admin/<uuid:pk>/', AdminArticleView.as_view()),
    path('events/<uuid:pk>/', EventRetrieveView.as_view(), name='event-detail-pk'),
    path('events/slug/<slug:slug>/', EventRetrieveView.as_view(), name='event-detail-slug'),
    path('editor-dashboard/', EditorDashboardView.as_view(), name='editor-dashboard'),
    path('subscribe/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('editor/articles/', EditorArticleListView.as_view(), name='editor-articles'),
    path('editor/events/', EditorEventListView.as_view(), name='editor-events'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
