from datetime import datetime
from http.client import BAD_REQUEST
from .models import Term, List, Resource, Collection, CollectionOrder
from django.views.generic import DetailView, ListView, UpdateView
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import ResourceForm, NewTermForm, NewListForm, CollectionForm, DocLogForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline
from taggit.models import Tag
from django.contrib.auth.models import User
from django.conf import settings
import requests
from copy import deepcopy
from Articles.views import Post as ArticlesPost
from Commentaries.views import Post as BooksPost
from .utils import storage_usage, resource_collection_order, resource_collection_reorder, get_resource_heatmap
from Blog.utils import profanity_filter
from Diaries.views import Post as BlogPost
import re
from dal import autocomplete
from pytube import YouTube, Channel  # Support YT Metadata
from linkpreview import link_preview
from ratelimit.decorators import ratelimit
from django.core.cache import cache
from isbnlib import meta, cover, doi

SERVICE = "wiki"

def clearMessagesView(request):
    return HttpResponse("")


class TermAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Term.objects.all()

        if self.q:
            qs = qs.filter(term__icontains=self.q)  # case insensitive standard search
        return qs


RESOURCES_KEY = "resources.all"


def wiki_view(request):
    if request.user.is_authenticated:
        resources = cache.get(RESOURCES_KEY)
        if not resources:
            resources = Resource.objects.filter(creator=request.user)
            cache.set(RESOURCES_KEY, resources, settings.RESOURCES_LIFESPAN)

        unsorted = resources.filter(collectionorder=None, creator=request.user)
        recents = resources[:10]

        title = "Log " + str(datetime.now().strftime("%Y-%m-%d"))
        if resources.filter(title=title, creator=request.user, category='LOG').exists():
            log = Resource.objects.get(title=title, creator=request.user, category='LOG')
        else:
            log = None

        collections = Collection.objects.filter(creator=request.user)

        active = collections.filter(archived=False)
        archived = collections.filter(archived=True)

        # collectionresources = CollectionOrder.objects.prefetch_related('resource').filter(user=request.user) #Prefetch resources of collection object in collectionresources
        bytes = storage_usage(request.user)

        form = ResourceForm()
        logform = DocLogForm(instance=request.user)
        heatmap = get_resource_heatmap(request.user)

        # for collection in collections.all():
        #    collection_resources = collectionresources.filter(collection__pk = collection.pk)
        #    for resource in collection_resources.iterator():
        #        collection.resourcesorder.add(resource)

    else:
        active = None
        archived = None
        bytes = None
        form = None
        logform = None
        heatmap = None
        unsorted = None
        recents = None
        log = None

    return render(request, 'Wiki/index.html', {
        'collections': active, 'archived': archived, 'resources': recents, 'bytes': bytes, 'form': form,
        'logform': logform, 'heatmap': heatmap, 'unsorted': unsorted,'log': log
    })


# WM DEFINE ---------------------------------------------------------------
def searchTermView(request, pk):
    query = request.POST.get('search')

    list = List.objects.get(pk=pk)

    terms = list.terms.all()

    results = Term.objects.filter(term__icontains=query).exclude(
        term__in=terms.values_list('term', flat=True))  # filters out terms already in list

    return render(request, 'Wiki/search-term-results.html', {
        'results': results, 'pk': pk
    })


@login_required(login_url='/users/login')
def removeTermView(request, listpk, termpk):
    term = Term.objects.get(pk=termpk)
    list = List.objects.get(pk=listpk)

    list.terms.remove(term)
    list.save()

    terms = Term.objects.filter(list=list)

    return render(request, 'Wiki/term-list.html', {
        'terms': terms, 'list': list
    })


@login_required(login_url='/users/login')
def existingTermView(request, pk):
    term = request.POST.get("term")

    object = Term.objects.get(term=term)

    list = List.objects.get(pk=pk)
    list.terms.add(object)
    list.save()

    terms = Term.objects.filter(list=list)
    messages.success(request, f"Added {term} to {list}.")
    return render(request, 'Wiki/term-list.html', {
        'terms': terms, 'list': list
    })


