from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import UpdateView
from hitcount.views import HitCountDetailView
from rest_framework.generics import ListAPIView
from taggit.models import Tag

from Blog.utils import profanity_filter
from Users.models import Profile, Log, Infraction
from Users.serializers import ProfileSerializer
from .forms import PostForm
from .models import Post, Comment


def diariesView(request):
    recents = Post.objects.filter(public=True).order_by('-dateCreated')[:5]
    profiles = Profile.objects.filter(is_public=True)

    tags = Tag.objects.all()  # Return all tags

    return render(
        request, 'Diaries/index.html', {
            'profiles': profiles, 'tags': tags, 'recents': recents
        }
    )

class diaryView(HitCountDetailView):
    model = Post
    slug_url_kwarg = 'pk_slug'
    template_name = 'Diaries/diary.html'
    count_hit = True

    def get_context_data(self, *args, **kwargs):
        context = super(diaryView, self).get_context_data(*args, **kwargs)
        relatedBlogs = Post.objects.filter(title__search=self.object.tags)

        context['relatedBlogs'] = relatedBlogs
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


class ProfileListAPIView(ListAPIView):
    queryset = Profile.objects.filter(is_public = True)
    serializer_class = ProfileSerializer

@login_required(login_url='/users/login')
def newPostView(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)  # Requires both request.Files, else will
            # be left blank.
            if form.is_valid():
                form.instance.author = request.user  # Because author field from forms.py was
                # excluded
                title = form.instance.title
                form.save()
                username = str(request.user)
                print(username)
                messages.success(request, ("Blog entry is successfully published!"))
                post_slug = Post.objects.latest('pk').slug  # Essentially gets latest entry object
                # based on last pk added, and then gets the pk of that entry object.
                link = f"https://www.walnutmind.org/blogs/{username}/{post_slug}"
                description = f"Published blog post: {title}"
                logitem = Log(
                    user=request.user,
                    description=description,
                    link=link,
                    datelog=datetime.now()
                )
                logitem.save()
                return HttpResponseRedirect(reverse('blogview', args=[username, str(post_slug)]))
        else:
            form = PostForm()
        return render(request, 'Diaries/post.html', {
                'form': form
            })

#---------------------------------------------------------------------------------
@login_required(login_url='/users/login')
def diarysave(request, username, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.saves.all():
        post.saves.remove(request.user)
        messages.debug(request, ("Blog post removed from your list."))
        return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))

    post.saves.add(request.user)
    link = f"https://www.walnutmind.org/blogs/{username}/{post.slug}"
    description = f"Saved blog post: {post.title}"
    logitem = Log(
        user = request.user,
        description =description,
        link = link,
        datelog = datetime.now()
    )
    logitem.save()
    messages.debug(request, ("Blog post saved to your list."))
    return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))

@login_required(login_url='/users/login')
def diaryupvote(request, username, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.debug(request, ("Blog post unliked."))
        return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))
    post.likes.add(request.user)
    link = f"https://www.walnutmind.org/blogs/{username}/{post.slug}"
    description = f"Liked blog post: {post.title}"
    logitem = Log(
        user=request.user,
        description=description,
        link=link,
        datelog=datetime.now()
    )
    logitem.save()
    messages.debug(request, ("Blog post liked, thank you for your feedback."))
    return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))

#---------------------------------------------------------------------------------
@login_required(login_url='/users/login')
def newCommentView(request, username, pk):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = Post.objects.get(pk=pk)

        if profanity_filter(content) == True:
            messages.error(
                request, ("Your comment could not be posted, please refrain from "
                          "the "
                          "use of explicit language.")
            )
            Infraction.objects.create(
                user=request.user,
                reason=f"Used explicit language in blog post ID {pk} with the comment: {content}",
                datelog=datetime.now()
            )
            return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))

        comment = Comment.objects.create(
            post=post,
            content=content,
            author=request.user,
            dateCreated=date.today(),
            dateUpdated=date.today(),
        )
        comment.save()
        title = post.title
        post_slug = post.slug
        link = f"https://www.walnutmind.org/blogs/{username}/{post_slug}"
        description = f"Posted comment on '{title}'"
        logitem = Log(
            user=request.user,
            description=description,
            link=link,
            datelog=datetime.now()
        )
        logitem.save()
        return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))
    return render(request, "Diaries/book.html")


@login_required(login_url='/users/login')
def deleteCommentView(request, username, pk, id):
    comment = Comment.objects.get(pk=id)
    post = Post.objects.get(pk=pk)

    if request.user == comment.author and comment.post == post: #IF AND ONLY IF user is the author of the comment, and the post is the same as the comment's post, then delete the comment.
        comment.delete()
        messages.debug(request, ("Comment succesfully deleted."))
        return HttpResponseRedirect(reverse('blogview', args=[username, str(post.slug)]))
    else:
        messages.error(request, ("An unknown error occured attempting to delete your comment."))
        return HttpResponseRedirect(reverse('blogindex'))


class updatePostView(UpdateView):
    login_required = True
    model = Post
    form_class = PostForm
    template_name = 'Diaries/updatepost.html'

    def get_context_data(self, *args, **kwargs):
        context = super(updatePostView, self).get_context_data(*args, **kwargs)
        tags = Tag.objects.all()
        context['tags'] = tags
        return context
