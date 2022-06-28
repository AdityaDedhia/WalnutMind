from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView
from .forms import PostForm
from django.urls import reverse
from Users.models import Blacklist, Log
from taggit.models import Tag
from .serializers import ArticleSerializer
from rest_framework.generics import ListAPIView
from django.contrib.auth import logout
import readtime


def indexView(request):
    #GET USER LOCATION and RUN through Blacklisted IPs.
    x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forw_for is not None:
        ip = x_forw_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    if Blacklist.objects.filter(ip = ip):
        logout(request)
        return render(request, "blacklist.html")

    recent = Post.objects.filter(public = True).order_by('-dateCreated')[:5] #Get last 5 entries
    tags = Tag.objects.all() #return all tags

    if request.user.is_authenticated: #Send custom feed to logged in users:
        user = request.user
        saved_articles = user.article_saves.all()
        saved_commentaries = user.commentary_saves.all()
    else:
        saved_articles = None
        saved_commentaries = None

    return render(request, 'Articles/index.html', {
        'recent': recent, 'tags': tags, 'saved_articles': saved_articles, 'saved_commentaries': saved_commentaries
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

class searchView(ListView):
    model = Post
    template_name = 'Articles/alpine.html'
    def get_context_data(self, *args, **kwargs):
        context = super(searchView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all() #return all tags
        context['tags'] = tags
        return context

    def dispatch(self, request, *args, **kwargs):
        #GET USER LOCATION and RUN through Blacklisted IPs.
        x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forw_for is not None:
            ip = x_forw_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if Blacklist.objects.filter(ip = ip):
            logout(request)
            return render(request, "blacklist.html")
        return super(searchView, self).dispatch(request, *args, **kwargs)

class ArticleListAPIView(ListAPIView):
    queryset = Post.objects.filter(public = True)
    serializer_class = ArticleSerializer

class articleView(DetailView):
    model = Post
    slug_url_kwarg = 'pk_slug'
    template_name = 'Articles/article.html'

    def get_context_data(self, *args, **kwargs):
        context = super(articleView, self).get_context_data(*args, **kwargs)
        content = self.object.content
        readEST = readtime.of_text(content).minutes + 1 #Get reading time of text.
        context['readEST'] = readEST
        return context

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

    def dispatch(self, request, *args, **kwargs):
        #GET USER LOCATION and RUN through Blacklisted IPs.
        x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forw_for is not None:
            ip = x_forw_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if Blacklist.objects.filter(ip = ip):
            logout(request)
            return render(request, "blacklist.html")
        return super(articleView, self).dispatch(request, *args, **kwargs)


@login_required(login_url='/users/login')
def articlesave(request, pk):
    post = get_object_or_404(Post, id = pk)
    if request.user in post.saves.all():
        post.saves.remove(request.user)
        messages.success(request, ("Article removed from your list."))
        return HttpResponseRedirect(reverse('articleview', args =[str(post.slug)]))

    post.saves.add(request.user)
    link = f"https://www.walnutmind.org/articles/{post.slug}"
    description = f"Saved article: {post.title}"
    logitem = Log(
        user = request.user,
        description =description,
        link = link,
        datelog = datetime.now()
    )
    logitem.save()
    messages.success(request, ("Article saved to your list."))
    return HttpResponseRedirect(reverse('articleview', args =[str(post.slug)]))

@login_required(login_url='/users/login')
def articleupvote(request, pk):
    post = get_object_or_404(Post, id = pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.success(request, ("Article unliked."))
        return HttpResponseRedirect(reverse('articleview', args =[str(post.slug)]))
    post.likes.add(request.user)
    link = f"https://www.walnutmind.org/articles/{post.slug}"
    description = f"Liked article: {post.title}"
    logitem = Log(
        user = request.user,
        description =description,
        link = link,
        datelog = datetime.now()
    )
    logitem.save()
    messages.success(request, ("Article liked, thank you for your feedback."))
    return HttpResponseRedirect(reverse('articleview', args =[str(post.slug)]))

#---------------------------------------------------------------------------------  
@login_required(login_url='/users/login')
def newPostView(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES) #Requires both request.Files, else will be left blank.
            if form.is_valid():
                form.instance.author = request.user #Because author field from forms.py was excluded
                title = form.instance.title
                form.save()
                messages.success(request, ("Article is successfully published!"))
                post_slug = Post.objects.latest('pk').slug #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
                link = f"https://www.walnutmind.org/articles/{post_slug}"
                description = f"Published article: {title}"
                logitem = Log(
                    user = request.user,
                    description =description,
                    link = link,
                    datelog = datetime.now()
                )
                logitem.save()
                return HttpResponseRedirect(reverse('articleview', args =[str(post_slug)]))
        else:
            form = PostForm()
        return render(request, 'Articles/post.html', {
                'form': form
            })
@login_required(login_url='/users/login')
def newCommentView(request, pk):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = Post.objects.get(pk=pk)

        comment = Comment.objects.create(
            post = post,
            content = content,
            author = request.user,
            dateCreated = date.today(),
            dateUpdated = date.today(),
        )
        comment.save()
        title = post.title
        post_slug = post.slug
        link = f"https://www.walnutmind.org/articles/{post_slug}"
        description = f"Posted comment on '{title}'"
        logitem = Log(
            user = request.user,
            description =description,
            link = link,
            datelog = datetime.now()
        )
        logitem.save()
        return HttpResponseRedirect(reverse('articleview', args =[str(post.slug)]))
    return render(request, "Articles/article.html")

class updatePostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'Articles/updatepost.html'

    def get_context_data(self, *args, **kwargs):
        context = super(updatePostView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all() #return all tags
        context['tags'] = tags
        return context