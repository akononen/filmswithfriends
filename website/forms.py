from django import forms

from website.models import MovieRating

#class AddFriendForm(forms.Form):
#    def __init__(self, *args, **kwargs):
#        self.fieds["friend_username"].required = True
#
#    friend_username = forms.CharField(label="friend_username", max_length=100)

class RateMovieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RateMovieForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["rating"].required = True

    class Meta:
        model = MovieRating
        fields = ["title", "rating"]
