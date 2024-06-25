from django import forms

class CreatorHandleForm(forms.Form):
    creators_handle = forms.CharField(label='',max_length=100,widget=forms.TextInput(attrs={'placeholder':"Handle Without '@'","id":'creators_handle'}))