@login_required(login_url='/users/login')
def addTermView(request, pk):
    if request.method == 'POST':
        form = NewTermForm(request.POST)

        # Since cover is optional, check whether it exists:
        if 'cover' in request.FILES:
            form.instance.cover = request.FILES['cover']
        else:
            form.instance.cover = None

        if form.is_valid():
            form.instance.creator = request.user  # Because author field from forms.py was excluded

            if profanity_filter(form.instance.term) == True or profanity_filter(form.instance.definition) == True:
                return HttpResponseBadRequest(STATUS=BAD_REQUEST)

            if request.user.profile.is_author:
                form.instance.verified = True
            form.save()

        latest_id = Term.objects.latest('pk').pk
        newterm = Term.objects.get(pk=latest_id)

        # 2) ADD TERM TO LIST

        list = List.objects.get(pk=pk)
        list.terms.add(newterm)
        list.save()

        # 3) RETRIEVE UPDATED TERMS LIST

        terms = Term.objects.filter(list=list)
        messages.success(request, f"Added {newterm} to {list}.")

        return render(request, 'Wiki/term-list.html', {
            'terms': terms, 'list': list
        })


# WM COLLECT -----------------------------------------------------------
def searchResourceView(request, pk):
    query = request.POST.get('search')
    resources = CollectionOrder.objects.filter(collection__pk=pk)
    help = False

    if query.startswith(('-', '#', '@')):  # Tuple for filtered searches

        if query.startswith('-'):
            category = query[1:]  # Remove operator from query
            category = str(category.split(' ')[0])  # Extract first word or 'category' from query

            if category == 'orphan':
                message = "Results in orphaned resources"
                if ' ' in query:
                    query = query.replace(f'-{category} ', '')  # Query, intentional space after type
                    results = Resource.objects.filter(title__icontains=query,
                                                      creator=request.user, collectionorder=None)[:10]
                else:
                    results = Resource.objects.filter(creator=request.user, collectionorder=None)[:10]

            else:
                message = "Invalid class specified"
                help = True
                results = None

        elif query.startswith('#'):
            type = query[1:]  # Remove operator from query
            type = str(type.split(' ')[0])  # Extract first word or 'tag' from query

            choices = Resource.category.field.choices
            message = ""
            for choice in choices:
                if choice[0] == type.upper():
                    message = "Results by type " + type
                    break
            if message == "":
                message = "Invalid category specified"
                help = True

            if ' ' in query:
                query = query.replace(f'#{type} ', '')  # Query, intentional space after type
            else:
                query = None
            type = type.upper()

            if query is None:
                results = Resource.objects.filter(category=type).exclude(~Q(creator=request.user),
                                                                         public=False).exclude(
                    title__in=resources.values_list('resource__title', flat=True))[:10]
            else:
                results = Resource.objects.filter(title__icontains=query, category=type).exclude(
                    ~Q(creator=request.user), public=False).exclude(
                    title__in=resources.values_list('resource__title', flat=True))[:10]
        else:
            creator = query[1:]  # Remove operator from query
            creator = str(creator.split(' ')[0])  # Extract first word or 'creator' from query

            if User.objects.filter(username=creator).exists():
                message = "Results by creator " + creator
            else:
                message = "Invalid username specified"
                help = True

            if ' ' in query:
                query = query.replace(f'@{creator} ', '')  # Query, intentional space after type
            else:
                query = None

            if query is None:
                results = Resource.objects.filter(creator__username=creator).exclude(~Q(creator=request.user),
                                                                                     public=False).exclude(
                    title__in=resources.values_list('resource__title', flat=True))[:10]
            else:
                results = Resource.objects.filter(title__icontains=query, creator__username=creator).exclude(
                    ~Q(creator=request.user), public=False).exclude(
                    title__in=resources.values_list('resource__title', flat=True))[:10]

    else:
        if query == '':
            message = "Waiting for a query"
            help = True
            results = None
        else:
            message = f"Results for '{query}'"
            results = Resource.objects.filter(title__icontains=query).exclude(
                ~Q(creator=request.user), public=False).exclude(
                title__in=resources.values_list('resource__title', flat=True))[:10]
            # Filter public false resources which are not created by user and are not in collection


    return render(request, 'Wiki/partials/search-resources-results.html', {
        'results': results, 'pk': pk, 'message': message, 'help': help
    })

def resourceSort(request):
    resource_order = request.POST.getlist('resource_order')
    collectionpk = request.POST.get('collectionpk')

    collections = Collection.objects.prefetch_related('resourcesorder').filter(
        creator=request.user, archived=False)

    updatedresources = []

    collectionresources = CollectionOrder.objects.prefetch_related('resource').filter(
        collection__pk=collectionpk, user=request.user)  # Prefetch resources of collection object in collectionresources

    for index, resource_pk in enumerate(resource_order, start=1):
        resource = next(x for x in collectionresources if x.pk == int(resource_pk))

        if resource.order != index:
            resource.order = index
            updatedresources.append(resource)

    CollectionOrder.objects.bulk_update(updatedresources, [
        'order'])  # Only update order field for only resources that have changed order.

    results = Resource.objects.filter(creator=request.user, collectionorder=None)[:10]

    messages.success(request, "Collection synced.")
    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections, 'unsorted': results,
    })


@login_required(login_url='/users/login')
def removeResourceView(request, collectionpk, resourcepk):
    collection = Collection.objects.get(pk=collectionpk)

    collections = Collection.objects.prefetch_related('resourcesorder').filter(creator=request.user, archived=False)

    resource = CollectionOrder.objects.filter(collection__pk=collectionpk, resource__pk=resourcepk, user=request.user)

    resource.delete()

    resource_collection_reorder(collection)

    messages.success(request, f"Removed resource from collection.")
    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections,
    })


@login_required(login_url='/users/login')
def existingResourceView(request, collectionpk, resourcepk):
    collections = Collection.objects.prefetch_related('resourcesorder').filter(creator=request.user,
                                                                                       archived=False)
    resource = Resource.objects.get(pk=resourcepk)
    collection = Collection.objects.get(pk=collectionpk)

    if not CollectionOrder.objects.filter(collection__pk=collectionpk, resource__pk=resourcepk).exists():
        resource = CollectionOrder(
            user=request.user,
            collection=collection,
            resource=resource,
            order=resource_collection_order(collection),
        )
        resource.save()
        collection.resourcesorder.add(resource)

    messages.success(request, "Resource added to collection.")
    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections,
    })


class termList(ListView):
    model = Term
    template_name = 'Wiki/term-list.html'
    context_object_name = 'terms'

    def get_queryset(self):
        return Term.objects.filter(creator=self.request.user)  # MUST MATCH WITH wikiView


class resourceList(ListView):
    model = Resource
    template_name = 'Wiki/resource-list.html'
    context_object_name = 'resources'

    def get_queryset(self):
        return Resource.objects.filter(creator=self.request.user)[:10]  # MUST MATCH WITH wikiView


@login_required(login_url='/users/login')
def docLog(request):
    title = "Log " + str(datetime.now().strftime("%Y-%m-%d"))
    resource = Resource.objects.get_or_create(title=title, creator=request.user, category='LOG')[0]

    if request.method == 'POST':
        resource.text = request.POST.get('content')
        resource.save()
    return HttpResponse(status=200)

