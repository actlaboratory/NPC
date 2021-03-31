import requests
import json

import errorCodes

from bs4 import BeautifulSoup

def getUserInfo(userId):
	page = requests.get("https://peing.net/%s/"% (userId),timeout=5)
	soup = BeautifulSoup(page.content, "lxml")
	entity = soup.find("div", {"id": "user-id"})
	if entity==None:	#ユーザ不存在
		return None
	return json.loads(entity.div.get("data-user-associated-with-page"))

def getAnswers(userId, page):
	assert page > 0
	answers = []
	page_content = requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (userId, page),timeout=5).json()
	for item in page_content["items"]:
		answers.append(item)
	return answers

def postQuestion(userId, message,session=None):
	if not session:
		session = requests.Session()

	# CSRFトークンとクッキーの取得のために一度アクセスしておく。
	page = session.get("https://peing.net/%s" % (userId),timeout=5)
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
	result = session.post("https://peing.net/ja/%s/message" % (userId), msg, headers=header, timeout=5)
	if result.status_code==201:
		return errorCodes.OK
	else:
		return errorCodes.PEING_ERROR

#ログインページを開き、その後のPOSTリクエストで必要なトークンを得る
def _getAuthenticityToken(session):
	page = session.get("https://peing.net/ja/acc/login",timeout=5)
	soup = BeautifulSoup(page.content, "lxml")
	input = soup.find("input", {"name":"authenticity_token","type":"hidden"})
	if input == None:
		return errorCodes.PEING_ERROR
	return input["value"]

#idとpwを用いてログインする
def login(id,pw):
	session = requests.Session()
	token = _getAuthenticityToken(session)
	if token == errorCodes.PEING_ERROR:
		return errorCodes.PEING_ERROR
	headers = {
		"Content-Type":"application/x-www-form-urlencoded",
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
	}
	body = {
		"authenticity_token":token,
		"account":id,
		"password":pw,
		"button":""
	}

	result = session.post("https://peing.net/ja/acc/login_confirm", body, headers=headers, timeout=5)
	if result.status_code!=200 or len(result.history)!=1 or result.history[0].status_code!=302:
		return errorCodes.PEING_ERROR
	return session


def _getToken(session):
	assert type(session)==requests.sessions.Session
	response = session.get("https://peing.net/api/v2/user_tokens/me")
	if response.status_code!=200 or len(response.text)!=32:
		return errorCodes.PEING_ERROR
	return response.text

def getReceivedItemList(session,page=1):
	assert type(session)==requests.sessions.Session
	result = session.get("https://peing.net/api/v2/me/items/received?status=%E6%9C%AA%E8%AA%AD&page="+str(page))
	return json.loads(result.text)["items"]

def getArchivedItemList(session,page):
	assert type(session)==requests.sessions.Session
	if page==1:
		# 1ページ目にpage=1を入れると未回答が取得されてしまうため対策
		result = session.get("https://peing.net/api/v2/me/items/received?status=%E9%9D%9E%E8%A1%A8%E7%A4%BA")
	else:
		result = session.get("https://peing.net/api/v2/me/items/received?status=%E9%9D%9E%E8%A1%A8%E7%A4%BA&page="+str(page))
	return json.loads(result.text)["items"]

def postAnswer(session,hash,answer):
	assert type(session)==requests.sessions.Session
	assert type(hash)==str
	assert type(answer)==str

	# token入手
	page = session.get("https://peing.net/ja/q/"+hash)
	soup = BeautifulSoup(page.content, "lxml")
	input = soup.find("input", {"name":"authenticity_token","type":"hidden"})
	if input == None:
		return errorCodes.PEING_ERROR
	token = input["value"]

	headers = {
		"Content-Type":"application/x-www-form-urlencoded",
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
	}
	body = {
		"authenticity_token":token,
		"answer[body]":answer,
		"type":"link"
	}
	result = session.post("https://peing.net/ja/q/"+hash+"/answer", body, headers=headers, timeout=5)
	if result.status_code!=200 or len(result.history)!=1 or result.history[0].status_code!=302:
		return errorCodes.PEING_ERROR
	return errorCodes.OK

def archive(session,hash):
	assert type(session)==requests.sessions.Session
	assert type(hash)==str

	#CSRF対策の為閲覧
	page = session.get("https://peing.net/ja/box")
	soup = BeautifulSoup(page.content, "lxml")
	entity = soup.find("meta", {"name": "csrf-token"})

	body = '{"change_type":"非表示","locale":"ja"}'.encode("UTF-8")
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"X-CSRF-TOKEN": entity["content"],
	}
	result = session.put("https://peing.net/api/v1/questions/"+hash, body, headers=headers, timeout=5)
	if result.status_code!=200:
		return errorCodes.PEING_ERROR
	return errorCodes.OK

def recycle(session,hash):
	assert type(session)==requests.sessions.Session
	assert type(hash)==str

	#CSRF対策の為閲覧
	page = session.get("https://peing.net/ja/box")
	soup = BeautifulSoup(page.content, "lxml")
	entity = soup.find("meta", {"name": "csrf-token"})

	body = '{"change_type":"未読","locale":"ja"}'.encode("UTF-8")
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"X-CSRF-TOKEN": entity["content"],
	}
	#result = session.put("https://peing.net/api/v1/questions/"+hash, body, headers=headers, timeout=5)
	if result.status_code!=200:
		return errorCodes.PEING_ERROR
	return errorCodes.OK

def getSentList(session,page=1):
	assert type(session)==requests.sessions.Session
	assert page>0

	result = session.get("https://peing.net/api/v2/send_questions?page="+str(page))
	return json.loads(result.text)["items"]
