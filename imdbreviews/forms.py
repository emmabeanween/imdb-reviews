from django import forms

class SortForm(forms.Form):
	sort = forms.ChoiceField(choices=[  ('helpfulness', 'helpfulness'), ('reviewdate', 'review date'),
		('rating', 'rating'), ('totalvotes', 'total votes')], widget=forms.Select(attrs={'onchange': 'this.form.submit();'})) 
	rating = forms.ChoiceField(choices=[('showall', 'show all'), ('1', '1 star'), ('2', '2 stars'), ('3', '3 stars'), ('4', '4 stars'), ('5', '5 stars')
		, ('6', '6 stars'), ('7', '7 stars'), ('8', '8 stars'), ('9', '9 stars'), ('10', '10 stars')], widget=forms.Select(attrs = {'onchange': 'this.form.submit();'}))
	direction = forms.ChoiceField(choices=[('asc', 'asc'), ('desc', 'desc')], initial='desc', widget=forms.RadioSelect(attrs = {
		'onchange': 'this.form.submit();'}))


class UserSortForm(forms.Form):
	sort = forms.ChoiceField(choices=[  ('reviewdate', 'review date'), ('helpfulness', 'helpfulness'),
		('rating', 'rating'), ('totalvotes', 'total votes')], widget=forms.Select(attrs={'onchange': 'this.form.submit();'})) 
	direction = forms.ChoiceField(choices=[('asc', 'asc'), ('desc', 'desc')], initial='desc', widget=forms.RadioSelect(attrs={'onchange':
		'this.form.submit();'}))


class RegisterForm(forms.Form):
	username = forms.CharField(max_length=100, required=True)
	password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput())
	confirmedpassword = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput())


class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput())


class ReviewForm(forms.Form):
	title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'review title...', 'class': 'form-control'}))
	content = forms.CharField(
                    widget=forms.Textarea(attrs={'placeholder': 'write your review here...', 'class': 'form-control'}))
	rating = forms.ChoiceField(choices=[('1', '1 star'), ('2', '2 stars'), ('3', '3 stars'), ('4', '4 stars'),
	 ('5', '5 stars'), ('6', '6 stars'), ('7', '7 stars'), ('8', '8 stars'), ('9', '9 stars'), ('10', '10 stars')])