@login_required(login_url='/users/login')
@ratelimit(key='ip', rate='6/m', block=True)
@ratelimit(key='ip', rate='60/h', block=True)
def addResourceView(request):
    if request.method == 'POST':

        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.creator = request.user

            # attempt to fill in missing fields

            # FILE CHECK
            if form.instance.filelink:
                filelink = str(form.instance.filelink)
                filetype = filelink.split('.')[-1]
                form.instance.filetype = filetype
                title = filelink.replace(f'{filetype}', '')
                title = title.replace('.', '')
                form.instance.title = title

                if filelink.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.svg', '.webp')):
                    form.instance.category = 'IMAGE'
                else:
                    form.instance.category = 'FILE'

            # URL CHECK
            elif form.instance.weblink is not None:
                url = str(form.instance.weblink)

                # If video, reroute
                if "youtube" in url:
                    form.instance.category = 'VIDEO'

                    form.instance.videolink = url
                    form.instance.weblink = None  # replace weblink with videolink field
                    yt = YouTube(url)
                    form.instance.title = str(yt.title)
                    form.instance.source = yt.author
                    form.instance.videochannel = yt.channel_url
                    form.instance.videolength = round((yt.length / 60))

                    videodescription = re.sub(r'http\S+', '', yt.description)
                    videodescription = re.sub(r'https\S+', '', videodescription)
                    videodate = yt.publish_date.strftime("%Y-%m-%d")

                    form.instance.videodescription = str(videodate) + ": " + videodescription[:220]
                    form.instance.videothumbnail = yt.thumbnail_url

                    # Clean phrase for key word NLP
                    cleanedphrase = yt.description
                    cleanedphrase = ''.join([i for i in cleanedphrase if not i.isdigit()])  # Remove numbers
                    cleanedphrase = re.sub(r'http\S+', '', cleanedphrase)

                    keywords = yt.keywords[:5]
                    print(keywords)
                    if keywords:
                        form.instance.description = keywords[:255]
                    else:
                        form.instance.keywords = yt.metadata[:255]
                else:
                    form.instance.category = 'WEB'
                    preview = link_preview(url)

                    # procedurally clean URL
                    url = url.replace('http://', '')
                    url = url.replace('https://', '')
                    url = url.replace('www.', '')

                    source = form.instance.source = url.split('/')[0]
                    url = url.replace(form.instance.source + '/', '')
                    imgurl = "https://logo.clearbit.com/" + source + "?size=100"  # get logo from clearbit

                    image_formats = ("image/png", "image/jpeg", "image/jpg")
                    r = requests.head(imgurl)
                    if r.headers["content-type"] in image_formats:
                        form.instance.webicon = imgurl
                    else:
                        form.instance.imgurl = None

                    # Add title
                    title = preview.title
                    if title:
                        form.instance.title = title
                    else:
                        if source == url:  # if remaining url is the source itself, do not elipse
                            form.instance.title = url[-40:]
                        else:
                            form.instance.title = "..." + url[-40:]

                    # Add description
                    description = preview.description  # Limit description to charfield 255 limit
                    if description != None:
                        form.instance.webdescription = description[:255]
                    else:
                        form.instance.webdescription = "No description available."

            elif form.instance.isbnlink is not None:
                form.instance.category = 'BOOK'
                isbnlink = form.instance.isbnlink
                metadata = meta(isbnlink, SERVICE)
                form.instance.title = metadata['Title']
                form.instance.source = metadata['Authors'][0]

            else:
                messages.success(request, "An unidentified resource was added, please try again later.")
                return HttpResponseBadRequest(status=204)

            # Fix public access
            if form.instance.public == True:
                if form.instance.category != 'WEB' and form.instance.category != 'VIDEO' and form.instance.category != 'BOOK':
                    title = str(form.instance.title).lower()
                    if Resource.objects.filter(title__iexact=title).exists():
                        messages.success(request,
                                         "Unable to publish live, we have found a similar public resource that already exists.")
                        return HttpResponseBadRequest(status=204)
                else:
                    messages.success(request, "You must be the original author of the resource to publish live.")
                    return HttpResponseBadRequest(status=204)

            form.save()

            form = ResourceForm()

            # VALIDATE TOTAL FILE STORAGE
            bytes = storage_usage(request.user)
            if bytes > settings.BASIC_STORAGE:
                messages.success(request, (
                    "You have exceeded your maximum file storage capacity of 200MB. Please delete some files before adding more."))

            heatmap = get_resource_heatmap(request.user)

            resources = Resource.objects.filter(creator=request.user)
            resources = cache.set(RESOURCES_KEY, resources, settings.RESOURCES_LIFESPAN)
            resources = cache.get(RESOURCES_KEY)[:10]
            return render(request, 'Wiki/resource-list.html', {
                'resources': resources, 'bytes': bytes, 'form': form, 'heatmap': heatmap,
            })
        else:
            messages.success = (request, "An error occured while trying to save your document.")
            return HttpResponseBadRequest(status=204)


