from datetime import datetime, date

import readtime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView
from hitcount.views import HitCountDetailView
from ratelimit.decorators import ratelimit
from rest_framework.generics import ListAPIView
from taggit.models import Tag

from Blog.utils import profanity_filter
from Users.models import Log, Infraction, Subscriber
from Users.utils import get_ip, verify_email
from .forms import PostForm
from .models import Post, Comment
from .serializers import ArticleSerializer


def index_view(request):
	recent = Post.objects.filter(public=True).order_by('-dateCreated')[:5]  # Get last 5 entries
	tags = Tag.objects.all()  # Return all tags

	show_subscribe = True

	ip = get_ip(request)
	if Subscriber.objects.filter(ip=ip).exists():
		show_subscribe = False

	if request.user.is_authenticated:  # Send custom feed to logged in users:
		user = request.user
		saved_articles = user.article_saves.all()
		saved_commentaries = user.commentary_saves.all()
		saved_diaries = user.diary_saves.all()

		if Subscriber.objects.filter(user=user).exists():
			show_subscribe = False
	else:
		saved_articles = None
		saved_commentaries = None
		saved_diaries = None

	return render(request, 'Articles/index.html', {
		'recent': recent, 'tags': tags, 'saved_articles': saved_articles,
		'saved_commentaries': saved_commentaries, 'saved_diaries': saved_diaries,
		'show_subscribe': show_subscribe
	})


@ratelimit(key='ip', rate='4/7d', block=True)
def subscribe_view(request):
	if request.method == 'POST':
		email = request.POST.get('email-subscribe')
		ip = get_ip(request)

		if Subscriber.objects.filter(email=email).exists():
			messages.error(request, 'You are already subscribed to our newsletter.')
			return HttpResponseRedirect(reverse('index'))  # Avoid db duplication

		if request.user.is_authenticated:
			user = request.user
			subscriber = Subscriber(user=user, email=email, ip=ip)
			subscriber.save()

		else:
			if not verify_email(email):
				messages.error(
					request, 'An error occurred whilst attempting to verify your email '
					         'address. Please ensure you have entered a valid and '
					         'non-disposable personal email address and try again.'
				)
				return HttpResponseRedirect(reverse('index'))

			subscriber = Subscriber(user=None, email=email, ip=ip)
			subscriber.save()

		messages.success(
			request, 'You have been successfully subscribed to our newsletter. You '
			         'will receive weekly updates on new publications and features '
			         'from authors you follow.'
		)
		return HttpResponseRedirect(reverse('index'))


def about_view(request):
	return render(request, 'Articles/about.html')


def opportunities_view(request):
	return render(request, 'Articles/opportunities.html')


def contact_view(request):
	return render(request, 'Articles/contact.html')


def roadmap_view(request):
	return render(request, 'Articles/roadmap.html')


def privacy_view(request):
	return render(request, 'Articles/privacy.html')


def terms_view(request):
	return render(request, 'Articles/terms.html')


def faq_view(request):
	return render(request, 'Articles/faq.html')


class SearchView(ListView):
	model = Post
	template_name = 'Articles/alpine.html'

	def get_context_data(self, *args, **kwargs):
		context = super(SearchView, self).get_context_data(*args, **kwargs)
		tags = Tag.objects.all()  # return all tags
		context['tags'] = tags
		return context

	def dispatch(self, request, *args, **kwargs):
		# additional code before view is called
		return super(SearchView, self).dispatch(request, *args, **kwargs)


class ArticleListAPIView(ListAPIView):
	queryset = Post.objects.filter(public=True)
	serializer_class = ArticleSerializer


class ArticleView(HitCountDetailView):
	model = Post
	slug_url_kwarg = 'pk_slug'
	template_name = 'Articles/article.html'
	count_hit = True

	def get_context_data(self, *args, **kwargs):
		context = super(ArticleView, self).get_context_data(*args, **kwargs)
		content = self.object.content
		readEST = readtime.of_text(content).minutes + 1  # Get reading time of text.

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

	def get_object(self, queryset=None):
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
		# Additional code before view is called
		return super(ArticleView, self).dispatch(request, *args, **kwargs)


