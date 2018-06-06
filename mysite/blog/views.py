from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, CreateView, DetailView, DeleteView, ListView, UpdateView)


# Create your views here.
class AboutView(TemplateView):
    template_name = "about.html"

class PostListView(ListView):
    model = Post

    #Grabs the Post model and all the objects there and filter out based on those conditions.
    #__lte means lean then or equal it is a Fied Lookup of Django
    def get_queryset(self):
        return Post.objects.filter(publish_date__lte=timezone.now()).order_by('-publish_date')

class PostDetailView(DetailView):
    model = Post


#LoginRequiredMixin is the @login_required decators of class based views
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'  #Where Django will bring the user once a post is made.
    form_class = PostForm

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'  #Where Django will bring the user once a post is updated.
    form_class = PostForm

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list') #Ensures that it runs after the delete command

#List the unpublished Drafts
class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    login_url='/login/'
    redirect_field_name = 'blog/post_draft_list.html'

    def get_queryset(self): #Checks to ensure published_date is empty which means its a draft
        return Post.objects.filter(publish_date__isnull=True).order_by('create_date')

###############################################################################
###############################################################################
#Comment Views Below:
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


#Links up Comments to Post Model
@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form':form})

##Comment Approval
@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

#Comment Removal
@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk= comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)
