import datetime
from re import T

from django.db import models
from django.utils import timezone
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect 

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ended', null=True)
    
    def __str__(self):
        """Show string of question"""
        return self.question_text
    
    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        """Check whether question was publish less than 1 day or not."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def is_published(self):
        """Check current date is on or after question's publication date."""
        return self.pub_date < timezone.localtime()
    
    def can_vote(self):
        """Check if voting is allowed for this question."""
        if self.end_date:  # check end_date is not NULL
            return self.end_date > timezone.localtime()
        return self.is_published()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)
    
    @property
    def votes(self):
        """Count the number of vote for this choice."""
        return Vote.objects.filter(choice=self).count()
    
    def __str__(self):
        """Show string of choice"""
        return self.choice_text
    
    
class Vote(models.Model):
    """A vote by a user for a question."""
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)