@login_required(login_url='/users/login')
def deleteResourceView(request, pk):
    resource = Resource.objects.get(pk=pk)
    if resource.creator == request.user:
        resource.delete()

    resources = Resource.objects.filter(creator=request.user)
    resources = cache.set(RESOURCES_KEY, resources, settings.RESOURCES_LIFESPAN)
    resources = cache.get(RESOURCES_KEY)[:10]

    bytes = storage_usage(request.user)
    heatmap = get_resource_heatmap(request.user)

    return render(request, 'Wiki/resource-list.html', {
        'resources': resources, 'bytes': bytes, 'heatmap': heatmap,
    })


@login_required(login_url='/users/login')
def addCollectionView(request):
    title = request.POST.get('title')
    description = request.POST.get('description')

    Collection.objects.create(
        title=title,
        creator=request.user,  # Not explicitly assigned
        description=description,
    )
    collections = Collection.objects.prefetch_related('resourcesorder').filter(creator=request.user, archived=False)

    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections, 'bytes': bytes
    })


@login_required(login_url='/users/login')
def editCollectionView(request, pk_slug):
    collection = Collection.objects.get(pk=pk_slug)

    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            return render(request, 'Wiki/partials/collection-details.html', {
                'collection': collection,
            })

    else:
        form = CollectionForm(instance=collection)  # Instantiate form data with collection data

        return render(request, 'Wiki/partials/edit-collection.html', {
            'form': form, 'collection': collection
        })


@login_required(login_url='/users/login')
def copyCollectionView(request, pk_slug):
    collection = deepcopy(Collection.objects.get(pk=pk_slug))
    collectionresources = CollectionOrder.objects.prefetch_related('resource').filter(
        collection__pk=collection.pk, user=request.user)  # Prefetch resources of collection object in collectionresources

    collection.pk = None
    collection.id = None
    collection._state.adding = True

    collection.title = "Copy of " + collection.title
    collection.cover = None
    collection.public = False

    collection.save()

    for resource in collectionresources.iterator():
        newresource = CollectionOrder(
            user=request.user,
            collection=collection,
            resource=resource.resource,
            order=resource_collection_order(collection),
        )
        newresource.save()
        collection.resourcesorder.add(newresource)

    collections = Collection.objects.prefetch_related('resourcesorder').filter(
        creator=request.user, archived=False)

    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections, 'collection': collection,
    })

@login_required(login_url='/users/login')
def archiveCollectionView(request, pk_slug):
    collection = Collection.objects.get(pk=pk_slug)
    if collection.creator == request.user:
        if collection.archived == True:
            collection.archived = False
        else:
            collection.archived = True
        collection.save()

    collections = Collection.objects.prefetch_related('resourcesorder').filter(creator=request.user, archived=False)

    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections,
    })


@login_required(login_url='/users/login')
def deleteCollectionView(request, pk):
    collection = Collection.objects.get(pk=pk)
    if collection.creator == request.user:
        collection.delete()

    collections = Collection.objects.prefetch_related('resourcesorder').filter(creator=request.user, archived=False)

    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections,
    })


