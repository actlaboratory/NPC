import requests
import json
from bs4 import BeautifulSoup

def getUserInfo(userId):
	return requests.get("	https://peing.net/api/v1/user/analysis_information/show?account=%s" % (userId)).json()

def getAnswers(userId):
	info = getUserInfo(userId)
	pages = -(info["answers_count"]*-1//5)
	answers = []
	for i in range(pages):
		answers.append(requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (userId, i+1)).json())
	return answers

def postQ(userId, message):
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
			"account":"guredora403"
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
		return result