@login_required(login_url='/users/login')
def article_save(request, pk):
	post = get_object_or_404(Post, id=pk)
	if request.user in post.saves.all():
		post.saves.remove(request.user)
		messages.debug(request, "Article removed from your list.")
		return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))

	post.saves.add(request.user)
	link = f"https://www.walnutmind.org/articles/{post.slug}"
	description = f"Saved article: {post.title}"
	logitem = Log(
		user=request.user,
		description=description,
		link=link,
		datelog=datetime.now()
	)
	logitem.save()
	messages.debug(request, "Article saved to your list.")
	return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))


@login_required(login_url='/users/login')
def articleupvote(request, pk):
	post = get_object_or_404(Post, id=pk)
	if request.user in post.likes.all():
		post.likes.remove(request.user)
		messages.debug(request, "Article unliked.")
		return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))
	post.likes.add(request.user)
	link = f"https://www.walnutmind.org/articles/{post.slug}"
	description = f"Liked article: {post.title}"
	logitem = Log(
		user=request.user,
		description=description,
		link=link,
		datelog=datetime.now()
	)
	logitem.save()
	messages.debug(request, "Article liked, thank you for your feedback.")
	return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))


# ---------------------------------------------------------------------------------
@login_required(login_url='/users/login')
def newPostView(request):
	if request.method == 'POST':
		form = PostForm(request.POST,
		                request.FILES)  # Requires both request.Files, else will be left blank.
		if form.is_valid():
			form.instance.author = request.user  # Because author field from forms.py was excluded
			title = form.instance.title

			if form.instance.public == True:
				form.instance.was_public = True
				link = f"https://www.walnutmind.org/articles/{post_slug}"
				description = f"Published article: {title}"
				logitem = Log(
					user=request.user,
					description=description,
					link=link,
					datelog=datetime.now()
				)
				logitem.save()
			form.save()
			messages.success(request, "Article is successfully published!")
			post_slug = Post.objects.latest('pk').slug  # Get last entry object based on last pk

			return HttpResponseRedirect(reverse('articleview', args=[str(post_slug)]))
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

		if profanity_filter(content) == True:
			messages.warning(
				request, "Your comment could not be posted, please refrain from the "
				         "use of explicit language."
			)
			Infraction.objects.create(
				user=request.user,
				reason=f"Used explicit language in article ID {pk} with the comment: {content}",
				datelog=datetime.now()
			)
			return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))

		comment = Comment(
			post=post,
			content=content,
			author=request.user,
			dateCreated=date.today(),
			dateUpdated=date.today(),
		)
		comment.save()
		title = post.title
		post_slug = post.slug
		link = f"https://www.walnutmind.org/articles/{post_slug}"
		description = f"Posted comment on '{title}'"
		logitem = Log(
			user=request.user,
			description=description,
			link=link,
			datelog=datetime.now()
		)
		logitem.save()
		return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))
	return render(request, "Articles/article.html")


class updatePostView(UpdateView):
	login_required = True
	model = Post
	form_class = PostForm
	template_name = 'Articles/updatepost.html'

	def get_context_data(self, *args, **kwargs):
		context = super(updatePostView, self).get_context_data(*args, **kwargs)
		tags = Tag.objects.all()  # return all tags
		context['tags'] = tags

		if not self.object.was_public == True and self.object.public == True:
			self.object.was_public = True
			title = self.object.title
			post_slug = self.object.slug

			link = f"https://www.walnutmind.org/articles/{post_slug}"
			description = f"Published article: {title}"
			logitem = Log(
				user=self.request.user,
				description=description,
				link=link,
				datelog=datetime.now()
			)
			logitem.save()
		return context


class deletePostView(DeleteView):
	login_required = True
	model = Post
	template_name = 'Articles/deletepost.html'
	success_url = reverse_lazy('index')


@login_required(login_url='/users/login')
def deleteCommentView(request, pk, id):
	comment = Comment.objects.get(pk=id)
	post = Post.objects.get(pk=pk)
	if request.user == comment.author and comment.post == post:  # IF AND ONLY IF user is the
		# author of the comment, and the post is the same as the comment's post, then delete.
		comment.delete()
		messages.debug(request, "Comment succesfully deleted.")
		return HttpResponseRedirect(reverse('articleview', args=[str(post.slug)]))
	else:
		messages.warning(request, "An unknown error occurred attempting to delete your comment.")
		return HttpResponseRedirect(reverse('articleindex'))
