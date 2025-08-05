from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, UserGroupSerializer, CustomTokenObtainPairSerializer
from .utils import assign_user_to_group, get_user_type
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'assign_user_type':
            return [permissions.IsAdminUser()]
        return super().get_permissions()
        
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            user = request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            user = request.user
            serializer = self.get_serializer(user, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign_user_type(self, request, pk=None):
        """
        Assign a user type (group) to a user. Only admins can do this.
        """
        user = self.get_object()
        serializer = UserGroupSerializer(data=request.data)
        
        if serializer.is_valid():
            user_type = serializer.validated_data['user_type']
            success = assign_user_to_group(user, user_type)
            
            if success:
                return Response({
                    'message': f'User {user.username} assigned to {user_type} group successfully',
                    'user_type': get_user_type(user)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': f'Failed to assign user to {user_type} group. Group may not exist.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def user_types(self, request):
        """
        Get available user types.
        """
        from .utils import get_available_user_types
        return Response({
            'user_types': get_available_user_types()
        })
