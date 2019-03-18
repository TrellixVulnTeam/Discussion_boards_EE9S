from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator
from django.utils.html import mark_safe
from markdown import markdown
import math
# Create your models here.
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class Board(models.Model):
	# 'max_legth' used in form validation and 
	# 'Charfield' used in database validation
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()   


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    #reverse relationship identified by 'related_name'
    board = models.ForeignKey(Board, on_delete = models.CASCADE,
            related_name='topics')
    #reverse relationship
    starter = models.ForeignKey(User, on_delete = models.SET(get_sentinel_user),
            related_name='topics')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 20
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)
        
    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]        




class Post(models.Model):
    message = models.TextField(max_length=4000)
    #reverse relationship (one to many relationship)
    topic = models.ForeignKey(Topic, on_delete = models.CASCADE,
    	  related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    #reverse relationship
    created_by = models.ForeignKey(User, on_delete = models.SET(get_sentinel_user),
               related_name='posts')
    #reverse relationship ignored using '+'and  
    #this is direct association(intersted in one side of relationship only)
    updated_by = models.ForeignKey(User, on_delete = models.SET(get_sentinel_user),
               null=True, related_name='+')

    # When using the markdown function, we are instructing it to
    # escape the special characters first and then parse the markdown
    # tags. After that, we mark the output string as safe to be used 
    # in the template.
    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)