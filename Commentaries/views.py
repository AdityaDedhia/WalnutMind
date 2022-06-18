from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import ListView,DetailView
from .models import Post
from django.http import Http404, JsonResponse
from django.contrib import messages
from .forms import PostForm

from taggit.models import Tag
from .serializers import CommentarySerializer
from rest_framework.generics import ListAPIView

class booksView(ListView):
    model = Post
    template_name = 'Commentaries/index.html'
    def get_context_data(self, *args, **kwargs):
        context = super(booksView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all() #return all tags
        context['tags'] = tags
        return context


class BookListAPIView(ListAPIView):
    queryset = Post.objects.filter(public = True)
    serializer_class = CommentarySerializer


class bookView(DetailView):
    model = Post
    slug_url_kwarg = 'pk_slug'
    template_name = 'Commentaries/book.html'

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
def post_json(request):
    data = list(Post.objects.values())
    return JsonResponse(data, safe = False)

@login_required(login_url='/users/login')
def newPostView(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES) #Requires both request.Files, else will be left blank.
            if form.is_valid():
                form.instance.publisher = request.user #Because author field from forms.py was excluded
                form.save()
                messages.success(request, ("Commentary is successfully published!"))
                latest_id = Post.objects.latest('pk').pk #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
                return redirect(f"/books/{latest_id}")
        else:
            form = PostForm()
        return render(request, 'Commentaries/post.html', {
                'form': form
            })