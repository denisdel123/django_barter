from django import forms
import ads.models as ads_models
from core import mixins


class AdsCreateForm(mixins.StyleFormMixin, forms.ModelForm):
    class Meta:
        model = ads_models.Ads
        fields = (
            "title",
            "description",
            "image_url",
            "category",
            "condition",
        )


class ExchangeProposalForm(mixins.StyleFormMixin, forms.ModelForm):
    class Meta:
        model = ads_models.ExchangeProposal
        fields = ("ad_sender", "comment")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['ad_sender'].queryset = ads_models.Ads.objects.filter(owner=user)
