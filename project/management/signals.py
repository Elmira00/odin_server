from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import *
    
_previous_status = {}
_previous_is_deleted = {}

@receiver(pre_save, sender=Task)
def track_old_fields(sender, instance, **kwargs):
    if instance.pk:
        old = Task.objects.filter(pk=instance.pk).first()
        if old:
            _previous_status[instance.pk] = old.status
            _previous_is_deleted[instance.pk] = old.is_deleted

@receiver(post_save, sender=Task)
def log_task_save(sender, instance, created, **kwargs):
    user = getattr(instance, 'created_by', None)  

    if created:
        Action.objects.create(
            user=user,
            action_type='create',
            task=instance,
            description=f"ID : {instance.id} Task created with status '{instance.status}'"
        )
    else:
        old_status = _previous_status.pop(instance.pk, None)
        old_is_deleted = _previous_is_deleted.pop(instance.pk, None)

        if old_is_deleted is False and instance.is_deleted is True:
            Action.objects.create(
                user=user,
                action_type='delete',  
                task=instance,
                description="Task soft deleted"

            )
        elif old_status and old_status != instance.status:
            Action.objects.create(
                user=user,
                action_type='status_change',
                task=instance,
                description=f"Status changed from '{old_status}' to '{instance.status}'"
            )
        

# @receiver(post_delete, sender=Task)
# def log_task_delete(sender, instance, **kwargs):
#     Action.objects.create(
#         user=None,
#         action_type='delete',
#         task=instance,
#         description="Task deleted"
#     )

@receiver(post_save, sender=Comment)
def log_comment(sender, instance, created, **kwargs):
    if created:
        Action.objects.create(
            user=instance.user,
            action_type='comment',
            task=instance.task,
            description=f"Commented: {instance.comment[:50]}"
        )



# # @receiver(post_save, sender=Comment)
# # def assign_user_on_comment(sender, instance, created, **kwargs):
# #     if created and instance.user and instance.task:
# #         instance.task.assigned_to.add(instance.user)

@receiver(post_save, sender=Action)
def assign_user_on_action(sender, instance, created, **kwargs):
    if created and instance.user and instance.task:
        instance.task.assigned_to.add(instance.user)
