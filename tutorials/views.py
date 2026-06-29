from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from tutorials.models import Course, Section, Lesson, Quiz, QuizAttempt, CourseRating, LessonRating, Banner, LessonProgress, UserBadge, Badge
from tutorials.serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    SectionSerializer,
    LessonListSerializer,
    LessonDetailSerializer,
    QuizSerializer,
    QuizAttemptSubmissionSerializer,
    QuizAttemptResponseSerializer,
    LeaderboardSerializer,
    RatingSubmitSerializer,
    CourseRatingResponseSerializer,
    LessonRatingResponseSerializer,
    BannerSerializer,
    BadgeSerializer,
)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    @action(detail=True, methods=['get'])
    def sections(self, request, slug=None):
        course = self.get_object()
        sections = course.sections.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post', 'put', 'patch', 'delete'], permission_classes=[IsAuthenticated])
    def rate(self, request, slug=None):
        course = self.get_object()
        
        # GET: Retrieve the logged-in user's rating for the course
        if request.method == 'GET':
            try:
                rating_obj = CourseRating.objects.get(course=course, user=request.user)
                response_serializer = CourseRatingResponseSerializer(rating_obj)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except CourseRating.DoesNotExist:
                return Response({"detail": "You have not rated this course yet."}, status=status.HTTP_404_NOT_FOUND)

        # POST: Submit a new rating
        elif request.method == 'POST':
            if CourseRating.objects.filter(course=course, user=request.user).exists():
                return Response({"detail": "You have already rated this course. Use PUT or PATCH to edit it."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = RatingSubmitSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            rating_val = serializer.validated_data['rating']
            review_val = serializer.validated_data.get('review', '')
            
            rating_obj = CourseRating.objects.create(
                course=course,
                user=request.user,
                rating=rating_val,
                review=review_val
            )
            
            response_serializer = CourseRatingResponseSerializer(rating_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # PUT/PATCH: Edit the existing rating
        elif request.method in ['PUT', 'PATCH']:
            try:
                rating_obj = CourseRating.objects.get(course=course, user=request.user)
            except CourseRating.DoesNotExist:
                return Response({"detail": "You have not rated this course yet. Use POST to create a rating."}, status=status.HTTP_404_NOT_FOUND)

            partial = (request.method == 'PATCH')
            serializer = RatingSubmitSerializer(rating_obj, data=request.data, partial=partial)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if 'rating' in serializer.validated_data:
                rating_obj.rating = serializer.validated_data['rating']
            if 'review' in serializer.validated_data:
                rating_obj.review = serializer.validated_data['review']
            rating_obj.save()

            response_serializer = CourseRatingResponseSerializer(rating_obj)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        # DELETE: Delete the existing rating
        elif request.method == 'DELETE':
            try:
                rating_obj = CourseRating.objects.get(course=course, user=request.user)
                rating_obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except CourseRating.DoesNotExist:
                return Response({"detail": "You have not rated this course yet."}, status=status.HTTP_404_NOT_FOUND)


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    lookup_field = 'slug'
    serializer_class = SectionSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def lessons(self, request, slug=None):
        section = self.get_object()
        lessons = section.lessons.all()
        serializer = LessonListSerializer(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def quiz(self, request, slug=None):
        lesson = self.get_object()
        try:
            quiz = lesson.quiz
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found for this lesson."}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post', 'put', 'patch', 'delete'], permission_classes=[IsAuthenticated])
    def rate(self, request, slug=None):
        lesson = self.get_object()
        
        # GET: Retrieve the logged-in user's rating for the lesson
        if request.method == 'GET':
            try:
                rating_obj = LessonRating.objects.get(lesson=lesson, user=request.user)
                response_serializer = LessonRatingResponseSerializer(rating_obj)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except LessonRating.DoesNotExist:
                return Response({"detail": "You have not rated this lesson yet."}, status=status.HTTP_404_NOT_FOUND)

        # POST: Submit a new rating
        elif request.method == 'POST':
            if LessonRating.objects.filter(lesson=lesson, user=request.user).exists():
                return Response({"detail": "You have already rated this lesson. Use PUT or PATCH to edit it."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = RatingSubmitSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            rating_val = serializer.validated_data['rating']
            review_val = serializer.validated_data.get('review', '')
            
            rating_obj = LessonRating.objects.create(
                lesson=lesson,
                user=request.user,
                rating=rating_val,
                review=review_val
            )
            
            response_serializer = LessonRatingResponseSerializer(rating_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # PUT/PATCH: Edit the existing rating
        elif request.method in ['PUT', 'PATCH']:
            try:
                rating_obj = LessonRating.objects.get(lesson=lesson, user=request.user)
            except LessonRating.DoesNotExist:
                return Response({"detail": "You have not rated this lesson yet. Use POST to create a rating."}, status=status.HTTP_404_NOT_FOUND)

            partial = (request.method == 'PATCH')
            serializer = RatingSubmitSerializer(rating_obj, data=request.data, partial=partial)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if 'rating' in serializer.validated_data:
                rating_obj.rating = serializer.validated_data['rating']
            if 'review' in serializer.validated_data:
                rating_obj.review = serializer.validated_data['review']
            rating_obj.save()

            response_serializer = LessonRatingResponseSerializer(rating_obj)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        # DELETE: Delete the existing rating
        elif request.method == 'DELETE':
            try:
                rating_obj = LessonRating.objects.get(lesson=lesson, user=request.user)
                rating_obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except LessonRating.DoesNotExist:
                return Response({"detail": "You have not rated this lesson yet."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, slug=None):
        lesson = self.get_object()
        user = request.user
        
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )
        
        xp_gained = 0
        if not created and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            created = True

        if created:
            xp_gained = 100
            user.xp += xp_gained
            user.save(update_fields=['xp'])

        # Check course completion
        course = lesson.section.course
        total_lessons_count = Lesson.objects.filter(section__course=course).count()
        completed_lessons_count = LessonProgress.objects.filter(
            user=user,
            lesson__section__course=course,
            is_completed=True
        ).count()

        course_completed = (completed_lessons_count == total_lessons_count)
        badge_earned_data = None

        if course_completed:
            badge = getattr(course, 'badge', None)
            if badge:
                user_badge, badge_created = UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge
                )
                if badge_created:
                    badge_earned_data = {
                        "name": badge.name,
                        "description": badge.description,
                        "image": request.build_absolute_uri(badge.image.url) if badge.image else None
                    }

        return Response({
            "detail": "Lesson marked as completed successfully.",
            "xp_gained": xp_gained,
            "total_xp": user.xp,
            "course_completed": course_completed,
            "badge_earned": badge_earned_data
        }, status=status.HTTP_200_OK)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def attempt(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizAttemptSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        submitted_answers = serializer.validated_data['answers']
        total_questions = quiz.questions.count()

        if total_questions == 0:
            return Response({"detail": "This quiz does not contain questions."}, status=status.HTTP_400_BAD_REQUEST)

        questions = quiz.questions.all()
        correct_choices = {q.id: q.choices.filter(is_correct=True).values_list('id', flat=True) for q in questions}

        correct_answers_count = 0
        graded_feedback = []

        for ans in submitted_answers:
            q_id = ans['question_id']
            c_id = ans['choice_id']

            if not questions.filter(id=q_id).exists():
                return Response({"detail": f"Question {q_id} does not belong to this quiz."}, status=status.HTTP_400_BAD_REQUEST)

            q_obj = questions.get(id=q_id)
            if not q_obj.choices.filter(id=c_id).exists():
                return Response({"detail": f"Choice {c_id} does not belong to Question {q_id}."}, status=status.HTTP_400_BAD_REQUEST)

            is_correct = c_id in correct_choices.get(q_id, [])
            if is_correct:
                correct_answers_count += 1

            graded_feedback.append({
                "question_id": q_id,
                "submitted_choice_id": c_id,
                "is_correct": is_correct
            })

        score = int((correct_answers_count / total_questions) * 100)

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score
        )

        response_data = QuizAttemptResponseSerializer(attempt).data
        response_data['answers_feedback'] = graded_feedback
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def leaderboard(self, request, pk=None):
        quiz = self.get_object()

        # Query all unique users who attempted this quiz
        user_ids = QuizAttempt.objects.filter(quiz=quiz).values_list('user_id', flat=True).distinct()

        # Find the earliest attempt ID for each user
        first_attempt_ids = []
        for u_id in user_ids:
            first_attempt = QuizAttempt.objects.filter(quiz=quiz, user_id=u_id).order_by('completed_at', 'id').first()
            if first_attempt:
                first_attempt_ids.append(first_attempt.id)

        # Retrieve first attempts ranked by score descending and completed_at ascending
        attempts = QuizAttempt.objects.filter(id__in=first_attempt_ids).select_related('user').order_by('-score', 'completed_at', 'id')

        leaderboard_data = []
        for index, attempt in enumerate(attempts):
            data = {
                "rank": index + 1,
                "score": attempt.score,
                "completed_at": attempt.completed_at,
                "user": {
                    "id": attempt.user.id,
                    "email": attempt.user.email,
                    "full_name": attempt.user.full_name
                }
            }
            leaderboard_data.append(data)

        serializer = LeaderboardSerializer(leaderboard_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    permission_classes = [AllowAny]


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        badges = self.get_queryset()
        
        # Map user's earned badges for quick lookup
        earned_user_badges = {ub.badge_id: ub.earned_at for ub in user.earned_badges.all()}
        
        badge_list = []
        for badge in badges:
            is_earned = badge.id in earned_user_badges
            earned_at = earned_user_badges.get(badge.id) if is_earned else None
            
            badge_list.append({
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "image": request.build_absolute_uri(badge.image.url) if badge.image else None,
                "is_earned": is_earned,
                "earned_at": earned_at
            })
            
        return Response({
            "xp": user.xp,
            "level": (user.xp // 1000) + 1,
            "badges": badge_list
        }, status=status.HTTP_200_OK)
