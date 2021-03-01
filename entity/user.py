


class User:
	def __init__(self,id,name,account,items,answers,profile,followees,flag=0):
		self.id=id
		self.name=name
		self.account=account
		self.items=items
		self.answers=answers
		self.profile=profile
		self.followees=followees
		self.flag=flag

	def __str__(self):
		return "userEntity:%s" % self.getViewString()

	def getViewString(self):
		return self.name+"(@"+self.account+")"