def resourceView(request, pk):
    resource = Resource.objects.get(pk=pk)
    if resource.weblink is not None:
        return redirect(resource.weblink)
    if resource.videolink is not None:
        return redirect(resource.videolink)

    if resource.isbnlink is not None:
        isbn = resource.isbnlink
        metadata = meta(isbn, SERVICE)
        DOI = doi(isbn)
        bookcover = cover(isbn)
        return render(request, 'Wiki/resource.html', {
            'resource': resource, 'metadata': metadata, 'DOI': DOI, 'cover': bookcover,
        })
    return render(request, 'Wiki/resource.html', {
        'resource': resource
    })


def resourceModalView(request, collectionpk, resourcepk, order):
    object = CollectionOrder.objects.get(collection__pk=collectionpk, resource__pk=resourcepk, user=request.user)

    orders = CollectionOrder.objects.filter(collection__pk=collectionpk, user=request.user)

    if order == 1 and len(orders) == 1:
        next = None  # For collections with only 1 resource
        previous = None
    elif order == 1 and len(orders) > 1:
        next = orders.get(order=int(order + 1))
        previous = None
    elif order == 2 and len(orders) == 2:
        next = None
        previous = orders.get(order=int(order - 1))

    elif order > 2 and order < len(orders):
        next = orders.get(order=int(order + 1))
        previous = orders.get(order=int(order - 1))

    elif order == len(orders) - 1:
        next = orders.get(order=int(order + 1))
        previous = orders.get(order=int(order - 1))
    else:
        next = None
        previous = orders.get(order=int(order - 1))

    resource = object.resource  # Input is order

    return render(request, 'Wiki/resource-modal.html', {
        'resource': resource, 'next': next, 'previous': previous, 'collectionpk': collectionpk,
    })


class editResourceView(UpdateView):
    login_required = True
    model = Resource
    form_class = ResourceForm
    template_name = 'Wiki/editresource.html'
    success_url = None


def collectionsView(request):
    resources = Resource.objects.filter(public=True)
    collections = Collection.objects.filter(public=True)
    return render(request, 'Wiki/collections.html', {
        'resources': resources, 'collections': collections,
    })


def listsView(request):
    terms = Term.objects.all()
    lists = List.objects.filter(public=True)
    listsCount = lists.count()

    if request.user.is_authenticated:
        privatelists = List.objects.filter(public=False, creator=request.user)
        privatelistsCount = privatelists.count()
    else:
        privatelists = None
        privatelistsCount = 0

    return render(request, 'Wiki/lists.html', {
        'terms': terms, 'lists': lists, 'listsCount': listsCount, 'privatelists': privatelists,
        'privatelistsCount': privatelistsCount
    })


class listView(DetailView):
    model = List
    slug_url_kwarg = 'pk_slug'
    template_name = 'Wiki/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(listView, self).get_context_data(*args, **kwargs)
        terms = Term.objects.filter(list=self.object)
        form = NewTermForm(self.request.POST)

        context['terms'] = terms
        context['form'] = form
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


def tagView(request, tag):
    print(tag)
    tag = get_object_or_404(Tag, slug=tag)
    articles = ArticlesPost.objects.filter(tags=tag)  # No need for referencing taggable manager
    books = BooksPost.objects.filter(tags=tag)
    blogs = BlogPost.objects.filter(tags=tag)
    return render(request, 'Wiki/tag.html', {
        'topic': tag, 'articles': articles, 'books': books, 'blogs': blogs
    })


