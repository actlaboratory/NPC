import requests
import json
from bs4 import BeautifulSoup

def getUserInfo(userId):
	page = requests.get("https://peing.net/%s/"% (userId))
	soup = BeautifulSoup(page.content, "lxml")
	div = soup.find("div", {"id": "user-id"}).div
	return json.loads(div.get("data-user-associated-with-page"))

def getAnswers(userId, page=None):
	info = getUserInfo(userId)
	page_count = -(info["answers_count"]*-1//3)
	answers = []
	if page == None:
		for i in range(page_count):
			page_content = requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (userId, i+1)).json()
			for item in page_content["items"]:
				answers.append(item)
		return answers
	if page >= 1 and page <= page_count:
		page_content = requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (userId, page)).json()
		for item in page_content["items"]:
			answers.append(item)
		return answers
	return False

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

