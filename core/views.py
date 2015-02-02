from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, ListView, UpdateView, CreateView

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

from core.models import Whitelist
from lessons.models import PbllPage
from .forms import HonorCodeForm



class HonorCodeFormView(FormView):
    template_name = 'inactive.html'
    form_class = HonorCodeForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if form.cleaned_data['honor_agreement']:
        	whitelister = Whitelist.objects.get(email_addr=self.request.user.email)
        	whitelister.honor_agreement = True
        	whitelister.save()
        else:
        	return redirect('home')

        return super(HonorCodeFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(HonorCodeFormView, self).get_context_data(**kwargs)
        context['pbllpage'] = PbllPage.objects.get(slug='honor-agreement')
        return context

class ParticipantListView(LoginRequiredMixin, StaffuserRequiredMixin, ListView):
    template_name = 'participants.html'
    model = Whitelist

    def get_context_data(self, **kwargs):
        context = super(ParticipantListView, self).get_context_data(**kwargs)
        context['object_list'] = context['object_list'].order_by('participant_type', 'email_addr')  #self.get_queryset()
        
        return context

class ParticipantCreateView(LoginRequiredMixin, StaffuserRequiredMixin, CreateView):
    model = Whitelist
    template_name = 'create_form.html'
    fields =['email_addr', 'participant_type']
    success_url = reverse_lazy('participants')


class ParticipantUpdateView(LoginRequiredMixin, StaffuserRequiredMixin, UpdateView):
    model = Whitelist
    template_name = 'edit_form.html'
    fields =['email_addr', 'participant_type']
    success_url = reverse_lazy('participants')


