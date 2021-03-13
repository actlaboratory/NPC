# answer entity
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


class Answer:
	def __init__(self,id,user,question,answer,answered_at,flag=0):
		self.id=id
		self.user=user
		self.question=question
		self.answer=answer
		self.answered_at=answered_at
		self.flag=flag


	def __str__(self):
		return "answer:%d(%s,%s=%s,%d)" % (self.id,str(self.user),self.question,self.answer,self.flag)


