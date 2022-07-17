from http.client import BAD_REQUEST
from .models import Term, List, Resource, Collection, CollectionOrder
from django.views.generic import DetailView, ListView, UpdateView
from django.http import Http404, HttpResponse, HttpResponseBadRequest, QueryDict
from django.contrib.auth.decorators import login_required
from .forms import ResourceForm, NewTermForm, NewListForm, CollectionForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from isbnlib import meta, cover,doi
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline #Support full-text search
from taggit.models import Tag
from django.conf import settings
from Articles.views import Post as ArticlesPost
from Commentaries.views import Post as BooksPost
from .utils import storage_usage, resource_collection_order, resource_collection_reorder
from Blog.utils import profanity_filter
from Diaries.views import Post as BlogPost
from dal import autocomplete
from pytube import YouTube #Support YT Metadata
SERVICE = "wiki"

def clearMessagesView(request):
    return HttpResponse("")

class TermAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Term.objects.all()

        if self.q:
            qs = qs.filter(term__icontains=self.q) #case insensitive standard search
        return qs

def wikiView(request):
    if request.user.is_authenticated:
        resources = Resource.objects.filter(creator = request.user)
        collections = Collection.objects.filter(creator = request.user)
        collectionresources = CollectionOrder.objects.prefetch_related('resource').filter(user=request.user) #Prefetch resources of collection object in collectionresources


        bytes = storage_usage(request.user)

    else:
        resources = None
        collections = None
        collectionresources = None
        bytes = None

    return render(request, 'Wiki/index.html', {
        'collections': collections, 'collectionresources': collectionresources,'resources': resources, 'bytes': bytes,
    })

#WM DEFINE ---------------------------------------------------------------
def searchTermView(request, pk):
    query = request.POST.get('search')

    list = List.objects.get(pk = pk)

    terms = list.terms.all()

    results = Term.objects.filter(term__icontains=query).exclude(term__in=terms.values_list('term', flat=True)) #filters out terms already in list


    return render(request, 'Wiki/search-term-results.html', {
        'results': results, 'pk': pk
    })

@login_required(login_url='/users/login')
def removeTermView(request, listpk, termpk):
    term = Term.objects.get(pk = termpk)
    list = List.objects.get(pk = listpk)

    list.terms.remove(term)
    list.save()

    terms = Term.objects.filter(list = list)

    return render(request, 'Wiki/term-list.html', {
        'terms': terms,'list':list
    })

@login_required(login_url='/users/login')
def existingTermView(request, pk):
    term = request.POST.get("term")
  
    object = Term.objects.get(term = term)

    list = List.objects.get(pk = pk)
    list.terms.add(object)
    list.save()

    terms = Term.objects.filter(list = list)
    messages.success(request, f"Added {term} to {list}.")
    return render(request, 'Wiki/term-list.html', {
        'terms': terms,'list':list
    })


@login_required(login_url='/users/login')
def addTermView(request, pk):
   
    if request.method == 'POST':
        form = NewTermForm(request.POST)

        #Since cover is optional, check whether it exists:
        if 'cover' in request.FILES:
            form.instance.cover = request.FILES['cover']
        else:
            form.instance.cover = None
                
        if form.is_valid():
            form.instance.creator = request.user #Because author field from forms.py was excluded

            if profanity_filter(form.instance.term) == True or profanity_filter(form.instance.definition) == True:
                return HttpResponseBadRequest(STATUS=BAD_REQUEST)

            if request.user.profile.is_author:
                form.instance.verified = True
            form.save()

        latest_id = Term.objects.latest('pk').pk 
        newterm = Term.objects.get(pk = latest_id)

        #2) ADD TERM TO LIST

        list = List.objects.get(pk = pk)
        list.terms.add(newterm)
        list.save()

        #3) RETRIEVE UPDATED TERMS LIST

        terms = Term.objects.filter(list = list)
        messages.success(request, f"Added {newterm} to {list}.")

        return render(request, 'Wiki/term-list.html', {
            'terms': terms,'list':list
        })
  
#WM COLLECT -----------------------------------------------------------
def searchResourceView(request, pk):
    query = request.POST.get('search')

    resources = CollectionOrder.objects.filter(collection__pk = pk)

    results = Resource.objects.filter(title__icontains=query).exclude(title__in=resources.values_list('resource__title', flat=True))

    return render(request, 'Wiki/partials/search-resources-results.html', {
        'results': results, 'pk': pk,
    })

