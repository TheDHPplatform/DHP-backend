from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .utils import get_user_type

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user type to the response
        data['user_type'] = get_user_type(self.user)
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data


class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password', 'user_type', 'groups')
        extra_kwargs = {'password': {'write_only': True}}

    def get_user_type(self, obj):
        return get_user_type(obj)

    def create(self, validated_data):
        validated_data['email'] = validated_data.get('email', '').lower()
        if(User.objects.filter(email=validated_data['email']).exists()):
            raise serializers.ValidationError("A user with this email already exists.")
        user = User.objects.create_user(**validated_data)
        # Assign new users to 'public' group by default
        from django.contrib.auth.models import Group
        try:
            public_group = Group.objects.get(name='public')
            user.groups.add(public_group)
        except Group.DoesNotExist:
            pass
        return user


class UserGroupSerializer(serializers.Serializer):
    user_type = serializers.ChoiceField(choices=['public', 'creator', 'admin'])
    
    def validate_user_type(self, value):
        from .utils import get_available_user_types
        if value not in get_available_user_types():
            raise serializers.ValidationError("Invalid user type")
        return value