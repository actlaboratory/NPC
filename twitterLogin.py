# NPC Twitter login module
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import errorCodes

import requests
import urllib.parse

from bs4 import BeautifulSoup


def getToken(session):
	page = session.get("https://peing.net/ja/",timeout=5,verify=False)
	soup = BeautifulSoup(page.content, "lxml")
	form = soup.find("form", {"action":"/auth/twitter"})
	ret = form.find("input", {"name":"authenticity_token","type":"hidden"})
	return ret["value"]

def login(id, password):
	session = requests.Session()
	try:
		data = {
			"authenticity_token": getToken(session)
		}
	except:
		return errorCodes.LOGIN_PEING_ERROR

	headers = {
		"Accept-Language": "ja-JP",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
		"Content-Type": "application/x-www-form-urlencoded",
	}
	ret = session.post("https://peing.net/auth/twitter",headers=headers,data=data,timeout=5,verify=False)
	if not ret.url.startswith("https://api.twitter.com/oauth/authenticate?"):
		return errorCodes.LOGIN_PEING_ERROR

	soup = BeautifulSoup(ret.content, "lxml")
	headers = {
	}
	data = {
		"authenticity_token": soup.find("input", {"name":"authenticity_token","type":"hidden"})["value"],
		"redirect_after_login": soup.find("input", {"name":"redirect_after_login","type":"hidden"})["value"],
		"oauth_token": soup.find("input", {"name":"oauth_token","type":"hidden"})["value"],
		"session[username_or_email]": id,
		"session[password]": password
	}

	ret =  session.post("https://api.twitter.com/oauth/authenticate",headers=headers,data=data,timeout=5,verify=False)
	if ret.url.startswith("https://twitter.com/login/error?"):
		return errorCodes.LOGIN_WRONG_PASSWORD
	elif ret.url.startswith("https://twitter.com/account/access") or ret.url.startswith("https://twitter.com/login"):
		return errorCodes.LOGIN_RECAPTCHA_NEEDED
	elif not ret.url.startswith("https://api.twitter.com/oauth/authenticate"):
		return errorCodes.LOGIN_TWITTER_ERROR

	try:
		soup = BeautifulSoup(ret.content, "lxml")
		url = soup.find("meta",{"http-equiv":"refresh"})["content"][6:]
	except:
		return errorCodes.LOGIN_CONFIRM_NEEDED

	if not url.startswith("https://peing.net/auth/twitter/callback"):
		return errorCodes.LOGIN_TWITTER_ERROR
	session.get(url)
	return session
