from .models import CollectionOrder, Resource
from django.db.models import Max

def storage_usage(User):
    #VALIDATE TOTAL FILE STORAGE
    bytes = 0

    resources = Resource.objects.filter(creator = User)
    for resource in resources:
        if resource.filelink:
            bytes += resource.filelink.size

        if resource.imagelink:
            bytes += resource.imagelink.size

    return bytes

def resource_collection_order(collection) -> int:
    existing_resources = CollectionOrder.objects.filter(collection = collection)

    if not existing_resources.exists(): #If no resources in collection initialise first item order to 1
        return 1
    else:
        current_max = existing_resources.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1

def resource_collection_reorder(collection):
    existing_resources = CollectionOrder.objects.filter(collection = collection)
    if not existing_resources.exists():
        return
    resource_count = existing_resources.count()
    new_order = range(1, resource_count+1)

    for order, resource in zip(new_order, existing_resources):
        resource.order = order
        resource.save()