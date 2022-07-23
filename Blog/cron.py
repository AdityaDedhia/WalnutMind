from django.core.management import call_command

def periodicbackup():
    try:
        call_command('dbbackup')
    except:
        pass