def resourceSort(request):
    resource_order = request.POST.getlist('resource_order')
    collectionpk = request.POST.get('collectionpk')
    collections = Collection.objects.filter(creator = request.user)

    updatedresources = []

    collectionresources = CollectionOrder.objects.prefetch_related('resource').filter(collection__pk = collectionpk, user=request.user) #Prefetch resources of collection object in collectionresources

    for index, resource_pk in enumerate(resource_order, start=1):
        resource = next(x for x in collectionresources if x.pk == int(resource_pk))

        if resource.order != index:
            resource.order = index
            updatedresources.append(resource)

    CollectionOrder.objects.bulk_update(updatedresources, ['order']) #Only update order field for only resources that have changed order.
    


    collectionresources = CollectionOrder.objects.filter(user=request.user)
    messages.success(request, "Collection synced.")
    return render(request, 'Wiki/partials/collection-resource-list.html', {  
        'collections': collections, 'collectionresources': collectionresources,
    })

@login_required(login_url='/users/login')
def removeResourceView(request, collectionpk, resourcepk):
    collection = Collection.objects.get(pk = collectionpk)

    collections = Collection.objects.filter(creator = request.user)

    item = CollectionOrder.objects.filter(collection__pk = collectionpk, resource__pk = resourcepk, user = request.user)

    item.delete()

    resource_collection_reorder(collection)

    collectionresources = CollectionOrder.objects.filter(user=request.user)

    messages.success(request, f"Removed resource from collection.")
    return render(request, 'Wiki/partials/collection-resource-list.html', {  
        'collections': collections, 'collectionresources': collectionresources,
    })

@login_required(login_url='/users/login')
def existingResourceView(request, collectionpk, resourcepk):
    collections = Collection.objects.filter(creator = request.user)

    object = Resource.objects.get(pk = resourcepk)
    collection = Collection.objects.get(pk = collectionpk)

    if not CollectionOrder.objects.filter(collection__pk=collectionpk, resource__pk=resourcepk).exists():

        CollectionOrder.objects.create(
            user = request.user,
            collection = collection,
            resource = object,
            order = resource_collection_order(collection),
        )

    collectionresources = CollectionOrder.objects.filter(user=request.user)

    messages.success(request, "Resource added to collection.")
    return render(request, 'Wiki/partials/collection-resource-list.html', {  
        'collections': collections, 'collectionresources': collectionresources,
    })

class termList(ListView):
    model = Term
    template_name ='Wiki/term-list.html'
    context_object_name = 'terms'

    def get_queryset(self):
        return Term.objects.filter(creator = self.request.user) #MUST MATCH WITH wikiView

class resourceList(ListView):
    model = Resource
    template_name ='Wiki/resource-list.html'
    context_object_name = 'resources'

    def get_queryset(self):
        return Resource.objects.filter(creator = self.request.user)[:10] #MUST MATCH WITH wikiView

@login_required(login_url='/users/login')
def addResourceView(request):

    title = request.POST.get('title')
    description = request.POST.get('description')
    source = request.POST.get('source')
    text = request.POST.get('text')
    file = request.FILES.get('filelink')
    image = request.FILES.get('imagelink')
    web = request.POST.get('weblink')
    video = request.POST.get('videolink')
    book = request.POST.get('isbnlink')
    public = bool(request.POST.get('public'))

    #VALIDATE TOTAL FILE STORAGE
    bytes = storage_usage(request.user)
    if bytes > settings.BASIC_STORAGE:
        messages.success(request, ("You have exceeded your maximum file storage capacity of 200MB. Please delete some files before adding more."))
        return render(request, 'Wiki/resource-list.html', {
            'resources': resources
        })

    Resource.objects.create(
        title = title,
        creator = request.user,
        description = description,
        source = source,
        text = text,
        filelink = file,
        imagelink = image,
        weblink = web,
        videolink = video,
        isbnlink = book,
        public = public,
    )

    resources = Resource.objects.filter(creator = request.user)

    return render(request, 'Wiki/resource-list.html', {
        'resources': resources, 'bytes': bytes
    })

