from urllib import response
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime, timedelta, date
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from Users.models import Profile
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView
from .forms import PostForm, CommentForm
from django.urls import reverse
from bootstrap_modal_forms.generic import BSModalDeleteView
from django.urls import reverse_lazy

from taggit.models import Tag
from .serializers import ArticleSerializer
from rest_framework.generics import ListAPIView

def indexView(request):


    #fix does not work atm
    today = datetime.today()
    one_week_ago = datetime.today() - timedelta(days=7)

    recentArticles = Post.objects.filter(dateCreated__range = [today, one_week_ago])

    recent = Post.objects.all()

    tags = Tag.objects.all() #return all tags
    return render(request, 'Articles/index.html', {
        'recent': recent, 'tags': tags
    })

def aboutView(request):
    return render(request, 'Articles/about.html')

def opportunitiesView(request):
    return render(request, 'Articles/opportunities.html')

def contactView(request):
    return render(request, 'Articles/contact.html')

def roadmapView(request):
    return render(request, 'Articles/roadmap.html')

def privacyView(request):
    return render(request, 'Articles/privacy.html')

def termsView(request):
    return render(request, 'Articles/terms.html')

def faqView(request):
    return render(request, 'Articles/faq.html')

#ARTICLE VIEWS-------------------

class searchView(ListView):
    model = Post
    template_name = 'Articles/alpine.html'
    def get_context_data(self, *args, **kwargs):
        context = super(searchView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all() #return all tags
        context['tags'] = tags
        return context

class ArticleListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = ArticleSerializer

class articleView(DetailView):
    model = Post
    slug_url_kwarg = 'pk_slug'
    template_name = 'Articles/article.html'


    def get_object(self, queryset = None):
        if queryset is None:
            queryset = self.get_queryset()

        pk_slug = self.kwargs.get(self.slug_url_kwarg)

        if pk_slug is not None and pk_slug.isdigit():
            queryset = queryset.filter(pk=pk_slug)
        
        elif pk_slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: pk_slug})

        
        if pk_slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with an object "
                "pk_slug in the URLconf." % self.__class__.__name__
            )

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


#A version of binary like/dislike implementation: does not work

@login_required(login_url='/users/login')
def articleupvote(request, pk):
    post = get_object_or_404(Post, id = pk)
    post.likes.add(request.user)
    messages.success(request, ("Rating saved, thank you for your feedback."))
    return HttpResponseRedirect(reverse('articleview', args =[str(pk)]))

@login_required(login_url='/users/login')
def articledownvote(request, pk):
    post = get_object_or_404(Post, id = pk)
    post.dislikes.add(request.user)
    messages.success(request, ("Rating saved, thank you for your feedback."))
    return HttpResponseRedirect(reverse('articleview', args =[str(pk)]))

#---------------------------------------------------------------------------------
  
@login_required(login_url='/users/login')
def newPostView(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES) #Requires both request.Files, else will be left blank.
            if form.is_valid():
                form.instance.author = request.user #Because author field from forms.py was excluded
                form.save()
                messages.success(request, ("Article is successfully published!"))
                latest_id = Post.objects.latest('pk').pk #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
                return redirect(f"/articles/{latest_id}")
        else:
            form = PostForm()
        return render(request, 'Articles/post.html', {
                'form': form
            })

@login_required(login_url='/users/login')
def newCommentView(request, pk):
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                post = Post.objects.get(pk=pk),
                content = form.cleaned_data['content'],
                author = request.user,
                dateCreated = date.today(),
                dateUpdated = date.today(),
            )
            comment.save()
            return HttpResponseRedirect(reverse('articleview', args =[str(pk)]))

        else:
            return render(request, "Articles/article.html")
    return render(request, "Articles/article.html")

class updatePostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'Articles/updatepost.html'

class deletePostView(BSModalDeleteView):
    model = Post
    template_name = 'Articles/deletepost.html'
    success_message = 'Post was successfully deleted.'
    success_url = reverse_lazy('index')