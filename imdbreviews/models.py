from django.db import models
from django.utils.timezone import now
from picklefield.fields import PickledObjectField

class Movie(models.Model):
	title = models.CharField(max_length=500)
	summary = models.CharField(max_length=8000)
	actors = models.CharField(max_length=100000)
	release_date = models.DateTimeField()
	movie_id = models.CharField(max_length=10)


class Review(models.Model):
	title = models.CharField(max_length = 400)
	content = models.CharField(max_length=400)
	review_date = models.DateTimeField(default=now)
	review_id = models.CharField(max_length=10)
	movie_id = models.CharField(max_length = 10)
	rating = models.IntegerField()
	helpfulness = models.IntegerField() 
	number_voted = models.IntegerField(default=0)
	user_reviewed = models.CharField(max_length=100)
	#a dictionary object of the usernames that have voted on the review and his/her vote, i.e. 'emmabean': 'yes'
	#allow own reviewer to vote (once) on the review
	users_reviewed = PickledObjectField()


class User(models.Model):
	username = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	user_id = models.CharField(max_length=100)
	date_joined = models.DateTimeField()




