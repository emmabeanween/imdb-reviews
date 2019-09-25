
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import HttpResponse
from imdbreviews.models import Movie, Review, User
from django.db.models import FloatField, ExpressionWrapper, F
from django.db.models.functions import Cast
from imdbreviews.forms import SortForm, RegisterForm, LoginForm, UserSortForm, ReviewForm
from django.contrib import messages
from random import randint
import datetime
import random
import string
import json
import re


@csrf_exempt
def myHome(request):
	#handle the autocomplete search for movie titles
	if request.is_ajax():
		s = json.loads(request.body)
		#find all titles that contain what the user searched
		list_titles = Movie.objects.filter(title__contains=s).values_list('title', flat=True)
		list_titles = [str(t) + '       ' for t in list_titles]
		#return those titles
		return HttpResponse(list_titles)
	context = {'session': request.session.get("username", None)}
	return render(request, "home.html", context)

@csrf_exempt
def mySearch(request):
	#handle the autocomplete search again
	if request.is_ajax():
		s = json.loads(request.body)
		list_titles = Movie.objects.filter(title__contains=s).values_list('title', flat=True)
		list_titles = [str(t) + '       ' for t in list_titles]
		return HttpResponse(list_titles)

    #pagination, return search results for a movie
	query = request.GET.get("query")
	#get all movies that contain that keyword
	movies = Movie.objects.filter(title__contains=query).all()
	paginator = Paginator(movies, 1)
	#if there is no page as a GET variable
	if request.GET.get("page") is None:
		page = 1
	else:
		#retrieve the current page
		page = int(request.GET.get("page"))
	current_movies = paginator.page(page)
	context  = {'current_movies': current_movies, 'query': query, 'page': page, 'session': request.session.get("username", None)}
	return render(request, "search.html", context)

#return information for a movie title
def myTitle(request, movieid):
	selected_movie = Movie.objects.filter(movie_id=movieid).first()
	actors = selected_movie.actors
	actors = actors.split(",")
	actors = [''.join(a) for a in actors]
	actors = [re.sub("[^a-zA-Z0-9]+", ' ', a) for a in actors]
	context = {'selected_movie': selected_movie, 'actors': actors, 'movieid': movieid, 'session': request.session.get("username",
		None)}
	return render(request, "title.html", context)


#sign in and register a new user in the movie database
def myAuth(request):
	#if there is already a user logged in, redirect them
	if 'username' in request.session:
		return redirect("myHome")
	#handle the POST request
	if request.method == "POST":
		#sign up the user
		if request.POST.get("button") == "signup":
			form = RegisterForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				confirmedpassword = form.cleaned_data['confirmedpassword']
				#evaluate other errors
				errors = []
				if password != confirmedpassword:
					errors.append("passwords need to match.")
				if len(username) < 6:
					errors.append("username is too short.")
				if len(password) < 6:
					errors.append("password is too short.")
				has_capital = any((char.isupper() for char in password))
				if has_capital is False:
					errors.append("password needs to contain at least one capital.")
				has_digit = any((char.isdigit() for char in password))
				if has_digit is False:
					errors.append("password needs to contain at least one digit.")
				if errors:
					for error in errors:
						messages.add_message(request, messages.INFO, error)
						return render(request, "signupandlogin.html", {"registerform": form, 'loginform': LoginForm()})
				else:
					new_user = User(username=username, password=password, user_id= randint(100000, 999999), 
							date_joined= datetime.datetime.now())
					new_user.save()
					#start session
					request.session['username'] = username
					return redirect("myHome")


		else:
			#login request
			form = LoginForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				is_user = User.objects.filter(username=username, password=password).count()
				if is_user is 0:
					#wrong info
					messages.add_message(request, messages.INFO, "your username and/or password are incorrect.")
					return render(request, "signupandlogin.html", {'registerform': RegisterForm(), 'loginform': form})
				else:
					#correct info, redirect
					request.session['username'] = username
					return redirect("myHome")
	context = {'registerform': RegisterForm(), 'loginform': LoginForm() }
	return render(request, "signupandlogin.html", context)



