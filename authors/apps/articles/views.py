from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException

from .models import Article, ArticleImage
from .serializers import ArticleSerializer, ArticleImageSerializer
from .permissions import ReadOnly
from authors.apps.authentication.models import User
import cloudinary


class ArticleView(APIView):
    """Class that contains the method that retrieves all articles and creates an article"""
    permission_classes = (IsAuthenticated | ReadOnly,)

    def get(self, request):
        """Method to get all articles"""
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({"articles": serializer.data})

    def post(self, request):
        """Method to create an article"""
        article = request.data.get('article')

        # Create an article from the above data
        serializer = ArticleSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save(author=self.request.user)

        return Response(
            {
                "success": "Article '{}' created successfully".format(article_saved.title)
            }, status=201)


class RetrieveArticleView(APIView):
    """Class with get, put and delete methods"""
    permission_classes = (IsAuthenticated | ReadOnly,)

    def is_owner(self, current_user_id, article_author_id):
        if article_author_id == current_user_id:
            return True
        return False

    def get(self, request, slug):
        """Method to get a specific article"""
        try:
            article = Article.objects.get(slug=slug)
            serializer = ArticleSerializer(article, many=False)
            return Response({"article": serializer.data})
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

    def put(self, request, slug):
        """Method to update a specific article"""
        try:
            saved_article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

        data = request.data.get('article')
        serializer = ArticleSerializer(
            instance=saved_article, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if self.is_owner(saved_article.author.id, request.user.id) is True:
                article_saved = serializer.save()
                return Response({"success": "Article '{}' updated successfully".format(article_saved.title)})
            response = {"message": "Only the owner can edit this article."}
            return Response(response, status=403)

    def delete(self, request, slug):
        """Method to delete a specific article"""
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

        if self.is_owner(article.author.id, request.user.id) is True:
            article.delete()
            return Response({"message": "Article `{}` has been deleted.".format(slug)}, status=200)

        response = {"message": "Only the owner can delete this article."}
        return Response(response, status=403)


class ArticleImageView(APIView):
    """Class with methods to upload an image and retrieve all images of an article"""
    permission_classes = (IsAuthenticated | ReadOnly,)

    def post(self, request, slug):
        """Method to upload an image"""

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

        if request.FILES:
            try:
                response = cloudinary.uploader.upload(
                    request.FILES['file'], allowed_formats=['png', 'jpg', 'jpeg'])
            except Exception as e:
                APIException.status_code = 400
                raise APIException({
                    "errors": str(e)
                })
            image_url = response.get('secure_url')

            serializer = ArticleImageSerializer(data={"image": image_url})
            if serializer.is_valid(raise_exception=True):
                serializer.save(article=article)

            response = {"message": "Image uploaded Successfully"}
            return Response(response, status=200)

        else:
            response = {"message": "Image uploaded failed."}
            return Response(response, status=400)

    def get(self, request, slug):
        """Method to get all images of an article"""
        images = ArticleImage.objects.select_related(
            'article').filter(article__slug=slug)
        serializer = ArticleImageSerializer(images, many=True)
        return Response({"images": serializer.data})