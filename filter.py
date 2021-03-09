# NPC list filter

import constants


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


def getFilterList():
	return enableFilters
