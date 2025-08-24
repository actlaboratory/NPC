# npc service
# Copyright (C) 2021-2025 yamahubuki <itiro.ishino@gmail.com>


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

from dao import userDao, answerDao,sentQuestionDao


JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
MAX_BLANK_PAGE_RETRY_COUNT = 5

class Service():
	def __init__(self):
		self.log=getLogger("%s.service" % (constants.LOG_PREFIX))
		self.userDao=userDao.UserDao()
		self.answerDao=answerDao.AnswerDao()
		self.sentQuestionDao=sentQuestionDao.sentQuestionDao()
		self.connection=dao.connectionFactory.getConnection()
		self.selfId=""
		self.session=None

	#
	#	ユーザ管理
	#

	# 指定のユーザが回答の閲覧対象として登録済みならTrue
	def isUserRegistered(self,info):
		if type(info)==int:		#idで照会
			try:
				if self.userDao.getWithoutFlag(info,constants.FLG_USER_NOT_REGISTERED|constants.FLG_USER_DISABLE) != []:
					return True
				return False
			except Exception as e:
				self.log.error(e)
				raise e
		if type(info)==entity.user.User: #userEntityで照会。idとaccountの両者一致を確認
			try:
				ret = self.userDao.getWithoutFlag(info.id,constants.FLG_USER_NOT_REGISTERED|constants.FLG_USER_DISABLE)
				if ret == [] or self._createUserObj(ret).account!=info.account:
					return False
				return True
			except Exception as e:
				self.log.error(e)
				raise e
		elif type(info)==str:	#accountで照会
			try:
				if self.userDao.getFromUserAccountWithoutFlag(info,constants.FLG_USER_NOT_REGISTERED|constants.FLG_USER_DISABLE) != []:
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

	# ユーザアカウントからユーザエンティティを得る
	# DBにあればそのまま返し、なければ取得してから返す
	def getUser(self,account):
		data = self.userDao.getFromUserAccount(account)
		if len(data)>0:
			return self._createUserObj(data[0])
		else:
			return self.getUserInfo(account)

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
			"flag": user.flag,
		}
		try:
			if len(self.userDao.get(user.id))==0:
				self.userDao.insert(data)
			else:
				self.userDao.update(data)
			self.connection.commit()
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			self.connection.rollback()
			raise e

	def deleteUser(self, user):
		self.log.debug("delete user target="+user.getViewString())
		try:
			data=self._createUserObj(self.userDao.get(user.id)[0])
			data.flag|=constants.FLG_USER_NOT_REGISTERED
			self.userDao.update(data.__dict__)
			self.answerDao.deleteFromUser(user.id)
			self.connection.commit()
			self.log.debug("user has been deleted.")
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			self.connection.rollback()
			raise e

	#有効なユーザのリストを返す
	def getEnableUserList(self):
		users = self.userDao.getAllWithoutFlag(constants.FLG_USER_DISABLE|constants.FLG_USER_NOT_REGISTERED)
		result = []
		for user in users:
			result.append(self._createUserObj(user))
		return result

	#登録済みユーザのリストを返す
	def getUserList(self):
		users = self.userDao.getAllWithoutFlag(constants.FLG_USER_NOT_REGISTERED)
		result = []
		for user in users:
			result.append(self._createUserObj(user))
		return result

	# 解凍件数より回答データが少ないユーザーを調べる
	# 結果は文字列
	def checkUserAnswerCount(self):
		result = ""
		users = self.userDao.getAllWithoutFlag(constants.FLG_USER_NOT_REGISTERED)
		for user in users:
			if user["answers"] > self.answerDao.count(user["id"])[0]["cnt"]:
				result += (user["account"] + ":回答数" + str(user["answers"]) + ",回答データ" + str(self.answerDao.count(user["id"])[0]["cnt"]) + "\n")
		if not result:
			return _("機械的に確認可能な不整合は見当たりませんでした。")
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
			return self.answerDao.getViewData(userId)
		except Exception as e:
			self.log.error(e)
			raise e

	def getSentQuestionList(self):
		self.log.debug("getSentQuestionViewData")
		try:
			return self.sentQuestionDao.getViewData()
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

	# 送信済み質問のanswerIdからanswerEntityを得る
	def getSentAnswer(self,id):
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
	def update(self,user, force = False):
		try:
			lastAnswer = self.answerDao.getLast(user.id)
		except Exception as e:
			self.log.debug("last answer check failed.")
			self.log.error(e)
			raise e
		if (lastAnswer == []) or force:
			return self._updateAnswer(user, datetime.datetime.fromtimestamp(0).replace(tzinfo=JST), force)
		else:
			return self._updateAnswer(user, lastAnswer[0]["answered_at"].replace(tzinfo=JST), force)

	#指定ユーザの指定時刻以降の回答を取得
	def _updateAnswer(self, user, time, force = False):
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
				# 途中にブランクページが入ることがあるらしいので対策
				is_end = True
				for i in range(1, MAX_BLANK_PAGE_RETRY_COUNT + 1):
					try:
						next_page_answers = peing.getAnswers(user.account, page=(page + i))
					except Exception as e:
						self.connection.rollback()
						self.log.error(e)
						return errorCodes.PEING_ERROR
					if next_page_answers:
						page += (i - 1)		# 下で1足すのでここでは-1する必要がある
						is_end = False
						break
				if is_end:
					break
			for answer in answers:
				answered_at = datetime.datetime.fromisoformat(answer["answer_created_at"])
				if answered_at <= time:		#これより先は前回以前に取得済みのため扶養
					flg = True
					break
				if lastAdd <= answered_at: # このループ中に追加の質問回答をした場合に発生する重複受信
					continue
				if force and len(self.answerDao.get(answer["answer_id"])):
					# すでに受信済み
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
	def login(self,idType,id,pw,force=False):
		if not force and self.session:
			self.log.debug("already logined")
			return errorCodes.OK
		self.log.debug("try login")
		if idType==constants.LOGIN_PEING:
			try:
				self.log.info("login with peing")
				session = peing.login(id,pw)
				if session == errorCodes.PEING_ERROR:
					return errorCodes.LOGIN_PEING_ERROR
				elif type(session)==int:
					return session
				self.session = session
				self.selfId = id
				return errorCodes.OK
			except Exception as e:
				self.log.error(e)
				return errorCodes.LOGIN_PEING_ERROR
		else:
			return errorCodes.LOGIN_UNKNOWN_ERROR

	def getSelfId(self,session):
		try:
			return peing.getLoginUser(session)
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

	def updateSentQuestionList(self):
		#まずは最新情報を更新
		self.log.debug("update sent questions")
		try:
			last = self.sentQuestionDao.getLast()
		except Exception as e:
			self.log.debug("last answer check failed.")
			self.log.error(e)
			raise e
		if last == []:
			last = datetime.datetime.fromtimestamp(0).replace(tzinfo=JST)
		else:
			last = last[0]["answered_at"].replace(tzinfo=JST)

		try:
			i=0
			while(True):
				i+=1
				ret = peing.getSentList(self.session,i)
				if ret == errorCodes.PEING_ERROR or type(ret)!=list:
					self.connection.rollback()
					return ret
				if len(ret)==0:
					break
				for q in ret:
					if datetime.datetime.fromisoformat(q["answer_created_at"]).replace(tzinfo=JST)<=last:
						break
					user = self.getUserInfo(q["answered_user_account"])
					self.sentQuestionDao.insert(entity.answer.Answer(
						q["answer_id"],
						user.id,
						q["body"],
						q["answer_body"],
						datetime.datetime.fromisoformat(q["answer_created_at"]).replace(tzinfo=None),
						self.makeAnswerFlag(q["question_type"]),
						q["uuid_hash"]
						).__dict__)
					if len(self.userDao.get(user.id))==0:		#新規
						user.flag|=constants.FLG_USER_NOT_REGISTERED
						self.userDao.insert(user.__dict__)
					else:
						self.userDao.update(user.__dict__)
				wx.YieldIfNeeded()
			self.connection.commit()
		except Exception as e:
			self.log.error(e)
			self.connection.rollback()
			return errorCodes.PEING_ERROR

		return errorCodes.OK

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
			return peing.recycle(self.session,hash)
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	#
	#	プロフィール
	#
	def getProfile(self):
		try:
			return peing.getProfile(self.session)
		except Exception as e:
			self.log.error(e)
			return errorCodes.PEING_ERROR

	def setProfile(self,v):
		try:
			return peing.setProfile(self.session,**v)
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
		except Exception as e:
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
		except Exception as e:
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
			self.log.warning("unknown question type %s found." % flagString)
		return flag
