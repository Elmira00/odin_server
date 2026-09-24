from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class CanArchiveTask(BasePermission):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('review', 'Review'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ]

    BASIC_STATUSES = ['pending', 'processing', 'review']
    RESTRICTED_STATUSES = ['completed', 'archived']

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            new_status = request.data.get('status')
            current_status = obj.status

            if not new_status or new_status == current_status:
                return True 

            if current_status == 'archived':
                raise PermissionDenied("Archived tasks cannot be modified.")

            if new_status == 'archived':
                if not request.user.is_superuser:
                    raise PermissionDenied("Only superusers can archive tasks.")

            if new_status == 'completed' and not request.user.is_superuser:
                raise PermissionDenied("Only superusers can mark tasks as completed.")

            if current_status == 'completed' and new_status in self.BASIC_STATUSES:
                return True

            
            if new_status in self.BASIC_STATUSES:
                return True

           
            
        return True