@login_required(login_url='/users/login')
def deleteResourceView(request, pk):
    resource = Resource.objects.get(pk = pk)
    if resource.creator == request.user:
        resource.delete()

    resources = Resource.objects.filter(creator = request.user)

    return render(request, 'Wiki/resource-list.html', {
        'resources': resources
    })

@login_required(login_url='/users/login')
def addCollectionView(request):
    title = request.POST.get('title')
    description = request.POST.get('description')

    Collection.objects.create(
        title = title,
        creator = request.user, #Not explicitly assigned
        description = description,
    )
    collections = Collection.objects.filter(creator = request.user)

    return render(request, 'Wiki/partials/collection-resource-list.html', {
        'collections': collections, 'bytes': bytes
    })


@login_required(login_url='/users/login')
def editCollectionView(request, pk_slug):
    collection = Collection.objects.get(pk = pk_slug)

    if request.method == 'POST':
        data = QueryDict(request.body).dict()
        form = CollectionForm(data, instance=collection)
        if form.is_valid():
            form.save()
            return render(request,'Wiki/partials/collection-details.html', {
                'collection': collection,
            })

    else:
        form = CollectionForm(instance=collection) #Instantiate form data with collection data

        return render(request, 'Wiki/partials/edit-collection.html', {
            'form': form, 'collection': collection
        })

def resourceView(request, pk):
    resource = Resource.objects.get(pk = pk)
    if resource.weblink is not None:
        return redirect(resource.weblink)
    if resource.videolink is not None:
        return redirect(resource.videolink)

    if resource.isbnlink is not None:
        isbn = resource.isbnlink
        metadata = meta(isbn, SERVICE)
        DOI = doi(isbn)
        bookcover = cover(isbn)
        return render(request,'Wiki/resource.html', {
            'resource':resource, 'metadata':metadata, 'DOI':DOI, 'cover':bookcover,
        })
    return render(request,'Wiki/resource.html', {
        'resource': resource
    })

def resourceModalView(request, collectionpk, resourcepk, order):

    object = CollectionOrder.objects.get(collection__pk=collectionpk, resource__pk=resourcepk, user=request.user)

    orders = CollectionOrder.objects.filter(collection__pk=collectionpk, user=request.user)

    if order >1 and order <len(orders):
        next = orders.get(order = int(order+1))
        previous = orders.get(order = int(order-1))
    elif order <2:
        previous = None
        next = orders.get(order = int(order+1))
    elif order >= len(orders):
            next = None
            previous = orders.get(order = int(order-1))


    resource = object.resource #Input is order

    return render(request,'Wiki/resource-modal.html', {
        'resource': resource, 'next': next, 'previous': previous, 'collectionpk': collectionpk,
    })

class editResourceView(UpdateView):
    login_required = True
    model = Resource
    form_class = ResourceForm
    template_name = 'Wiki/editresource.html'
    success_url = None

def collectionsView(request):
    resources = Resource.objects.all()
    collections = Collection.objects.all()
    collectionsCount = collections.count()
    return render(request, 'Wiki/collections.html', {
        'resources':resources, 'collections':collections, 'collectionsCount': collectionsCount
    })

def listsView(request):
    terms = Term.objects.all()
    lists = List.objects.filter(public = True)
    listsCount = lists.count()

    if request.user.is_authenticated:
        privatelists = List.objects.filter(public =False, creator = request.user)
        privatelistsCount = privatelists.count()
    else:
        privatelists = None
        privatelistsCount = 0

    return render(request, 'Wiki/lists.html', {
        'terms':terms, 'lists':lists, 'listsCount': listsCount, 'privatelists':privatelists, 'privatelistsCount': privatelistsCount
    })

class listView(DetailView):
    model = List
    slug_url_kwarg = 'pk_slug'
    template_name = 'Wiki/list.html'
    def get_context_data(self, *args, **kwargs):
        context = super(listView, self).get_context_data(*args, **kwargs)
        terms = Term.objects.filter(list = self.object)
        form = NewTermForm(self.request.POST)

        context['terms'] = terms
        context['form'] = form
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

