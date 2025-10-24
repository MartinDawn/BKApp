from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Khởi tạo 'address' mặc định là chuỗi rỗng ""
    address = models.TextField(default="", blank=True)
    rating = models.FloatField(default=0.0)
    num_reviews = models.IntegerField(default=0)
    

    def __str__(self):
        return f'{self.user.username} Profile'

# --- Tín hiệu (Signal) tự động tạo Profile ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Tự động TẠO một Profile mới mỗi khi một User
    được đăng ký thành công (kể cả qua Google).
    """
    if created:
        Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     """
#     Tự động LƯU Profile mỗi khi User được lưu.
#     """
#     instance.profile.save()