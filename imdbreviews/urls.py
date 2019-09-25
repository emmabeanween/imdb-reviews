
from django.contrib import admin
from django.urls import path, include
from imdbreviews.views import myHome, mySearch, myTitle, myReviews, myAuth, myProfile, userProfile, myLogout, mySubmitReview


urlpatterns = [

    path('admin/', admin.site.urls),
    path('home/', myHome, name = "myHome"),
    path("myprofile/", myProfile, name="myProfile"),
    path('userprofile/<str:user>', userProfile, name='userProfile'),
    path('search/', mySearch, name = 'mySearch'),
    path('title/<str:movieid>', myTitle, name='myTitle'),
    path('title/<str:movieid>/reviews', myReviews, name='myReviews'),
    path('title/<str:movieid>/submitreview', mySubmitReview, name='mySubmitReview'),
    path('logout/', myLogout, name = 'myLogout'),
    path('signupandlogin/', myAuth, name='myAuth')

]

