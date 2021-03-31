# answer entity
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import constants

class Answer:
	def __init__(self,id,user,question,answer,answered_at,flag=0,uuid=None):
		self.id=id
		self.user=user
		self.question=question
		self.answer=answer
		self.answered_at=answered_at
		self.flag=flag
		self.uuid=uuid

	def getTypeString(self):
		return getTypeString(self.flag)

	def __str__(self):
		return "answer:%d(%s,%s=%s,%d)" % (self.id,str(self.user),self.question,self.answer,self.flag)

def getTypeString(flag):
	ret=[]
	dic={
		constants.FLG_ANSWER_AUTOQUESTION:_("運営"),
		constants.FLG_ANSWER_BATON_QUESTION:_("バトン"),
	}
	for i,s in dic.items():
		if flag&i==i:
			ret.append(s)
	return ",".join(ret)