@csrf_exempt
def myReviews(request, movieid):
	#ajax request for the helpfulness of a movie review
	if request.method == 'POST':
		vote = request.POST.get("vote")
		review_id = request.POST.get("review_id")
		review_user_voted_on = Review.objects.filter(review_id=review_id).first()
		users_reviewed = review_user_voted_on.users_reviewed
		current_user = request.session.get("username", None)
		#see if the current signed in user has already voted on a review
		if current_user in users_reviewed:
			#they have previously voted
			current_vote = users_reviewed[current_user]
			#they are changing their vote from yes to no
			if current_vote == 'yes' and vote == 'no':
				#change vote to no
				users_reviewed[current_user] = 'no'
				review_user_voted_on.helpfulness = review_user_voted_on.helpfulness - 1
				#they are changing their vote from no to yes
			if current_vote == 'no' and vote == 'yes':
				#change vote to yes
				users_reviewed[current_user] = 'yes'
				review_user_voted_on.helpfulness = review_user_voted_on.helpfulness + 1


		else:
			#the user has not previously voted on the movie review
			if vote == 'yes':
				#log the user's vote as a yes
				users_reviewed[current_user] = 'yes'
				review_user_voted_on.helpfulness = review_user_voted_on.helpfulness + 1
				review_user_voted_on.number_voted = review_user_voted_on.number_voted + 1
			else:
				#log the user's vote as a no
				users_reviewed[current_user] = 'no'
				review_user_voted_on.number_voted = review_user_voted_on.number_voted + 1
		#save the review
		review_user_voted_on.users_reviewed = users_reviewed
		review_user_voted_on.save()

		return HttpResponse("your vote has been counted! refresh to see your vote.") 

		#request to sort the reviews for a movie
	if request.GET:
		form = SortForm(request.GET)
		movie_title = Movie.objects.filter(movie_id=movieid).first().title
		sort = request.GET['sort']
		rating = request.GET['rating']
		direction = request.GET['direction']
		if sort == 'helpfulness':
			#sorting the reviews for the movie by helpfulness
			if direction == 'asc':
				reviews = Review.objects.annotate(score=Cast(F('helpfulness') * 1.0 / F('number_voted') * 1.0, FloatField())).filter(movie_id=movieid).order_by('score').all()
			else:
				reviews = Review.objects.annotate(score=Cast(F('helpfulness') * 1.0 / F('number_voted') * 1.0, FloatField())).filter(movie_id=movieid).order_by('-score').all()
		#sorting by reviewdate
		elif sort == "reviewdate":
			if direction == 'asc':
				reviews = Review.objects.filter(movie_id=movieid).order_by('review_date')
			else:
				reviews = Review.objects.filter(movie_id=movieid).order_by('-review_date')
		elif sort == "rating":
			#sort the reviews by rating
			if direction == "asc":
				reviews = Review.objects.filter(movie_id=movieid).order_by('rating')
			else:
				reviews = Review.objects.filter(movie_id=movieid).order_by('-rating')
		else:
			#sorting by total votes
			if direction == "asc":
				reviews = Review.objects.filter(movie_id=movieid).order_by('number_voted')
			else:
				reviews = Review.objects.filter(movie_id=movieid).order_by('-number_voted')
		if rating!= "showall":
			#if the user wants to filter the movie reviews by a rating
			reviews = reviews.filter(rating=int(rating)).all()
		else:
			reviews = reviews.all()
		return render(request, "reviews.html", {"title": movie_title, "reviews": reviews, 'session': request.session.get('username', None),
		 'form': form, 'sort': sort, 'movieid': movieid})

	#get the movie title
	movie_title = Movie.objects.filter(movie_id=movieid).first().title
	reviews = Review.objects.annotate(score=Cast(F('helpfulness') * 1.0 / F('number_voted') * 1.0, FloatField())).filter(movie_id=movieid).order_by('-score').all()
	return render(request, "reviews.html", {"title": movie_title, "reviews": reviews, 'movieid': movieid,
		'session': request.session.get('username', None), 'form': SortForm()})


