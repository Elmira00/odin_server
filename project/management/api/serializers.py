from management.models import *
from rest_framework import serializers


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "comment", "created_at"]


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ["id", "user", "action_type", "description", "timestamp"]


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field="username")
    assigned_to = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )
    effective_category = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "problem",
            "created_by",
            "assigned_to",
            "category",
            "content",
            "status",
            "created_at",
            "is_deleted",
            "effective_category",
            "comments",
            "comment",
        ]

    def get_effective_category(self, obj):
        return obj.effective_category.category if obj.effective_category else None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category"]


class ProblemSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = Problem
        fields = [
            "id",
            "source",
            "source_name",
            "category",
            "problem_description",
            "created_at",
        ]
