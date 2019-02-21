from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # user model extensions here:
    #friends = models.ManyToManyField(User, through="Connection")
    text = models.TextField(max_length=255)

# Signals for profile:
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class RatingInfo(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=(MinValueValidator(0),MaxValueValidator(5)))
    class Meta:
        abstract = True
class MovieRating(RatingInfo):
    title = models.CharField(blank=False, null=False, max_length=255, default='')
class GenreRating(RatingInfo):
    genre = models.CharField(blank=False, null=False, max_length=255, default='')
class DirectorRating(RatingInfo):
    director = models.CharField(blank=False, null=False, max_length=255, default='')
class WriterRating(RatingInfo):
    writer = models.CharField(blank=False, null=False, max_length=255, default='')
class ActorRating(RatingInfo):
    actor = models.CharField(blank=False, null=False, max_length=255, default='')
#connection throughtable
#class Connection(models.Model):
#    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends")
#    user2 = models.ForeignKey(User, on_delete=models.CASCADE)
#    # connection specific information:
