# npc service
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import constants
import csvExporter
import dao
import errorCodes
import entity.user
import entity.answer
import peing
import views.main

import datetime
import wx

from logging import getLogger

from dao import userDao, answerDao


JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


class Service():
	def __init__(self):
		self.log=getLogger("%s.service" % (constants.LOG_PREFIX))
		self.userDao=userDao.UserDao()
		self.answerDao=answerDao.AnswerDao()
		self.connection=dao.connectionFactory.getConnection()
		self.selfId=""
		self.session=None

	#
	#	ユーザ管理
	#

	#指定のユーザが登録済みならTrue
	def isUserRegistered(self,info):
		if type(info) in (int,entity.user.User):			#idで紹介
			if type(info)==entity.user.User:
				info=info.id
			try:
				if self.userDao.get(info) != []:
					return True
				return False
			except Exception as e:
				self.log.error(e)
				raise e
		elif type(info)==str:	#accountで紹介
			try:
				if self.userDao.getFromUserName(info) != []:
					return True
				return False
			except Exception as e:
				self.log.error(e)
				raise e
		else:
			raise ValueError

	#peingのaccountからUserオブジェクトを得る
	def getUserInfo(self,key):
		assert type(key)==str
		self.log.debug("get user info:"+key)
		try:
			info = peing.getUserInfo(key)
			if info==None:
				self.log.info("requested user %s not found." % key)
				return errorCodes.NOT_FOUND
			return entity.user.User(info["id"],info["name"],info["account"],info["items_count"],info["answers_count"],info["profile"],info["followees_count"])
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR


	def addUser(self, user):
		self.log.debug("add user:"+user.getViewString())

		#STEP1:重複チェック
		ret = self.isUserRegistered(user)
		if ret==True:
			self.log.warning("this user already registered.")
			return errorCodes.DUPLICATED

		#STEP2:データ追加
		data = {
			"id": user.id,
			"account": user.account,
			"name": user.name,
			"items": user.items,
			"answers": user.answers,
			"profile": user.profile,
			"followees": user.followees,
		}
		try:
			self.userDao.insert(data)
			self.connection.commit()
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			self.connection.rollback()
			raise e

	def deleteUser(self, user):
		self.log.debug("delete user target="+user.getViewString())
		try:
			self.userDao.delete(user.id)
			self.answerDao.deleteFromUser(user.id)
			self.connection.commit()
			self.log.debug("user has been deleted.")
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			self.connection.rollback()
			raise e

	#有効なユーザIDの一覧を返す
	def getEnableUserList(self):
		users = self.userDao.getAllWithoutFlag(constants.FLG_USER_DISABLE)
		result = []
		for user in users:
			result.append(self._createUserObj(user))
		return result

	def getUserList(self):
		users = self.userDao.getAll()
		result = []
		for user in users:
			result.append(self._createUserObj(user))
		return result

	def updateUserInfo(self,user):
		try:
			self.userDao.update(user.__dict__)
			self.connection.commit()
			return errorCodes.OK
		except Exception as e:
			self.log.debug("update user info:"+user.account)
			self.log.error(e)
			self.connection.rollback()
			raise e

	def getViewData(self,userId=-1):
		self.log.debug("getViewData.target="+str(userId))
		try:
			data = self.answerDao.getViewData(userId)
			return data
		except Exception as e:
			self.log.error(e)
			raise e

	#answerIdからanswerEntityを得る
	def getAnswer(self,id):
		assert type(id)==int
		try:
			data = self.answerDao.get(id)[0]
			user = self.userDao.get(data["user_id"])[0]
			return self._createAnswerObj(data,user)
		except Exception as e:
			self.log.error(e)
			raise e

	#
	#	更新系
	#
	def update(self,user):
		try:
			lastAnswer = self.answerDao.getLast(user.id)
		except Exception as e:
			self.log.debug("last answer check failed.")
			self.log.error(e)
			raise e
		if lastAnswer == []:
			return self._updateAnswer(user, datetime.datetime.fromtimestamp(0).replace(tzinfo=JST))
		else:
			return self._updateAnswer(user, lastAnswer[0]["answered_at"].replace(tzinfo=JST))

	#指定ユーザの指定時刻以降の回答を取得
	def _updateAnswer(self, user, time):
		flg = False
		page = 1
		lastAdd = datetime.datetime.now().replace(tzinfo=JST)
		while True:
			try:
				answers = peing.getAnswers(user.account, page=page)
			except Exception as e:
				self.connection.rollback()
				self.log.error(e)
				return errorCodes.PEING_ERROR
			if answers == []:
				break
			for answer in answers:
				answered_at = datetime.datetime.fromisoformat(answer["answer_created_at"])
				if answered_at <= time:		#これより先は前回以前に取得済みのため扶養
					flg = True
					break
				if lastAdd <= answered_at: # このループ中に追加の質問回答をした場合に発生する重複受信
					continue
				flag=self.makeAnswerFlag(answer["question_type"])
				data = (answer["answer_id"],user.id, answer["body"], answer["answer_body"], answered_at.replace(tzinfo=None),flag)
				try:
					self.answerDao.insert(data)
				except Exception as e:
					self.connection.rollback()
					self.log.error(e)
					raise e
				lastAdd = answered_at
			if flg:
				break
			page += 1
			wx.YieldIfNeeded()
		self.connection.commit()
		return errorCodes.OK

	#
	#	質問投稿
	#
	def postQuestion(self,user,question,useSession=True):
		self.log.debug("post question %s to %s use_session=%s" %(question, user.account,str(useSession)))
		try:
			if useSession:
				if self.session==None:
					self.log.error("login required.")
					return errorCodes.PEING_ERROR
				return peing.postQuestion(user.account,question,self.session)
			else:
				return peing.postQuestion(user.account,question)
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR


	#
	#	質問への応答
	#
	def login(self,id,pw,force=False):
		if not force and self.session:
			self.log.debug("already logined")
			return errorCodes.OK
		try:
			self.log.debug("try login")
			session = peing.login(id,pw)
			if session == errorCodes.PEING_ERROR:
				return errorCodes.PEING_ERROR
			self.session = session
			self.selfId = id
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	def logout(self):
		self.session = None

	def getReceivedItemList(self):
		try:
			user = self.getUserInfo(self.selfId)
			l = []
			for i in range(-( (-(user.getQuestionCount()))//3 )):
				ret = peing.getReceivedItemList(self.session,i+1)
				if ret == errorCodes.PEING_ERROR or type(ret)!=list:
					return ret
				for q in ret:
					l.append(entity.answer.Answer(q["id"],None,q["body"],None,q["relative_time"],self.makeAnswerFlag(q["question_type"]),q["uuid_hash"]))
			return l
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	def getArchivedItemList(self):
		try:
			l = []
			i=0
			while(True):
				i+=1
				ret = peing.getArchivedItemList(self.session,i)
				if ret == errorCodes.PEING_ERROR or type(ret)!=list:
					return ret
				if len(ret)==0:
					break
				for q in ret:
					l.append(entity.answer.Answer(q["id"],None,q["body"],None,q["relative_time"],self.makeAnswerFlag(q["question_type"]),q["uuid_hash"]))
			return l
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	def answer(self,hash,answer):
		try:
			ret = peing.postAnswer(self.session,hash,answer)
			return ret
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	def archive(self,hash):
		try:
			ret = peing.archive(self.session,hash)
			return ret
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	def recycle(self,hash):
		try:
			ret = peing.recycle(self.session,hash)
			return ret
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	#
	#	ビュー補助
	#

	def makeContextMenu(self):
		helper=views.main.Menu("mainView")
		menu=wx.Menu()
		helper.RegisterMenuCommand(menu,[
			"FILE_SHOW_DETAIL",
			"FILE_DELETE_USER",
			"FILE_SHOW_USER_WEB",
			"FILE_SHOW_USER_DETAIL"
		])
		return menu

	def export(self,fileName,lst):
		exporter = csvExporter.CsvExporter()
		if exporter.exportVirtualList(fileName,lst,"\t"):
			return True
		else:
			return exporter.getErrorMessage()

	#
	#	内部用
	#
	#sqlite3.Rowからentity.user.Userに変換
	def _createUserObj(self,user):
		try:
			return entity.user.User(user["id"],user["name"],user["account"],user["items"],user["answers"],user["profile"],user["followees"],user["flag"])
		except exception as e:
			self.log.error(e)
			raise e

	#sqlite3.Rowからentity.answer.Answerに変換
	def _createAnswerObj(self,data,user):
		try:
			return entity.answer.Answer(
				data["id"],
				self._createUserObj(user),
				data["question"],
				data["answer"],
				data["answered_at"],
				data["flag"]
			)
		except exception as e:
			self.log.error(e)
			raise e

	def makeAnswerFlag(self,flagString):
		flag=0
		if flagString=="auto_question":
			flag|=constants.FLG_ANSWER_AUTOQUESTION
		elif flagString=="baton_question":
			flag|=constants.FLG_ANSWER_BATON_QUESTION
		elif flagString in ("normal_question"):
			pass
		else:
			self.log.warning("unknown question type %s found." % answer["question_type"])
		return flag