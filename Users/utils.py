import json
import os
import urllib.request

import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
	def _make_hash_value(self, user, timestamp):
		return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(
			user.is_active)).encode('utf-8')


generate_token = TokenGenerator()


def verify_email(email):
	api_key = os.environ.get('REALEMAIL_API_KEY')
	link = 'https://realemail.expeditedaddons.com/?api_key=' + api_key + '&email=' + email + \
	       '&fix_typos=true'

	link = urllib.request.urlopen(link)
	response = link.read()
	print(response)
	obj = json.loads(response)
	try:
		if obj["valid"] == True and obj["domain_error"] == False and obj["is_personal"] == True \
				and obj["is_disposable"] == False and obj["mx_records_found"] == True:
			return True
		else:
			return False
	except:
		return False


def verify_ip(ip):
	api_key = os.environ.get('IPINVESTIGATOR_API_KEY')
	link = 'https://ipinvestigator.expeditedaddons.com/?api_key=' + api_key + '&ip=' + ip

	link = urllib.request.urlopen(link)
	response = link.read()
	obj = json.loads(response)
	try:
		if obj["is_spam_bot"] == True or obj["is_listed"] == True or obj["is_malware"] == True or \
				obj["blocklists"] != [] or obj["is_hijacked"] == True or obj["is_exploit_bot"] == \
				True or obj["is_spyware"] == True or obj["is_bot"] == True:
			status = "malicious"
			return status
		if obj["is_tor"] == True or obj["is_vpn"] == True or obj["is_proxy"] == True:
			status = "anonymous"
			return status
		else:
			status = "normal"
			return status
	except:
		status = "anonymous"
		return status


def get_ip(request):
	x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forw_for is not None:
		ip = x_forw_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip
