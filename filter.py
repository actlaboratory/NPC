# NPC list filter
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import re

import constants
import globalVars

enableFilters=[]


class FilterBase():
	def __init__(self):
		pass

	#フィルタの有効/無効を切り替える
	def enable(self,status):
		global enableFilters
		if status:
			enableFilters.append(self)
		else:
			enableFilters = [x for x in enableFilters if type(x)!= type(self)]

	#現在有効になっていればTrue
	def isEnable(self):
		for f in getFilterList():
			if type(self)==type(f):
				return True
		return False

	#フィルタが有効な場合にのみ呼び出される
	#与えられたanswerを画面に表示すべきならTrue
	def test(self,**args):
		raise NotImplementedError


#自動質問を非表示にする
class AutoQuestionFilter(FilterBase):
	def test(self,**args):
		return args["answerFlag"]&constants.FLG_ANSWER_AUTOQUESTION==0


#バトン質問を非表示にする
class BatonFilter(FilterBase):
	def test(self,**args):
		return args["answerFlag"]&constants.FLG_ANSWER_BATON_QUESTION==0


#特定ユーザの質問のみを表示
class UserFilter(FilterBase):
	def __init__(self,user=None):
		if user != None:
			self.targetUserId = user.id
		else:
			self.targetUserId = -1

	def test(self,**args):
		if self.targetUserId > 0:
			return args["userId"]==self.targetUserId
		else:
			return True

#検索条件に一致する回答のみを表示
class SearchFilter(FilterBase):
	def __init__(self,keyword="",type=0,isRe=False):
		self.keyword = keyword
		self.type = type
		self.isRe = isRe
		if isRe:
			self.ptn = re.compile(keyword)

	def test(self,**args):
		if self.isRe:
			if self.type == 0 and not self.ptn.search(args["q"]):
				return False
			elif self.type == 1 and not self.ptn.search(args["a"]):
				return False
			elif self.type == 2 and not (self.ptn.search(args["a"])!=None or self.ptn.search(args["q"])!=None):
				return False
		else:
			if self.type == 0 and not self.keyword in args["q"]:
				return False
			elif self.type == 1 and not self.keyword in args["a"]:
				return False
			elif self.type == 2 and not (self.keyword in args["q"] or self.keyword in args["a"]):
				return False
		return True


def getFilterList():
	return enableFilters

# 適用状況を設定から読込
def loadStatus():
	if globalVars.app.config.getboolean("filter_status","auto_question",False):
		AutoQuestionFilter().enable(True)
	if globalVars.app.config.getboolean("filter_status","baton",False):
		BatonFilter().enable(True)

# 適用状況を保存
def saveStatus():
	# いったんすべてFalseにしておく
	globalVars.app.config["filter_status"]["auto_question"]=False
	globalVars.app.config["filter_status"]["baton"]=False

	for f in getFilterList():
		if type(f)==AutoQuestionFilter:
			globalVars.app.config["filter_status"]["auto_question"]=True
		elif type(f)==BatonFilter:
			globalVars.app.config["filter_status"]["baton"]=True
