from django.shortcuts import render
from .models import Technology, Topic, Question
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from rest_framework import viewsets
from .models import *
from .serializers import  *
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from taggit.models import Tag
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, filters

User = get_user_model()


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserDashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        #prepare user data
        user_data = {
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
            'is_active': user.is_active
        }

        return Response(user_data)
    

class GoogleLogin(SocialLoginView): # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"
    client_class = OAuth2Client

@login_required
def google_login_callback(request):
    user = request.user

    social_accounts = SocialAccount.objects.filter(user=user)
    print("Social Account for user:", social_accounts)

    social_account = social_accounts.first()

    if not social_account:
        print("No social account for user:", user)
        return redirect('http://localhost:3000/login/callback/?error=NoSocialAccount')
    
    token = SocialToken.objects.filter(account=social_account, account__provider='google').first()

    if token:
        print('Google token found:', token.token)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:3000/login/callback/?access_token={access_token}')
    else:
        print('No Google token found for user', user)
        return redirect(f'http://localhost:3000/login/callback/?error=NoGoogleToken')


GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

@csrf_exempt
def validate_google_token(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed.'}, status=405)

    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')

        if not access_token:
            return JsonResponse({'detail': 'Access Token is missing.'}, status=400)

        # Step 1: Get user info from Google
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        
        if response.status_code != 200:
            return JsonResponse({'detail': 'Invalid Google token.'}, status=401)

        user_info = response.json()
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')

        if not email:
            return JsonResponse({'detail': 'Unable to fetch user email from Google.'}, status=400)

        # Step 2: Get or create user in your DB
        user, _ = User.objects.get_or_create(email=email, defaults={
            'username': email,
            'first_name': first_name,
            'last_name': last_name,
        })

        # Step 3: Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return JsonResponse({
            'access': access,
            'refresh': str(refresh),
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)



class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.filter()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class TagListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

class TaggedItemsAPIView(generics.ListAPIView):
    serializer_class = None  # Will be set dynamically
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        model_name = self.kwargs['model_name']
        
        models = {
            'technology': Technology,
            'tutorial': Tutorial,
            'blog': BlogPost,
            'snippet': CodeSnippet,
        }
        
        if model_name not in models:
            return []
            
        model = models[model_name]
        return model.objects.filter(tags__slug=tag_slug)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        model_name = self.kwargs['model_name']
        serializers = {
            'technology': TechnologySerializer,
            'tutorial': TutorialSerializer,
            'blog': BlogPostSerializer,
            'snippet': CodeSnippetSerializer,
        
        }
        
        serializer_class = serializers.get(model_name)
        if not serializer_class:
            return Response([])
            
        serializer = serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    

class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.filter(is_active=True)
    serializer_class = TechnologySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Use minimal serializers here
        data['tutorials'] = MinimalTutorialSerializer(instance.tutorials.all(), many=True, context={'request': request}).data
        data['blog_posts'] = MinimalBlogPostSerializer(instance.blog_posts.all(), many=True, context={'request': request}).data
        data['code_snippets'] = MinimalCodeSnippetSerializer(instance.code_snippets.all(), many=True, context={'request': request}).data

        return Response(data)

class TutorialViewSet(viewsets.ModelViewSet):
    queryset = Tutorial.objects.filter(is_published=True)
    serializer_class = TutorialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['technology', 'difficulty', 'is_published']
    ordering_fields = ['published_date', 'views']
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Include topics
        data = serializer.data
        data['topics'] = TopicSerializer(instance.topics.all(), many=True, context={'request': request}).data
        
        return Response(data)

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['tutorial', 'is_free']
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Use minimal serializers here
        data['questions'] = QuestionSerializer(instance.questions.all(), many=True, context={'request': request}).data

        return Response(data)

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.filter(is_published=True)
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content']
    filterset_fields = ['technology', 'is_published']
    ordering_fields = ['published_date']
    lookup_field = 'slug'

class CodeSnippetViewSet(viewsets.ModelViewSet):
    queryset = CodeSnippet.objects.filter(is_public=True)
    serializer_class = CodeSnippetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'code']
    filterset_fields = ['technology', 'language', 'is_public']
    ordering_fields = ['created_at']
    lookup_field = 'slug'
