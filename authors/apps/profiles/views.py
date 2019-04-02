from rest_framework.views import APIView
from .serializers import ProfileSerializer
from .models import Profile


class ListProfiles(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, JWTAuthentication, )
    # queryset = Profile.objects.all()
    # serializer_class = ProfileSerializer

    def get(self, request, pk):
        profile = get_object_or_404(Profile.objects.all(), pk=pk)
        serializer = ProfileSerializer(profile)
        return Response({"Profile": serializer.data})

    def post(self, request):
        profile = request.data.get('profile')

        serializer = ProfileSerializer(data=profile)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save()
        return Response({"success": "Profile '{}' created successfully".format(profile_saved.title)})

    def put(self, request, pk):
        saved_profile = get_object_or_404(Profile.objects.all(), pk=pk)
        data = request.data.get('profile')
        serializer = ProfileSerializer(
            instance=saved_profile, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save()
        return Response({"success": "Profile '{}' updated successfully".format(profile_saved.title)})