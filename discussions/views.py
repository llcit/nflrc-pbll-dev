from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView, FormView, View
from django.core.urlresolvers import reverse

from braces.views import CsrfExemptMixin, JSONResponseMixin, AjaxResponseMixin, LoginRequiredMixin, StaffuserRequiredMixin

from .models import Post
from .forms import PostForm, PostReplyForm
from lessons.models import LessonDiscussion
from core.mixins import HonorCodeRequired


class DiscussionListView(LoginRequiredMixin, HonorCodeRequired, TemplateView):
    template_name = 'discussions_index.html'

    def get_context_data(self, **kwargs):
        context = super(DiscussionListView, self).get_context_data(**kwargs)
        headers = Post.objects.filter(parent_post=None).order_by('-modified')
        threads = []

        for hdr in headers:
           
            try:
                lesson = LessonDiscussion.objects.get(thread=hdr).lesson
            except:
                lesson = None
            
            threads.append({'lesson': lesson, 'header': hdr, 'reply_count': hdr.replies.count()})

        context['threads'] = threads
        return context


class DiscussionView(LoginRequiredMixin, HonorCodeRequired, DetailView):
    model = Post
    template_name = 'discussions.html'
    
    def get_context_data(self, **kwargs):
        context = super(DiscussionView, self).get_context_data(**kwargs)
        initial_post_data = {}
        initial_post_data['creator'] = self.request.user
        thread_post = self.get_object()
        
        try:
            lesson = LessonDiscussion.objects.get(thread=thread_post).lesson
        except:
            lesson = None

        replies = thread_post.replies.all().filter(deleted=False).order_by('-created')
        initial_post_data['subject'] = 'Re: %s'% thread_post.subject
        initial_post_data['parent_post'] = thread_post.id  
        form = PostReplyForm(initial=initial_post_data)
        # form = self.get_form(self.get_form_class())

        context['thread'] = thread_post
        context['thread_list'] = Post.objects.filter(parent_post=None).order_by('created')
        context['lesson'] = lesson
        context['replies'] = replies
        context['postform'] = form

        return context

class PostView(LoginRequiredMixin, HonorCodeRequired, ListView):
    model = Post
    template_name = 'post.html'

class PostUpdateView(LoginRequiredMixin, HonorCodeRequired, CsrfExemptMixin, UpdateView):
    model = Post
    form_class= PostReplyForm
    template_name = 'edit_form.html'


    def get_form_class(self):
        form_class = super(PostUpdateView, self).get_form_class()
        if self.request.user.is_staff:
            form_class = PostForm
        return form_class

    def get_success_url(self):
        if self.get_object().parent_post:
            return reverse('discussion_select', args=[str(self.get_object().parent_post.slug)])
        return reverse('discussion_select', args=[str(self.get_object().slug)])
    

class PostCreateView(LoginRequiredMixin, HonorCodeRequired, CsrfExemptMixin, JSONResponseMixin, AjaxResponseMixin, CreateView):
    model = Post
    template_name = 'discussions.html'
    form_class= PostReplyForm

    def post_ajax(self, request, *args, **kwargs):
        postform = PostReplyForm(request.POST)
        print postform
        if postform.is_valid():

            new_post = postform.save()
            data = {}
            data['id'] = new_post.id
            data['modified'] = new_post.modified.strftime('%b %d %Y %H:%M')
            data['text'] = new_post.text
            data['creator'] = new_post.creator.username
            data['subject'] = new_post.subject

            # print self.render_json_response(data)
            return self.render_json_response(data)
        else:
            data = postform.errors
            print 'Errors?' , data
            return self.render_json_response(data)

class PostDeleteView(LoginRequiredMixin, HonorCodeRequired, CsrfExemptMixin, JSONResponseMixin, AjaxResponseMixin, View):
   
    def post_ajax(self, request, *args, **kwargs):
        if request:
            try:
                post = Post.objects.get(id=request.POST['post'])
                
                if post.creator == request.user or request.user.is_staff:
                    post.deleted = True
                    post.save()
                    data = 'data removed'
                    return self.render_json_response(data)
                else:
                    data = 'data not removed'

            except Exception as e:
                data = 'data not removed'
                print 'Error: ', e
        
        return self.render_json_response(data) 


