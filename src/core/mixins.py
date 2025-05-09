from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import CheckboxInput


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs') and not isinstance(field.widget, CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class OwnerOrSuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.owner or self.request.user.is_superuser


class SenderOrSuperuserMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.ad_sender.owner or self.request.user.is_superuser