#a view to look at a user's profile information
def userProfile(request, user):
	if request.GET:
		form = UserSortForm(request.GET)
		sort = request.GET['sort']
		direction = request.GET['direction']
		#sort the user's reviews
		if sort == 'helpfulness':
			if direction == 'asc':
				userReviews = Review.objects.annotate(score=Cast(F('helpfulness') * 1.0 / F('number_voted') * 1.0, FloatField())).filter(user_reviewed=user).order_by('score')
			else:
				userReviews = Review.objects.annotate(score=Cast(F('helpfulness') * 1.0 / F('number_voted') * 1.0, FloatField())).filter(user_reviewed=user).order_by('-score')
		elif sort == 'reviewdate':
			if direction == 'asc':
				userReviews = Review.objects.filter(user_reviewed=user).order_by('review_date')
			else:
				userReviews = Review.objects.filter(user_reviewed=user).order_by('-review_date')
		elif sort == 'rating':
			if direction == 'asc':
				userReviews = Review.objects.filter(user_reviewed=user).order_by('rating')
			else:
				userReviews = Review.objects.filter(user_reviewed=user).order_by('-rating')
		else:
			if direction == 'asc':
				userReviews = Review.objects.filter(user_reviewed=user).order_by('number_voted')
			else:
				userReviews = Review.objects.filter(user_reviewed=user).order_by('-number_voted')
		numReviews = userReviews.count()
		userReviews = userReviews.all()
		dateJoined = User.objects.filter(username=user).all()[0].date_joined.date()
		movie_titles = []
		movie_ids = []
		for review in userReviews:
			each_id = review.movie_id
			movie_ids.append(each_id)
			movie_title = Movie.objects.filter(movie_id=each_id).first().title 
			movie_titles.append(movie_title)
		zipped = zip(userReviews, movie_titles, movie_ids)
		return render(request, "userprofile.html", {'user': user, 'userReviews': zipped, 'numReviews': numReviews, 
			'dateJoined': dateJoined, 'userSortForm': form, 'titles': movie_titles, 'viewing_own_profile': viewing_own_profile})
    
    #the user to view
	userProfile = user
	movie_titles = []
	movie_ids = []
	numReviews = Review.objects.filter(user_reviewed=userProfile).count()
	#sort by review date initially, desc
	userReviews = Review.objects.filter(user_reviewed=userProfile).order_by('-review_date').all()
	for review in userReviews:
		each_id = review.movie_id 
		movie_ids.append(each_id)
		movie_title = Movie.objects.filter(movie_id=each_id).first().title 
		movie_titles.append(movie_title)
	#the date the user joined
	dateJoined = User.objects.filter(username=user).all()[0].date_joined
	dateJoined = dateJoined.date()
	#return the user's reviews, along with the associated movie titles and ids
	zipped = zip(userReviews, movie_titles, movie_ids)
	return render(request, "userprofile.html", {'user': userProfile, 'userReviews': zipped, 'numReviews': numReviews
		, 'dateJoined': dateJoined, 'userSortForm': UserSortForm()})


#submit a review for a movie
def mySubmitReview(request, movieid):
	if 'username' not in request.session:
		messages.add_message(request, messages.INFO, 'you must be logged in to review this movie.')
		return redirect("myHome")
	if request.method == 'POST':
		form = ReviewForm(request.POST)
		if form.is_valid():
			#see if a review already exists for this movie, for that user
			already_exists = Review.objects.filter(movie_id=movieid, user_reviewed=request.session.get("username", None)).count()
			if already_exists > 0:
				messages.add_message(request, messages.INFO, 'you have already reviewed this movie.')
				return redirect("myReviews", movieid= movieid)
			else:
				#add a new review
				rating = form.cleaned_data['rating']
				title = form.cleaned_data['title']
				content = form.cleaned_data['content']
				user_reviewed = request.session.get("username", None)
				review_id =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
				new_review = Review(title=title, content=content, review_date=datetime.datetime.now(), review_id= review_id, 
					movie_id=movieid, rating=rating, helpfulness=0, number_voted=0, user_reviewed= user_reviewed, users_reviewed={})
				new_review.save()
				messages.add_message(request, messages.INFO, 'your review has been added.')
				return redirect("myReviews", movieid=movieid)
	movie_title = Movie.objects.filter(movie_id=movieid).first().title
	context = {'reviewform': ReviewForm(), 'title': movie_title}
	return render(request, "submitreview.html", context)


#view the signed in user's profile, and be able to delete your account
def myProfile(request):
	if 'username' not in request.session:
		return redirect("myHome")
	if request.is_ajax():
		#delete the user's account
		user_to_delete = request.session.get("username", None)
		User.objects.filter(username=user_to_delete).delete()
		#delete all reviews associated with the user
		Review.objects.filter(user_reviewed=user_to_delete).delete()
		#clear session
		request.session.flush()
		messages.add_message(request, messages.INFO, 'your account has been deleted.')
		return redirect("myHome")
	current_profile = request.session.get("username", None)
	num_reviews = Review.objects.filter(user_reviewed = current_profile).count()
	date_current_user_joined = User.objects.filter(username = current_profile).first().date_joined
	date_current_user_joined = date_current_user_joined.replace(tzinfo=None)
	since_joined = str((datetime.datetime.now() - date_current_user_joined).days) + ' ' + 'days'
	days_joined = (datetime.datetime.now() - date_current_user_joined).days
	if days_joined > 30 and days_joined < 365:
		since_joined = str(((datetime.datetime.now() - date_current_user_joined).days)/(30.25)) + ' ' + 'months'
	if days_joined >= 365:
		since_joined = str(((datetime.datetime.now() - date_current_user_joined).days)/(365.25)) + ' ' + 'years'
	number_reviews = Review.objects.filter(user_reviewed=request.session.get("username", None)).count()
	context = {'user': current_profile, 'num_reviews': num_reviews, 'date_joined': date_current_user_joined, 
	 'since_joined': since_joined, 'number_reviews': number_reviews}
	return render(request, "myprofile.html", context)


def myLogout(request):
	#logout the user
	request.session.flush()
	return redirect('myHome')
