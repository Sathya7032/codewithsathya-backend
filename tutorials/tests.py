from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tutorials.models import (
    Course,
    Section,
    Lesson,
    CourseRating,
    LessonRating,
    LessonAttachment,
    Quiz,
    Question,
    Choice,
    QuizAttempt,
    Banner,
    LessonProgress,
    Badge,
    UserBadge,
)

User = get_user_model()

class TutorialModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1@example.com',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2@example.com',
            email='user2@example.com',
            password='password123'
        )

    def test_course_creation_and_auto_slug(self):
        course1 = Course.objects.create(
            title='Django Advanced Development',
            description='Learn advanced Django patterns',
            level='pro',
            course_time=240
        )
        self.assertEqual(course1.slug, 'django-advanced-development')

    def test_section_and_lesson_auto_slug(self):
        course = Course.objects.create(
            title='Vue.js Basics',
            description='Learn Vue.js',
            level='beginner',
            course_time=60
        )
        section = Section.objects.create(
            course=course,
            title='Vue.js Directives',
            order=1
        )
        lesson = Lesson.objects.create(
            section=section,
            title='v-bind Directive',
            description='Learn v-bind',
            time=10,
            author=self.user1,
            order=1
        )

        self.assertEqual(section.slug, 'vuejs-directives')
        self.assertEqual(lesson.slug, 'v-bind-directive')

    def test_lesson_video_url_field(self):
        course = Course.objects.create(
            title='Vue.js Basics',
            description='Learn Vue.js',
            level='beginner',
            course_time=60
        )
        section = Section.objects.create(
            course=course,
            title='Vue.js Directives',
            order=1
        )
        lesson = Lesson.objects.create(
            section=section,
            title='v-bind Directive',
            description='Learn v-bind',
            time=10,
            author=self.user1,
            order=1,
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )
        self.assertEqual(lesson.video_url, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    def test_relationships_course_section_lesson(self):
        course = Course.objects.create(
            title='React Native Basics',
            description='Learn React Native',
            level='beginner',
            course_time=180
        )
        section = Section.objects.create(
            course=course,
            title='Introduction',
            order=1
        )
        lesson = Lesson.objects.create(
            section=section,
            title='Getting Started',
            description='Setup developer environment',
            time=15,
            author=self.user1,
            order=1
        )

        self.assertEqual(section.course, course)
        self.assertEqual(lesson.section, section)
        self.assertEqual(lesson.author, self.user1)
        self.assertEqual(course.sections.count(), 1)
        self.assertEqual(section.lessons.count(), 1)

    def test_course_average_rating(self):
        course = Course.objects.create(
            title='Python Fundamentals',
            description='Learn python core concepts',
            level='beginner',
            course_time=90
        )

        # Average is 0.0 initially
        self.assertEqual(course.average_rating(), 0.0)

        # Add ratings
        CourseRating.objects.create(course=course, user=self.user1, rating=5, review='Excellent!')
        CourseRating.objects.create(course=course, user=self.user2, rating=4, review='Very Good!')

        self.assertEqual(course.average_rating(), 4.5)

        # Check unique constraint
        with self.assertRaises(IntegrityError):
            CourseRating.objects.create(course=course, user=self.user1, rating=3)

    def test_lesson_average_rating(self):
        course = Course.objects.create(
            title='HTML and CSS',
            description='Learn web styling',
            level='beginner',
            course_time=100
        )
        section = Section.objects.create(course=course, title='HTML Core')
        lesson = Lesson.objects.create(
            section=section,
            title='Tags and Elements',
            description='All about tags',
            time=20,
            author=self.user1
        )

        # Average is 0.0 initially
        self.assertEqual(lesson.average_rating(), 0.0)

        # Add ratings
        LessonRating.objects.create(lesson=lesson, user=self.user1, rating=4)
        LessonRating.objects.create(lesson=lesson, user=self.user2, rating=2)

        self.assertEqual(lesson.average_rating(), 3.0)

        # Check unique constraint
        with self.assertRaises(IntegrityError):
            LessonRating.objects.create(lesson=lesson, user=self.user1, rating=5)

    def test_course_enrollment(self):
        course = Course.objects.create(
            title='Docker for Beginners',
            description='Learn containerization',
            level='beginner',
            course_time=60
        )
        
        # Initially empty
        self.assertEqual(course.enrolled_users.count(), 0)

        # Enroll user1
        course.enrolled_users.add(self.user1)
        self.assertEqual(course.enrolled_users.count(), 1)
        self.assertIn(self.user1, course.enrolled_users.all())
        
        # Verify backward relation
        self.assertIn(course, self.user1.enrolled_courses.all())

    def test_lesson_views(self):
        course = Course.objects.create(
            title='Git Fundamentals',
            description='Learn version control',
            level='beginner',
            course_time=50
        )
        section = Section.objects.create(course=course, title='Git basics')
        lesson = Lesson.objects.create(
            section=section,
            title='Commits and Branches',
            description='Understanding commits',
            time=15,
            author=self.user1
        )

        # Views start at 0
        self.assertEqual(lesson.views, 0)

        # Increment views
        lesson.views += 1
        lesson.save()
        self.assertEqual(lesson.views, 1)

    def test_lesson_attachments(self):
        course = Course.objects.create(
            title='SQL Core',
            description='Learn SQL databases',
            level='beginner',
            course_time=120
        )
        section = Section.objects.create(course=course, title='SQL Core Basics')
        lesson = Lesson.objects.create(
            section=section,
            title='SELECT Queries',
            description='Query database tables',
            time=30,
            author=self.user1
        )

        # Creating dummy files for attachments
        file1 = SimpleUploadedFile("slides.pdf", b"pdf content", content_type="application/pdf")
        file2 = SimpleUploadedFile("code.sql", b"SELECT * FROM users;", content_type="text/plain")

        # Create attachments
        attachment1 = LessonAttachment.objects.create(lesson=lesson, file=file1)
        attachment2 = LessonAttachment.objects.create(lesson=lesson, file=file2)

        # Verify attachments are added
        self.assertEqual(lesson.attachments.count(), 2)
        self.assertEqual(attachment1.name, "slides.pdf")
        self.assertEqual(attachment2.name, "code.sql")
        self.assertIn(attachment1, lesson.attachments.all())
        self.assertIn(attachment2, lesson.attachments.all())

    def test_quiz_and_attempts(self):
        course = Course.objects.create(
            title='Vue.js Fundamentals',
            description='Learn Vue framework',
            level='beginner',
            course_time=90
        )
        section = Section.objects.create(course=course, title='Vue Basics')
        lesson = Lesson.objects.create(
            section=section,
            title='Vue Instance',
            description='Understanding Vue reactivity',
            time=20,
            author=self.user1
        )

        # Create Quiz
        quiz = Quiz.objects.create(
            lesson=lesson,
            title='Vue reactivity quiz',
            passing_score=75
        )

        # Create MCQ Question
        question = Question.objects.create(
            quiz=quiz,
            text='Which option creates a reactive reference in Vue 3?',
            order=1
        )

        # Create Choices
        choice1 = Choice.objects.create(question=question, text='ref()', is_correct=True)
        choice2 = Choice.objects.create(question=question, text='createRef()', is_correct=False)
        choice3 = Choice.objects.create(question=question, text='reactiveRef()', is_correct=False)

        self.assertEqual(lesson.quiz, quiz)
        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(question.choices.count(), 3)
        self.assertEqual(choice1.question, question)

        # Record a passing attempt
        attempt_passed = QuizAttempt.objects.create(
            user=self.user1,
            quiz=quiz,
            score=80  # 80 >= 75 passing_score
        )
        self.assertTrue(attempt_passed.is_passed)


class TutorialAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='author@example.com',
            email='author@example.com',
            password='password123',
            full_name='Author User'
        )
        self.user2 = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='password123',
            full_name='Student User'
        )
        self.course = Course.objects.create(
            title='Django REST Framework',
            description='Learn web APIs',
            level='intermediate',
            course_time=120
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Authentication & Permissions',
            order=1
        )
        self.lesson = Lesson.objects.create(
            section=self.section,
            title='Implementing JWT',
            description='Use simplejwt',
            time=25,
            author=self.user,
            order=1
        )

    def test_list_lessons(self):
        url = reverse('tutorials:lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['slug'], self.lesson.slug)

    def test_get_course_details_by_slug(self):
        url = reverse('tutorials:course-detail', kwargs={'slug': self.course.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course.title)
        self.assertEqual(len(response.data['sections']), 1)
        self.assertEqual(response.data['sections'][0]['slug'], self.section.slug)

    def test_get_sections_under_course(self):
        url = reverse('tutorials:course-sections', kwargs={'slug': self.course.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['slug'], self.section.slug)

    def test_get_section_details_by_slug(self):
        url = reverse('tutorials:section-detail', kwargs={'slug': self.section.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.section.title)
        self.assertEqual(len(response.data['lessons']), 1)
        self.assertEqual(response.data['lessons'][0]['slug'], self.lesson.slug)

    def test_get_lessons_under_section(self):
        url = reverse('tutorials:section-lessons', kwargs={'slug': self.section.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['slug'], self.lesson.slug)

    def test_get_lesson_details_by_slug(self):
        self.lesson.video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        self.lesson.save()
        url = reverse('tutorials:lesson-detail', kwargs={'slug': self.lesson.slug})
        
        # Initial views is 0
        self.assertEqual(self.lesson.views, 0)

        # First request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.lesson.title)
        self.assertEqual(response.data['author']['email'], self.user.email)
        self.assertEqual(response.data['video_url'], 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.assertEqual(response.data['views'], 1)

        # Second request
        response = self.client.get(url)
        self.assertEqual(response.data['views'], 2)

        # Verify database is updated
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.views, 2)

    def test_get_quiz_by_lesson_slug(self):
        quiz = Quiz.objects.create(lesson=self.lesson, title="DRF JWT Quiz", passing_score=80)
        question = Question.objects.create(quiz=quiz, text="What does JWT stand for?", order=1)
        Choice.objects.create(question=question, text="JSON Web Token", is_correct=True)
        Choice.objects.create(question=question, text="Java Web Token", is_correct=False)

        url = reverse('tutorials:lesson-quiz', kwargs={'slug': self.lesson.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "DRF JWT Quiz")
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(len(response.data['questions'][0]['choices']), 2)
        
        # Verify cheat prevention (is_correct must not be returned)
        self.assertNotIn('is_correct', response.data['questions'][0]['choices'][0])

    def test_quiz_attempt_scoring_success(self):
        quiz = Quiz.objects.create(lesson=self.lesson, title="Scoring Quiz", passing_score=75)
        q1 = Question.objects.create(quiz=quiz, text="Q1", order=1)
        q2 = Question.objects.create(quiz=quiz, text="Q2", order=2)

        c1_correct = Choice.objects.create(question=q1, text="C1 Correct", is_correct=True)
        c1_incorrect = Choice.objects.create(question=q1, text="C1 Incorrect", is_correct=False)
        c2_correct = Choice.objects.create(question=q2, text="C2 Correct", is_correct=True)
        c2_incorrect = Choice.objects.create(question=q2, text="C2 Incorrect", is_correct=False)

        url = reverse('tutorials:quiz-attempt', kwargs={'pk': quiz.id})
        
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # 1. Attempt scoring 50% (Passed=False)
        payload = {
            "answers": [
                {"question_id": q1.id, "choice_id": c1_correct.id},
                {"question_id": q2.id, "choice_id": c2_incorrect.id}
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 50)
        self.assertFalse(response.data['is_passed'])
        self.assertEqual(len(response.data['answers_feedback']), 2)

        # 2. Attempt scoring 100% (Passed=True)
        payload_all_correct = {
            "answers": [
                {"question_id": q1.id, "choice_id": c1_correct.id},
                {"question_id": q2.id, "choice_id": c2_correct.id}
            ]
        }
        response = self.client.post(url, payload_all_correct, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 100)
        self.assertTrue(response.data['is_passed'])

    def test_quiz_leaderboard_first_attempt_only(self):
        quiz = Quiz.objects.create(lesson=self.lesson, title="Leaderboard Quiz", passing_score=50)
        q = Question.objects.create(quiz=quiz, text="Q", order=1)
        Choice.objects.create(question=q, text="C1", is_correct=True)

        url = reverse('tutorials:quiz-leaderboard', kwargs={'pk': quiz.id})

        # User 1 makes their first attempt (score 50%)
        QuizAttempt.objects.create(user=self.user, quiz=quiz, score=50)
        
        # User 1 makes their second attempt (score 100%) -> Should NOT count in leaderboard
        QuizAttempt.objects.create(user=self.user, quiz=quiz, score=100)

        # User 2 makes their first attempt (score 80%)
        QuizAttempt.objects.create(user=self.user2, quiz=quiz, score=80)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Leaderboard should have 2 entries (one per unique user)
        self.assertEqual(len(response.data), 2)
        
        # Entry 1: User 2 (Rank 1, Score 80)
        self.assertEqual(response.data[0]['rank'], 1)
        self.assertEqual(response.data[0]['user_id'], self.user2.id)
        self.assertEqual(response.data[0]['score'], 80)
        
        # Entry 2: User 1 (Rank 2, Score 50) -- ignoring their 100 score second attempt
        self.assertEqual(response.data[1]['rank'], 2)
        self.assertEqual(response.data[1]['user_id'], self.user.id)
        self.assertEqual(response.data[1]['score'], 50)

    def test_quiz_attempt_unauthorized(self):
        quiz = Quiz.objects.create(lesson=self.lesson, title="Unauthorized Test Quiz", passing_score=75)
        url = reverse('tutorials:quiz-attempt', kwargs={'pk': quiz.id})
        
        # Do not force authenticate
        response = self.client.post(url, {"answers": []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TutorialRatingAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='password123',
            full_name='Rating User'
        )
        self.course = Course.objects.create(
            title='Django Advanced Development',
            description='Learn advanced Django patterns',
            level='pro',
            course_time=240
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Introduction',
            order=1
        )
        self.lesson = Lesson.objects.create(
            section=self.section,
            title='Vite Setup',
            description='Setup Vite project',
            time=15,
            author=self.user,
            order=1
        )

    def test_course_rate_success(self):
        url = reverse('tutorials:course-rate', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.user)
        
        payload = {'rating': 5, 'review': 'Excellent course!'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['review'], 'Excellent course!')
        self.assertEqual(response.data['course'], self.course.id)
        self.assertEqual(response.data['user'], self.user.id)
        
        # Verify db persistence
        self.assertEqual(CourseRating.objects.count(), 1)
        rating_obj = CourseRating.objects.first()
        self.assertEqual(rating_obj.rating, 5)
        self.assertEqual(rating_obj.review, 'Excellent course!')

    def test_course_rate_once_only(self):
        url = reverse('tutorials:course-rate', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.user)
        
        # First rating
        response1 = self.client.post(url, {'rating': 4, 'review': 'Good'}, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseRating.objects.count(), 1)
        
        # Second rating attempt should fail
        payload = {'rating': 5, 'review': 'Attempt two'}
        response2 = self.client.post(url, payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['detail'], 'You have already rated this course. Use PUT or PATCH to edit it.')
        
        # Verify db persistence is still 1 entry, and not updated
        self.assertEqual(CourseRating.objects.count(), 1)
        rating_obj = CourseRating.objects.first()
        self.assertEqual(rating_obj.rating, 4)
        self.assertEqual(rating_obj.review, 'Good')

    def test_course_rate_validation(self):
        url = reverse('tutorials:course-rate', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.user)
        
        # Rating too high
        response = self.client.post(url, {'rating': 6}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)
        
        # Rating too low
        response = self.client.post(url, {'rating': 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    def test_lesson_rate_success(self):
        url = reverse('tutorials:lesson-rate', kwargs={'slug': self.lesson.slug})
        self.client.force_authenticate(user=self.user)
        
        payload = {'rating': 4, 'review': 'Very nice lesson'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['review'], 'Very nice lesson')
        self.assertEqual(response.data['lesson'], self.lesson.id)
        
        # Verify db persistence
        self.assertEqual(LessonRating.objects.count(), 1)
        rating_obj = LessonRating.objects.first()
        self.assertEqual(rating_obj.rating, 4)
        self.assertEqual(rating_obj.review, 'Very nice lesson')

    def test_lesson_rate_once_only(self):
        url = reverse('tutorials:lesson-rate', kwargs={'slug': self.lesson.slug})
        self.client.force_authenticate(user=self.user)
        
        # First rating
        response1 = self.client.post(url, {'rating': 3, 'review': 'Okay'}, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LessonRating.objects.count(), 1)
        
        # Second rating attempt should fail
        payload = {'rating': 4, 'review': 'Actually better'}
        response2 = self.client.post(url, payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['detail'], 'You have already rated this lesson. Use PUT or PATCH to edit it.')
        
        # Verify db persistence is still 1 entry, and not updated
        self.assertEqual(LessonRating.objects.count(), 1)
        rating_obj = LessonRating.objects.first()
        self.assertEqual(rating_obj.rating, 3)
        self.assertEqual(rating_obj.review, 'Okay')

    def test_lesson_rate_validation(self):
        url = reverse('tutorials:lesson-rate', kwargs={'slug': self.lesson.slug})
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(url, {'rating': 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    def test_rate_unauthorized(self):
        # Anonymous user rating course
        course_url = reverse('tutorials:course-rate', kwargs={'slug': self.course.slug})
        response = self.client.post(course_url, {'rating': 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Anonymous user rating lesson
        lesson_url = reverse('tutorials:lesson-rate', kwargs={'slug': self.lesson.slug})
        response = self.client.post(lesson_url, {'rating': 4}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Anonymous user GET rating
        response = self.client.get(course_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(lesson_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_update_delete_course_rating(self):
        url = reverse('tutorials:course-rate', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.user)

        # 1. GET rating when none exists -> 404
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 2. POST rating -> 201
        self.client.post(url, {'rating': 4, 'review': 'Initial rating'}, format='json')
        self.assertEqual(CourseRating.objects.count(), 1)

        # 3. GET rating -> 200
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['review'], 'Initial rating')

        # 4. PUT rating -> 200
        response = self.client.put(url, {'rating': 5, 'review': 'Updated rating'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['review'], 'Updated rating')
        self.assertEqual(CourseRating.objects.first().rating, 5)

        # 5. PATCH rating -> 200
        response = self.client.patch(url, {'review': 'Patched review'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5) # Rating unchanged
        self.assertEqual(response.data['review'], 'Patched review')

        # 6. DELETE rating -> 204
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CourseRating.objects.count(), 0)

        # 7. GET rating after delete -> 404
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_update_delete_lesson_rating(self):
        url = reverse('tutorials:lesson-rate', kwargs={'slug': self.lesson.slug})
        self.client.force_authenticate(user=self.user)

        # 1. GET rating when none exists -> 404
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 2. POST rating -> 201
        self.client.post(url, {'rating': 3, 'review': 'Ok lesson'}, format='json')
        self.assertEqual(LessonRating.objects.count(), 1)

        # 3. GET rating -> 200
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 3)
        self.assertEqual(response.data['review'], 'Ok lesson')

        # 4. PUT rating -> 200
        response = self.client.put(url, {'rating': 4, 'review': 'Better lesson'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['review'], 'Better lesson')
        self.assertEqual(LessonRating.objects.first().rating, 4)

        # 5. PATCH rating -> 200
        response = self.client.patch(url, {'review': 'Patched lesson'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['review'], 'Patched lesson')

        # 6. DELETE rating -> 204
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LessonRating.objects.count(), 0)

        # 7. GET rating after delete -> 404
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BannerAPITests(APITestCase):

    def setUp(self):
        self.image_file = SimpleUploadedFile("banner.png", b"image data", content_type="image/png")
        
        self.banner1 = Banner.objects.create(
            title="Banner 1",
            badge_text="New",
            description="First banner",
            image=self.image_file,
            order=2,
            is_active=True
        )
        self.banner2 = Banner.objects.create(
            title="Banner 2",
            badge_text="Trending",
            description="Second banner",
            image=self.image_file,
            order=1,
            is_active=True
        )
        self.banner3 = Banner.objects.create(
            title="Banner 3",
            description="Inactive banner",
            image=self.image_file,
            order=3,
            is_active=False
        )

    def test_list_banners_success(self):
        url = reverse('tutorials:banner-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return only active banners
        self.assertEqual(len(response.data), 2)
        
        # Verify ordering (order=1 should come first: Banner 2, then order=2: Banner 1)
        self.assertEqual(response.data[0]['title'], "Banner 2")
        self.assertEqual(response.data[1]['title'], "Banner 1")
        
        # Check payload fields
        self.assertEqual(response.data[0]['badge_text'], "Trending")
        self.assertIn('image', response.data[0])


class GamificationAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='gamer@example.com',
            email='gamer@example.com',
            password='password123',
            full_name='Gamer User'
        )
        self.course = Course.objects.create(
            title='Gamified Django',
            description='Learn with XP',
            level='intermediate',
            course_time=120
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Chapter 1',
            order=1
        )
        self.lesson1 = Lesson.objects.create(
            section=self.section,
            title='XP Intro',
            description='Earn 100 XP',
            time=10,
            author=self.user,
            order=1
        )
        self.lesson2 = Lesson.objects.create(
            section=self.section,
            title='Badge Intro',
            description='Earn a Badge',
            time=15,
            author=self.user,
            order=2
        )
        self.badge = Badge.objects.create(
            name='Django Master Badge',
            description='Completed the Gamified Django course!',
            course=self.course
        )

    def test_complete_lesson_adds_xp_and_awards_badge(self):
        self.client.force_authenticate(user=self.user)
        
        # Verify initial XP is 0
        self.assertEqual(self.user.xp, 0)
        
        # 1. Complete first lesson -> 100 XP
        url1 = reverse('tutorials:lesson-complete', kwargs={'slug': self.lesson1.slug})
        response = self.client.post(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['xp_gained'], 100)
        self.assertEqual(response.data['total_xp'], 100)
        self.assertFalse(response.data['course_completed'])
        self.assertIsNone(response.data['badge_earned'])

        # Verify db user XP is updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.xp, 100)

        # 2. Attempt completing lesson1 again -> No new XP, not created
        response_dup = self.client.post(url1)
        self.assertEqual(response_dup.status_code, status.HTTP_200_OK)
        self.assertEqual(response_dup.data['xp_gained'], 0)
        self.assertEqual(response_dup.data['total_xp'], 100)

        # 3. Complete second (and final) lesson -> 100 XP + course complete + Badge
        url2 = reverse('tutorials:lesson-complete', kwargs={'slug': self.lesson2.slug})
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['xp_gained'], 100)
        self.assertEqual(response2.data['total_xp'], 200)
        self.assertTrue(response2.data['course_completed'])
        self.assertIsNotNone(response2.data['badge_earned'])
        self.assertEqual(response2.data['badge_earned']['name'], 'Django Master Badge')

        # Verify User has UserBadge record
        self.assertEqual(UserBadge.objects.filter(user=self.user, badge=self.badge).count(), 1)

        # 4. Check user profile endpoint (/api/users/me/) returns correct XP, level and badges
        profile_url = reverse('users:me')
        profile_response = self.client.get(profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['xp'], 200)
        self.assertEqual(profile_response.data['level'], 1) # level = 200 // 1000 + 1 = 1
        self.assertEqual(len(profile_response.data['earned_badges']), 1)
        self.assertEqual(profile_response.data['earned_badges'][0]['badge_name'], 'Django Master Badge')

        # 5. Check user badges endpoint (/api/users/me/badges/) returns earned badges list
        badges_url = reverse('users:me_badges')
        badges_response = self.client.get(badges_url)
        self.assertEqual(badges_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(badges_response.data), 1)
        self.assertEqual(badges_response.data[0]['badge_name'], 'Django Master Badge')

        # 6. Check all badges endpoint (/api/badges/) returns all badges, earned status, and user XP
        all_badges_url = reverse('tutorials:badge-list')
        all_badges_response = self.client.get(all_badges_url)
        self.assertEqual(all_badges_response.status_code, status.HTTP_200_OK)
        self.assertEqual(all_badges_response.data['xp'], 200)
        self.assertEqual(all_badges_response.data['level'], 1)
        self.assertEqual(len(all_badges_response.data['badges']), 1)
        self.assertTrue(all_badges_response.data['badges'][0]['is_earned'])
        self.assertEqual(all_badges_response.data['badges'][0]['name'], 'Django Master Badge')

        # 7. Verify anonymous user receives 401 Unauthorized for badges list
        self.client.logout()
        anon_response = self.client.get(badges_url)
        self.assertEqual(anon_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 8. Verify anonymous user receives 401 Unauthorized for all badges list
        anon_all_response = self.client.get(all_badges_url)
        self.assertEqual(anon_all_response.status_code, status.HTTP_401_UNAUTHORIZED)

