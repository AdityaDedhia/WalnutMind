from django.core.exceptions import ValidationError

def validate_file_size(value):
    filesize= value.size
    
    if filesize > 5242880 * 5: # 5MB * 5 = 25MB
        raise ValidationError("The maximum file size that can be uploaded is 20MB")
    else:
        return value