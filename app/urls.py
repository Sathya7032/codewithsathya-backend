from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerViewSet, basename='answer')
router.register(r'technologies', TechnologyViewSet)
router.register(r'tutorials', TutorialViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'blogs', BlogPostViewSet)
router.register(r'snippets', CodeSnippetViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/user/register/', UserCreate.as_view(), name='user_create'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('callback/', google_login_callback, name='callback'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('api/google/validate_token/', validate_google_token, name='validate_token'),
    path('tags/', TagListAPIView.as_view(), name='tag-list'),
    path('tags/<slug:tag_slug>/<str:model_name>/', TaggedItemsAPIView.as_view(), name='tagged-items'),
   
]
