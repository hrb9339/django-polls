import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        question = create_question("Old question", days=-2)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        question = create_question("Recent question", days=0)
        self.assertIs(question.was_published_recently(), True)

    def test_str(self):
        question = create_question("Favorite language?", days=0)
        choice = Choice.objects.create(question=question, choice_text="Python")
        self.assertEqual(str(question), "Favorite language?")
        self.assertEqual(str(choice), "Python")


class PollViewTests(TestCase):
    def setUp(self):
        self.question = create_question("Favorite language?", days=-1)
        self.choice = Choice.objects.create(
            question=self.question, choice_text="Python"
        )

    def test_index_lists_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Favorite language?")

    def test_index_with_no_questions(self):
        Question.objects.all().delete()
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_detail_view(self):
        response = self.client.get(reverse("polls:detail", args=(self.question.id,)))
        self.assertContains(response, "Python")

    def test_results_view(self):
        response = self.client.get(reverse("polls:results", args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_vote_increments_choice(self):
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)),
            {"choice": self.choice.id},
        )
        self.assertRedirects(
            response, reverse("polls:results", args=(self.question.id,))
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)

    def test_vote_without_choice_shows_error(self):
        response = self.client.post(reverse("polls:vote", args=(self.question.id,)))
        self.assertContains(response, "Please select a choice.")
