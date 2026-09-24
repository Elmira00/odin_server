from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User
from management.models import Task

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    remember_me = serializers.BooleanField(default=False, required=False)
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            data['user'] = user
            return data
        raise serializers.ValidationError("Invalid credentials")


class TaskSummarySerializer(serializers.ModelSerializer):
    effective_category = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'status', 'effective_category', 'created_at']

    def get_effective_category(self, obj):
        return str(obj.effective_category) if obj.effective_category else None


class UserSerializer(serializers.ModelSerializer):
    created_tasks = serializers.SerializerMethodField()
    assigned_tasks = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_tasks', 'assigned_tasks', 'is_superuser', 'is_active']

    def filter_tasks(self, task_qs):
        return task_qs.filter(is_deleted=False).exclude(status='archived')

    def get_created_tasks(self, obj):
        return TaskSummarySerializer(self.filter_tasks(obj.created_tasks), many=True).data

    def get_assigned_tasks(self, obj):
        return TaskSummarySerializer(self.filter_tasks(obj.assigned_tasks), many=True).data
