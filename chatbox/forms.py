from django import forms


class NewChatMessageForm(forms.Form):
    """A minimal form for posting a chat message."""
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Type your message..."}),
        label="Message",
    )
