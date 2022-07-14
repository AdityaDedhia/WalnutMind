from .models import Resource

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

