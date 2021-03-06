from django import forms

from .models import Referral


class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = [
            "requester",
            "requester_email",
            "requester_phone_number",
            "subject",
            "question",
            "urgency",
            "urgency_explanation",
            "context",
            "prior_work",
        ]

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )
