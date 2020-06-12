import requests
import time
class Peing():
	def __init__(self, userId):
		self.id = userId
	def get_user_info(self):
		json = requests.get("	https://peing.net/api/v1/user/analysis_information/show?account=%s" % (self.id)).json()
		return json
	def get_user_answers(self, count):
		pages = -(count*-1//5)
		print("answer page count is %d", (pages))
		answers = {}
		for i in range(pages):
			print("getting pages %d", (i+1))
			json = requests.get("https://peing.net/api/v2/items/?type=answered&account=%s&page=%d" % (self.id, i+1)).json()
			for item in json["items"]:
				answers[item["body"]] = item["answer_body"]
			time.sleep(0.5)
		return answers
