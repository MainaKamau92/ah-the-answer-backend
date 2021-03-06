from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment


class TestCommentsModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@mail.com",
            username="test",
            password="test1234"
        )
        self.article = Article.objects.create(
            title="This Article",
            body="Best article body ever",
            author=self.user
        )

    def test_model_created(self):
        """
        Test that the model is created successfully
        """
        comment = Comment.objects.create(
            body="This is a nice article",
            author=self.user,
            article=self.article
        )

        self.assertTrue(comment)
        self.assertEqual(comment.body, "This is a nice article")
        self.assertEqual(comment.__str__(), 'This is a nice ...')


class TestCommentsAPI(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user_signup = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "test@mail.com",
                    "username": "test",
                    "password": "test1234"
                }
            },
            format="json"
        )
        self.user = User.objects.get(
            email=self.user_signup.data.get('email')
        )
        self.user.is_verified = True
        self.user.save()
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test@mail.com",
                    "password": "test1234"
                }
            },
            format="json"
        )
        self.token = self.login.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.article = Article.objects.create(
            title="Test title",
            body="This is a very awesome article on testing tests",
            description="Written by testing tester",
            author=self.user
        )

        # Create Comment
        self.comment = self.client.post(
            reverse(
                'comments:create-list',
                kwargs={
                    "slug": self.article.slug
                }
            ),
            data={
                "comment": {
                    "body": "This is a comment"
                }
            },
            format="json"
        )
        self.comment_id = self.comment.data.get('comment')['id']

    def test_create_comment(self):
        """
        Test that a comment is created on sending a POST request
        """
        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)

    def test_get_all_comments(self):
        """
        Test that all comments are retrieved on sending a GET request
        """
        res = self.client.get(
            reverse(
                'comments:create-list',
                kwargs={
                    "slug": self.article.slug
                }
            ),
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_specific_comment(self):
        """
        Test that a specific comment is retrieved on sending a GET request
        """
        res = self.client.get(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_error_on_invalid_data(self):
        """
        Test that an error is displayed when invalid values are supplied
        """
        res1 = self.client.post(
            reverse(
                'comments:create-list',
                kwargs={
                    "slug": self.article.slug
                }
            ),
            data={
                "comment": {
                    "body": "      "
                }
            },
            format="json"
        )

        res2 = self.client.post(
            reverse(
                'comments:create-list',
                kwargs={
                    "slug": self.article.slug
                }
            ),
            data={
                "comment": {
                    "body": True
                }
            },
            format="json"
        )

        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_comment(self):
        """
        Test that a comment is updated successfully
        """

        res = self.client.put(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            data={
                "comment": {
                    "body": "This is an updated comment"
                }
            },
            format="json"
        )

        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            self.comment.data.get('comment'),
            res.data.get('comment')
        )

    def test_delete_comment(self):
        """
        Test that comment can be deleted
        """
        del_res = self.client.delete(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)

    def test_delete_non_existent_comment(self):
        """
        Test that error raised if comment to be deleted does not exist
        """
        del_res = self.client.delete(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        res = self.client.get(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_get_comment_history(self):
        self.test_create_comment()
        self.test_update_comment()
        res = self.client.get(
            reverse(
                'comments:comment-history',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_can_view_comment_history(self):
        self.test_create_comment()
        self.test_update_comment()
        self.client.logout()
        res = self.client.get(
            reverse(
                'comments:comment-history',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_all_users_can_view_others_history(self):
        user = User.objects.create(username="johndoe")
        self.client2 = test.APIClient()
        self.client2.force_authenticate(user=user)
        self.test_create_comment()
        self.test_update_comment()
        res = self.client2.get(
            reverse(
                'comments:comment-history',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_cant_get_inexistent_comment_history(self):
        res = self.client.get(
            reverse(
                'comments:comment-history',
                kwargs={
                    "slug": self.article.slug,
                    'pk': 100
                }
            ),
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        self.comment = None
