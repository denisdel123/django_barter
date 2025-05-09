from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.urls import reverse_lazy
from django.views import generic
import ads.models as ads_models
import ads.forms as ads_forms
import core.enums
from core import mixins
from django.shortcuts import render, get_object_or_404, redirect


def main(request):
    return render(request, 'ads/main.html')


class AdsCreateView(LoginRequiredMixin, generic.CreateView):
    model = ads_models.Ads
    form_class = ads_forms.AdsCreateForm
    template_name = 'ads/ads_form.html'
    success_url = reverse_lazy('ads:ads-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AdsListView(LoginRequiredMixin, generic.ListView):
    model = ads_models.Ads
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ads_models.Category.objects.all()
        context['condition'] = core.enums.ConditionEnums.choices
        return context


class AdsUpdateView(LoginRequiredMixin, mixins.OwnerOrSuperuserRequiredMixin, generic.UpdateView):
    model = ads_models.Ads
    form_class = ads_forms.AdsCreateForm
    template_name = 'ads/ads_form.html'
    success_url = reverse_lazy('ads:ads-list')


class AdsDeleteView(LoginRequiredMixin, mixins.OwnerOrSuperuserRequiredMixin, generic.DeleteView):
    model = ads_models.Ads
    success_url = reverse_lazy("ads:ads-list")


class ExchangeProposalCreateView(LoginRequiredMixin, generic.CreateView):
    model = ads_models.ExchangeProposal
    form_class = ads_forms.ExchangeProposalForm
    template_name = 'ads/ads_form.html'
    success_url = reverse_lazy('ads:ads-list')

    def dispatch(self, request, *args, **kwargs):
        try:
            self.ad_receiver = ads_models.Ads.objects.get(pk=kwargs['pk'])
        except ads_models.Ads.DoesNotExist:
            raise Http404("Ad not found")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # ❗ Проверка на попытку обмена своим же объявлением
        if self.ad_receiver.owner == self.request.user:
            form.add_error(None, "Нельзя обменивать свои собственные объявления.")
            return self.form_invalid(form)

        form.instance.ad_receiver = self.ad_receiver
        return super().form_valid(form)


class ExchangeProposalListView(LoginRequiredMixin, generic.ListView):
    model = ads_models.ExchangeProposal
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {}

        status = self.request.GET.get("status")
        ad_sender = self.request.GET.get("ad_sender")
        ad_receiver = self.request.GET.get("ad_receiver")

        if status:
            filters["status"] = status
        if ad_sender:
            filters["ad_sender_id"] = ad_sender
        if ad_receiver:
            filters["ad_receiver_id"] = ad_receiver

        return queryset.filter(**filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["statuses"] = core.enums.StatusEnums.choices

        context["ad_receivers"] = ads_models.ExchangeProposal.objects.filter(ad_sender__owner=user)  # кому я отправил
        context["ad_senders"] = ads_models.ExchangeProposal.objects.filter(ad_receiver__owner=user)  # кто мне отправил

        return context


class ExchangeProposalDeleteView(LoginRequiredMixin, mixins.SenderOrSuperuserMixin, generic.DeleteView):
    model = ads_models.ExchangeProposal
    template_name = "ads/ads_confirm_delete.html"
    success_url = reverse_lazy("ads:offer-list")
    raise_exception = True


@login_required
def exchange_proposal_accept(request, pk):
    proposal = get_object_or_404(ads_models.ExchangeProposal, pk=pk)
    proposal.status = core.enums.StatusEnums.ACCEPTED
    proposal.save()
    return redirect("ads:offer-list")


@login_required
def exchange_proposal_reject(request, pk):
    proposal = get_object_or_404(ads_models.ExchangeProposal, pk=pk)
    proposal.status = core.enums.StatusEnums.REJECTED
    proposal.save()
    return redirect("ads:offer-list")
