import requests
import json

import errorCodes

from bs4 import BeautifulSoup

def getUserInfo(userId):
	page = requests.get("https://peing.net/%s/"% (userId))
	soup = BeautifulSoup(page.content, "lxml")
	entity = soup.find("div", {"id": "user-id"})
	if entity==None:	#ユーザ不存在
		return None
	return json.loads(entity.div.get("data-user-associated-with-page"))

def getAnswers(userId, page):
	assert page > 0
	answers = []
	page_content = requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (userId, page)).json()
	for item in page_content["items"]:
		answers.append(item)
	return answers

def postQuestion(userId, message):
	with requests.Session() as s:
		# CSRFトークンとクッキーの取得のために一度アクセスしておく。
		page = s.get("http://peing.net/%s" % (userId))
		# htmlを解析
		soup = BeautifulSoup(page.content, "lxml")
		tmp = soup.find("meta", {"name": "csrf-token"})
		token = tmp["content"]
		# リクエスト用のJSONを作る。
		reqJson = {
			"item":{
				"body":message,
				"hope_answer_type":"leave",
				"item_card_color":"default"
			},
			"user":{
			"account":userId
		},
			"type":"question",
			"event_theme_id":None
		}
		msg = json.dumps(reqJson)
		header = {
			"Content-Type": "application/json",
			"Accept": "application/json",
			"X-CSRF-TOKEN": token
		}
		result = s.post("https://peing.net/ja/%s/message" % (userId), msg, headers=header)
		if result.status_code==201:
			return errorCodes.OK
		else:
			return errorCodes.PEING_ERROR
