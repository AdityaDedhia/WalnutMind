from .models import Term, List, Resource, Collection
from django.views.generic import DetailView
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .forms import NewTermForm
from django.contrib import messages
from django.shortcuts import render, redirect
from isbnlib import meta, cover,doi
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline #Support full-text search
from Articles.views import Post as ArticlesPost
from Commentaries.views import Post as BooksPost
from Diaries.views import Post as BlogPost

SERVICE = "goob"

def wikiView(request):
    return render(request, 'Wiki/index.html')

def resourceView(request, pk):
    resource = Resource.objects.get(pk = pk)
    if resource.isbnlink is not None:
        isbn = resource.isbnlink
        metadata = meta(isbn, SERVICE)
        DOI = doi(isbn)
        bookcover = cover(isbn)
        return render(request,'Wiki/resource.html', {
            'metadata':metadata, 'DOI':DOI, 'cover':bookcover
        })
    return render(request,'Wiki/resource.html', {
        'resource': resource
    })

def collectionsView(request):
    resources = Resource.objects.all()
    collections = Collection.objects.all()
    collectionsCount = collections.count()
    return render(request, 'Wiki/collections.html', {
        'resources':resources, 'collections':collections, 'collectionsCount': collectionsCount
    })

def listsView(request):
    terms = Term.objects.all()
    lists = List.objects.all()
    listsCount = lists.count()
    return render(request, 'Wiki/lists.html', {
        'terms':terms, 'lists':lists, 'listsCount': listsCount
    })

#FULL-TEXT SEARCH FUNCTION
def searchView(request):
    if request.method == "POST":
        searchedterm = request.POST['searchedterm'] #Get the searched term
        query = SearchQuery(searchedterm) #USED FOR POSTGRES SEARCH INDEX
        search_headline =  SearchHeadline('content', query, config=None,start_sel = '<mark>',stop_sel = '</mark>',max_words=40, min_words=10, short_word=3,highlight_all=False)
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
            if form.is_valid():
                form.save()
                messages.success(request, ("Term was successfully published!"))
                latest_id = Term.objects.latest('pk').pk #Essentially gets latest entry object based on last pk added, and then gets the pk of that entry object.
                return redirect(f"/wiki/define-{latest_id}")
        else:
            form = NewTermForm()
        return render(request, 'Wiki/newterm.html', {
                'form': form
            })
