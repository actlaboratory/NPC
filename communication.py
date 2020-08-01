import requests

def getUserInfo(userId):
	return requests.get("	https://peing.net/api/v1/user/analysis_information/show?account=%s" % (userId)).json()

def getAnswers(userId):
	info = getUserInfo(userId)
	pages = -(info["answers_count"]*-1//5)
	answers = []
	for i in range(pages):
		answers.append(requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (userId, i+1)).json())
	return answers