# FULL-TEXT SEARCH FUNCTION
@ratelimit(key='post:searchedterm', rate='5/10m', block=True)  # Limit search for same query to 5 queries per 10 minutes
@ratelimit(key='ip', rate='60/h', block=True)  # Limit searches to 60 per hour
def searchView(request):
    if request.method == "POST":
        searchedterm = request.POST['searchedterm']  # Get the searched term
        query = SearchQuery(searchedterm)  # USED FOR POSTGRES SEARCH INDEX
        search_headline = SearchHeadline('content', query, config=None, start_sel='<mark>', stop_sel='</mark>',
                                         max_words=40, min_words=8, short_word=3, highlight_all=False)
        # query database
        if searchedterm and len(searchedterm) >= 2:
            # FULLTEXT SEARCH #1: TERMS & LISTS
            relatedLists = List.objects.filter(title__search=searchedterm)  # LIST
            termvector = SearchVector('term', 'definition')  # TERMS
            relatedTerms = Term.objects.annotate(priority=SearchRank(termvector, query)).annotate().filter(
                priority__gte=0.001).order_by('-priority')

            # FULLTEXT SEARCH #2: RESOURCES & COLLECTIONS
            relatedCollections = Collection.objects.filter(title__search=searchedterm)  # COLLECTIONS
            resourcevector = SearchVector('title', 'description')  # RESOURCES
            relatedResources = Resource.objects.annotate(priority=SearchRank(resourcevector, query)).annotate().filter(
                priority__gte=0.001).order_by('-priority')

            # FULLTEXT SEARCH #3: ARTICLES
            articlevector = SearchVector('title', 'abstract', 'content')  # ARTICLES

            relatedArticles = ArticlesPost.objects.annotate(priority=SearchRank(articlevector, query)).annotate(
                headline=search_headline).filter(priority__gte=0.001).order_by('-priority')

            # FULLTEXT SEARCH #4: BOOKS
            bookvector = SearchVector('title', 'abstract', 'summary', 'content')  # BOOKS

            relatedBooks = BooksPost.objects.annotate(priority=SearchRank(bookvector, query)).annotate(
                headline=search_headline).filter(priority__gte=0.001).order_by('-priority')

            # FULLTEXT SEARCH #5: BLOG
            blogvector = SearchVector('title', 'content')  # BLOG

            relatedBlog = BlogPost.objects.annotate(priority=SearchRank(blogvector, query)).annotate(
                headline=search_headline).filter(priority__gte=0.001).order_by('-priority')

            return render(request, 'Wiki/search.html', {
                'query': searchedterm, 'lists': relatedLists, 'terms': relatedTerms, 'collections': relatedCollections,
                'resources': relatedResources, 'articles': relatedArticles, 'books': relatedBooks, 'blogs': relatedBlog
            })
        return render(request, 'Wiki/search.html', {
            'noinput': True
        })
    else:
        return wikiView(request)


class definitionView(DetailView):
    model = Term
    slug_url_kwarg = 'pk_slug'
    template_name = 'Wiki/definition.html'

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


class collectionView(DetailView):
    model = Collection
    slug_url_kwarg = 'pk_slug'
    template_name = 'Wiki/collection.html'

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


@login_required(login_url='/users/login')
def newTermView(request):
    if request.method == 'POST':
        form = NewTermForm(request.POST)

        # Since cover is optional, check whether it exists:
        if 'cover' in request.FILES:
            form.instance.cover = request.FILES['cover']
        else:
            form.instance.cover = None

        if form.is_valid():
            # If publisher is author, terms are verified by default:
            if request.user.profile.is_author:
                form.instance.verified = True
            form.save()
            messages.success(request, ("Terms were successfully published."))

            # if request.POST.get('to_term'):
            # latest_id = Term.objects.latest('pk').pk #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
            #   return redirect(f"/wiki/define-{latest_id}")
            # else:
            return redirect(f"/wiki/terms/new")
        else:
            messages.success(request, ("Integrity validation failed. This term may already exist."))

    form = NewTermForm(request.POST)
    return render(request, 'Wiki/newterm.html', {
        'form': form
    })


@login_required(login_url='/users/login')
def newListView(request):
    if request.method == 'POST':
        form = NewListForm(request.POST)

        if form.is_valid():
            form.instance.creator = request.user  # Because author field from forms.py was excluded
            form.save()
            messages.success(request, ("Terms list was successfully created."))
            latest_id = List.objects.latest(
                'pk').slug  # Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
            return redirect(f"/wiki/lists/{latest_id}")
        else:
            messages.success(request,
                             ("Integrity validation failed. You have attempted to manipulate non-editable fields."))

    form = NewListForm(request.POST, instance=request.user)
    return render(request, 'Wiki/newlist.html', {
        'form': form,
    })
