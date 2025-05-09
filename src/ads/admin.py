from django.contrib import admin

from ads import models as ads_models

admin.site.register(ads_models.Ads)
admin.site.register(ads_models.Category)
admin.site.register(ads_models.ExchangeProposal)
