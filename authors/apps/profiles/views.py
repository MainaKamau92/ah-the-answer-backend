from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

import cloudinary

from .models import Profile
from ..authentication.models import User
from .serializers import ProfileSerializer


class CreateRetrieveProfileView(APIView):
    """Implements two user profile related views. The 'get' view fetches a single
    profile from the database and the 'post' view creates a single user
    profile."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        """Returns a single user profile. Matches a profile
        based on the username."""
        user = User.objects.get(username=username)
        uid = user.pk
        profile = get_object_or_404(Profile.objects.all(), user_id=uid)
        serializer = ProfileSerializer(profile, many=False)
        return Response({"profile": serializer.data})

    def post(self, request):
        """Creates and saves a single user profile to the database. Checks if
        a profile already exits for the current user."""
        user_check = self.request.user
        try:
            profile_check = Profile.objects.get(user=user_check).id
        except ObjectDoesNotExist:
            profile_check = None
        if user_check.id == profile_check:
            return Response('A profile for this user already exists. Please '
                            'choose a new user to create a profile.',
                            status=status.HTTP_400_BAD_REQUEST)
        profile = request.data.get('profile')
        serializer = ProfileSerializer(data=profile)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save(user=self.request.user)
            return Response({"success": "Profile for '{}' created successfully"
                             .format(profile_saved)},
                            status=status.HTTP_201_CREATED)
        return Response('Invalid data. Ensure your profile '
                        'payload corresponds to the profile.serializers '
                        'fields.', status=status.HTTP_400_BAD_REQUEST)


class EditProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, username):
        try:
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
            if saved_profile.user != self.request.user:
                # validates ownership of the profile
                APIException.status_code = HTTP_401_UNAUTHORIZED
                raise APIException({
                    "errors": {
                        "Unauthorized": "You are not allowed\
                                        to edit this Profile"
                    }
                })
        except ObjectDoesNotExist:
            APIException.status_code = HTTP_404_NOT_FOUND
            raise APIException(
                {"message": "User with that profile does not exist"})
        data = request.data.get('profile')
        serializer = ProfileSerializer(
            instance=saved_profile, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save()
        return Response(
            {
                "success": "Profile updated successfully",
                "profile": serializer.data
            },
            status=200
        )


class AvatarView(APIView):
    """
    Makes partioal edits to the profile to change the avatar to a desired one
    Throws an Authorization error if user who did not create the profile,
    attempts edits
    """
    permission_classes = (IsAuthenticated, )
    # checks whether user is logged in

    def patch(self, request, username):
        try:
            # retrieves user object throws error if profile is in-existent
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except ObjectDoesNotExist:
            APIException.status_code = HTTP_404_NOT_FOUND
            raise APIException(
                {"message": "User with that profile does not exist"})

        if saved_profile.user != self.request.user:
            APIException.status_code = HTTP_401_UNAUTHORIZED
            raise APIException({
                "errors": {
                    "Unauthorized": "You are not allowed to edit this Profile"
                }
            })
        try:
            avatar_data = str(request.data.get('avatar'))
            if not avatar_data.lower().endswith((".png", ".jpg", ".jpeg")):
                raise APIException(
                    {"message": "This is an invalid avatar format"})
            data = {"avatar": request.data.get('avatar')}
            serializer = ProfileSerializer(
                instance=saved_profile, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(
                {
                    "success": "Profile avatar was updated successfully"
                }, status=200)
        except Exception as e:
            APIException.status_code = HTTP_400_BAD_REQUEST
            raise APIException({
                "errors": str(e)
            })