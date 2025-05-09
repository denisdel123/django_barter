from django.urls import path

from ads.apps import AdsConfig
from ads import views as ads_views

app_name = AdsConfig.name

urlpatterns = [
    path('', ads_views.main, name='main'),
    path('create/', ads_views.AdsCreateView.as_view(), name='ads-create'),
    path('list/', ads_views.AdsListView.as_view(), name='ads-list'),
    path('update/<int:pk>/', ads_views.AdsUpdateView.as_view(), name='ads-update'),
    path('delete/<int:pk>/', ads_views.AdsDeleteView.as_view(), name='ads-delete'),

    path('offer/create/<int:pk>/', ads_views.ExchangeProposalCreateView.as_view(), name='offer-create'),
    path('offer/list/', ads_views.ExchangeProposalListView.as_view(), name='offer-list'),
    path('offer/accept/<int:pk>/', ads_views.exchange_proposal_accept, name='offer-accept'),
    path('offer/reject/<int:pk>/', ads_views.exchange_proposal_reject, name='offer-reject'),
    path('offer/delete/<int:pk>/', ads_views.ExchangeProposalDeleteView.as_view(), name='offer-delete'),
]