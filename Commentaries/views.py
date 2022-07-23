from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.views.generic import ListView, UpdateView
from Blog.utils import profanity_filter
from .models import Post, Comment
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.contrib import messages
from django.conf import settings
from .forms import PostForm
from Users.models import Log, Infraction
from isbnlib import is_isbn13
from django.urls import reverse
import readtime
from datetime import datetime, date
from taggit.models import Tag
from .serializers import CommentarySerializer
from rest_framework.generics import ListAPIView
from hitcount.views import HitCountDetailView

class booksView(ListView):
    model = Post
    template_name = 'Commentaries/index.html'
    def get_context_data(self, *args, **kwargs):
        context = super(booksView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all() #return all tags
        context['tags'] = tags
        return context

    def dispatch(self, request, *args, **kwargs):
        #additional code before the view is called
        return super(booksView, self).dispatch(request, *args, **kwargs)


class BookListAPIView(ListAPIView):
    queryset = Post.objects.filter(public = True)
    serializer_class = CommentarySerializer


class bookView(HitCountDetailView):
    model = Post
    slug_url_kwarg = 'pk_slug'
    template_name = 'Commentaries/book.html'
    count_hit = True
    def get_context_data(self, *args, **kwargs):
        context = super(bookView, self).get_context_data(*args, **kwargs)
        content = self.object.content
        readEST = readtime.of_text(content).minutes + 4 #Get reading time of text.

        # FOR ANONYMOUS USERS CHECK PUBSLEFT
        if not self.request.user.is_authenticated: 
            if 'pubs_remaining' in self.request.session:
                if self.request.session['pubs_remaining'] >= 0:
                    self.request.session['pubs_remaining'] -= 1
            else:
                self.request.session['pubs_remaining'] = settings.PUBS_ACCESS
                pubs_left = settings.PUBS_ACCESS
            pubs_left = self.request.session['pubs_remaining']
            context['pubs_left'] = pubs_left
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
        #additional code before view is called.
        return super(bookView, self).dispatch(request, *args, **kwargs)

def post_json(request):
    data = list(Post.objects.values('content'))
    return JsonResponse(data, safe = False)

#---------------------------------------------------------------------------------
@login_required(login_url='/users/login')
def commentarysave(request, pk):
    post = get_object_or_404(Post, id = pk)
    if request.user in post.saves.all():
        post.saves.remove(request.user)
        messages.success(request, ("Commentary removed from your list."))
        return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))

    post.saves.add(request.user)
    link = f"https://www.walnutmind.org/books/{post.slug}"
    description = f"Saved commentary: {post.title}"
    logitem = Log(
        user = request.user,
        description =description,
        link = link,
        datelog = datetime.now()
    )
    logitem.save()
    messages.success(request, ("Commentary saved to your list."))
    return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))

@login_required(login_url='/users/login')
def commentaryupvote(request, pk):
    post = get_object_or_404(Post, id = pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.success(request, ("Commentary unliked."))
        return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))
    post.likes.add(request.user)
    link = f"https://www.walnutmind.org/books/{post.slug}"
    description = f"Liked commentary: {post.title}"
    logitem = Log(
        user = request.user,
        description = description,
        link = link,
        datelog = datetime.now()
    )
    logitem.save()
    messages.success(request, ("Commentary liked, thank you for your feedback."))
    return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))

#---------------------------------------------------------------------------------

@login_required(login_url='/users/login')
def newCommentView(request, pk):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = Post.objects.get(pk=pk)

        if profanity_filter(content) == True:
                messages.success(request, ("Your comment could not be posted, please refrain from the use of explicit language."))
                Infraction.objects.create(
                    user = request.user,
                    reason = f"Used explicit language in commentary ID {pk} with the comment: {content}",
                    datelog = datetime.now()
                )
                return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))
                
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
        link = f"https://www.walnutmind.org/books/{post_slug}"
        description = f"Posted comment on '{title}'"
        logitem = Log(
            user = request.user,
            description =description,
            link = link,
            datelog = datetime.now()
        )
        logitem.save()
        return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))
    return render(request, "Commentaries/book.html")

@login_required(login_url='/users/login')
def deleteCommentView(request, pk, id):
    comment = Comment.objects.get(pk=id)
    post = Post.objects.get(pk=pk)
    if request.user == comment.author and comment.post == post: #IF AND ONLY IF user is the author of the comment, and the post is the same as the comment's post, then delete the comment.
        comment.delete()
        messages.success(request, ("Comment succesfully deleted."))
        return HttpResponseRedirect(reverse('bookview', args =[str(post.slug)]))
    else:
        messages.success(request, ("An unknown error occured attempting to delete your comment."))
        return HttpResponseRedirect(reverse('bookindex'))

@login_required(login_url='/users/login')
def newPostView(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES) #Requires both request.Files, else will be left blank.
            if form.is_valid():
                form.instance.publisher = request.user #Because author field from forms.py was excluded
                title = form.instance.title
                isbnfield = form.instance.isbn
                if isbnfield:
                    if not is_isbn13(isbnfield):
                        isbnfield = None
                form.save()
                messages.success(request, ("Commentary is successfully published!"))
                post_slug = Post.objects.latest('pk').slug #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
                link = f"https://www.walnutmind.org/books/{post_slug}"
                description = f"Published new commentary: {title}"
                logitem = Log(
                    user = request.user,
                    description =description,
                    link = link,
                    datelog = datetime.now()
                )
                logitem.save()
                return HttpResponseRedirect(reverse('bookview', args =[str(post_slug)]))
        else:
            form = PostForm()
        return render(request, 'Commentaries/post.html', {
                'form': form
            })
class updatePostView(UpdateView):
    login_required = True
    model = Post
    form_class = PostForm
    template_name = 'Commentaries/updatepost.html'