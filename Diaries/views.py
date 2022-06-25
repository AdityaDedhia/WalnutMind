from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView
from .models import Post
from .forms import PostForm
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from Users.models import Log
from taggit.models import Tag

class diariesView(ListView):
    model = Post
    template_name = 'Diaries/index.html'

class diaryView(DetailView):
    model = Post
    slug_url_kwarg = 'pk_slug'
    template_name = 'Diaries/diary.html'

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

@login_required(login_url='/users/login')
def newPostView(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES) #Requires both request.Files, else will be left blank.
            if form.is_valid():
                form.instance.author = request.user #Because author field from forms.py was excluded
                title = form.instance.title
                form.save()
                username = str(request.user)
                print(username)
                messages.success(request, ("Blog entry is successfully published!"))
                post_slug = Post.objects.latest('pk').slug #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
                link = f"https://www.walnutmind.org/blogs/{username}/{post_slug}"
                description = f"Published blog post: {title}"
                logitem = Log(
                    user = request.user,
                    description =description,
                    link = link,
                    datelog = datetime.now()
                )
                logitem.save()
                return HttpResponseRedirect(reverse('blogview', args =[username,str(post_slug)]))
        else:
            form = PostForm()
        return render(request, 'Diaries/post.html', {
                'form': form
            })
        
class updatePostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'Diaries/updatepost.html'

    def get_context_data(self, *args, **kwargs):
        context = super(updatePostView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all() #return all tags
        context['tags'] = tags
        return context