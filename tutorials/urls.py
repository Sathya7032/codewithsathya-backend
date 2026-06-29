from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tutorials.views import CourseViewSet, SectionViewSet, LessonViewSet, QuizViewSet, BannerViewSet, BadgeViewSet

app_name = 'tutorials'

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course')
router.register('sections', SectionViewSet, basename='section')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('quizzes', QuizViewSet, basename='quiz')
router.register('banners', BannerViewSet, basename='banner')
router.register('badges', BadgeViewSet, basename='badge')

urlpatterns = [
    path('', include(router.urls)),
]