def tagView(request, tag):
    print(tag)
    tag = get_object_or_404(Tag, slug=tag)
    articles = ArticlesPost.objects.filter(tags=tag) #No need for referencing taggable manager
    books = BooksPost.objects.filter(tags=tag)
    blogs = BlogPost.objects.filter(tags=tag)
    return render(request, 'Wiki/tag.html', {
        'topic': tag, 'articles': articles, 'books': books, 'blogs': blogs
    })

#FULL-TEXT SEARCH FUNCTION
def searchView(request):
    if request.method == "POST":
        searchedterm = request.POST['searchedterm'] #Get the searched term
        query = SearchQuery(searchedterm) #USED FOR POSTGRES SEARCH INDEX
        search_headline =  SearchHeadline('content', query, config=None,start_sel = '<mark>',stop_sel = '</mark>',max_words=40, min_words=8, short_word=3,highlight_all=False)
        #query database
        if searchedterm and len(searchedterm)>=2:
            #FULLTEXT SEARCH #1: TERMS & LISTS
            relatedLists = List.objects.filter(title__search= searchedterm) #LIST
            termvector = SearchVector('term','definition') #TERMS
            relatedTerms = Term.objects.annotate(priority=SearchRank(termvector, query)).annotate().filter(priority__gte=0.001).order_by('-priority')

            #FULLTEXT SEARCH #2: RESOURCES & COLLECTIONS
            relatedCollections = Collection.objects.filter(title__search= searchedterm) #COLLECTIONS
            resourcevector = SearchVector('title','description') #RESOURCES
            relatedResources = Resource.objects.annotate(priority=SearchRank(resourcevector, query)).annotate().filter(priority__gte=0.001).order_by('-priority')

            #FULLTEXT SEARCH #3: ARTICLES
            articlevector = SearchVector('title','abstract','content') #ARTICLES

            relatedArticles = ArticlesPost.objects.annotate(priority=SearchRank(articlevector, query)).annotate(headline=search_headline).filter(priority__gte=0.001).order_by('-priority')

            #FULLTEXT SEARCH #4: BOOKS
            bookvector = SearchVector('title','abstract','summary','content') #BOOKS

            relatedBooks = BooksPost.objects.annotate(priority=SearchRank(bookvector, query)).annotate(headline=search_headline).filter(priority__gte=0.001).order_by('-priority')

            #FULLTEXT SEARCH #5: BLOG
            blogvector = SearchVector('title', 'content') #BLOG

            relatedBlog = BlogPost.objects.annotate(priority=SearchRank(blogvector, query)).annotate(headline=search_headline).filter(priority__gte=0.001).order_by('-priority')


            return render(request, 'Wiki/search.html', {
                'query': searchedterm, 'lists': relatedLists, 'terms': relatedTerms, 'collections':relatedCollections, 'resources': relatedResources, 'articles': relatedArticles, 'books': relatedBooks, 'blogs': relatedBlog
        })
        return render(request, 'Wiki/search.html', {
            'noinput': True
        })
    else:
        return render(request, 'Wiki/search.html', {
            'noinput': False}
            )


class definitionView(DetailView):
    model = Term
    slug_url_kwarg = 'pk_slug'
    template_name = 'Wiki/definition.html'

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


class collectionView(DetailView):
    model = Collection
    slug_url_kwarg = 'pk_slug'
    template_name = 'Wiki/collection.html'

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
def newTermView(request):
    if request.method == 'POST':
        form = NewTermForm(request.POST)

        #Since cover is optional, check whether it exists:
        if 'cover' in request.FILES:
            form.instance.cover = request.FILES['cover']
        else:
            form.instance.cover = None

        if form.is_valid():
            #If publisher is author, terms are verified by default:
            if request.user.profile.is_author:
                form.instance.verified = True
            form.save()
            messages.success(request, ("Terms were successfully published."))

            #if request.POST.get('to_term'):
            #latest_id = Term.objects.latest('pk').pk #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
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
            form.instance.creator = request.user #Because author field from forms.py was excluded
            form.save()
            messages.success(request, ("Terms list was successfully created."))
            latest_id = List.objects.latest('pk').slug #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
            return redirect(f"/wiki/lists/{latest_id}")
        else:
            messages.success(request, ("Integrity validation failed. You have attempted to manipulate non-editable fields."))

    form = NewListForm(request.POST, instance = request.user)
    return render(request, 'Wiki/newlist.html', {
        'form': form,
    })