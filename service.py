import constants
import dao
import errorCodes
import entity.user
import entity.answer
import exceptions.dbException
import peing
import views.main

import datetime
import wx

from dao import userDao, answerDao
from exceptions import *

from logging import getLogger


JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


class Service():
	def __init__(self):
		self.log=getLogger("%s.service" % (constants.LOG_PREFIX))
		self.userDao=userDao.UserDao()
		self.answerDao=answerDao.AnswerDao()
		self.connection=dao.connectionFactory.getConnection()

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

	#peingのidまたはaccountからUserオブジェクトを得る
	def getUserInfo(self,key):
		assert type(key) in (int,str)
		try:
			info = peing.getUserInfo(key)
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
			"name": user.name
		}
		try:
			self.userDao.insert(data)
			self.connection.commit()
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			self.connection.rollback()
			raise e

	def deleteUser(self, userId):
		self.log.debug("delete user target="+str(userId))
		try:
			info = self.userDao.get(userId)
			self.log.debug("target user = "+info[0]["account"])
			if info == None:
				return errorCodes.NOT_FOUND
			self.userDao.delete((info[0]["id"],))
			self.answerDao.deleteFromUser((info[0]["id"],))
			self.connection.commit()
			self.log.debug("user has been deleted.")
			return errorCodes.OK
		except Exception as e:
			self.log.error(e)
			return self.connection.rollback()
			raise e

	#有効なユーザIDの一覧を返す
	def getEnableUserList(self):
		users = self.userDao.getAllWithoutFlag(constants.FLG_USER_DISABLE)
		result = []
		for user in users:
			result.append(self._createUserObj(user))
		return result

	def getViewData(self,userId=-1):
		self.log.debug("getViewData.target="+str(userId))
		try:
			data = self.answerDao.getViewData(userId)
			return data
		except Exception as e:
			self.log.error(e)
			return errorCodes.UNKNOWN

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
			return self._addAllAnswers(user)
		else:
			return self._updateAnswer(user, lastAnswer[0]["answered_at"].replace(tzinfo=JST))

	#指定ユーザの全ての回答を取得
	def _addAllAnswers(self, user):
		self.log.debug("addAllAnswers from user "+str(user))
		try:
			answers = peing.getAnswers(user.account)
		except:
			return errorCodes.PEING_ERROR
		values = []
		for answer in answers:
			answered_at=answer["answer_created_at"][0:10]+" "+answer["answer_created_at"][11:19]
			data = (answer["answer_id"],user.id, answer["body"], answer["answer_body"], answered_at)
			values.append(data)
		try:
			self.answerDao.insertMany(values)
			self.connection.commit()
			return errorCodes.OK
		except Exception as e:
			return self.connection.rollback()
			self.log.error(e)
			raise e

	#指定ユーザの指定時刻以降の回答を取得
	def _updateAnswer(self, user, time):
		flg = False
		page = 1
		lastAdd = datetime.datetime.now(JST)
		while True:
			try:
				answers = peing.getAnswers(user.account, page=page)
			except Exception as e:
				self.connection.rollback()
				self.log.error(e)
				return errorCodes.PEING_ERROR
			for answer in answers:
				answered_at = datetime.datetime.fromisoformat(answer["answer_created_at"])
				if answered_at <= time:		#これより先は前回以前に取得済みのため扶養
					flg = True
					break
				if lastAdd >= answered_at: # このループ中に追加の質問回答をした場合に発生する重複受信
					continue
				data = (answer["answer_id"],user["id"], answer["body"], answer["answer_body"], answered_at)
				try:
					self.answerDao.insert(data)
				except Exception as e:
					return self.connection.rollback()
					self.log.error(e)
					raise e
				lastAdd = answered_at
			if flg:
				break
			page += 1
		self.connection.commit()
		return errorCodes.OK

	#
	#	ビュー補助
	#

	def makeContextMenu(self):
		helper=views.main.Menu("mainView")
		menu=wx.Menu()
		helper.RegisterMenuCommand(menu,[
			"FILE_SHOW_DETAIL"
		])
		return menu

	#
	#	内部用
	#
	#sqlite3.Rowからentity.user.Userに変換
	def _createUserObj(self,user):
		try:
			return entity.user.User(user["id"],user["name"],user["account"],user["items"],user["answers"],user["profile"],user["followees"])
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
