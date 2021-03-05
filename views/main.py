# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import logging
import os
import sys
import wx
import re
import ctypes
import pywintypes
import simpleDialog
import webbrowser

import constants
import errorCodes
import filter
import globalVars
import menuItemsStore
import service

from .base import *
from simpleDialog import *
from views import detailDialog
from views import progress
from views import SimpleImputDialog
from views import userDetailDialog
from views import versionDialog


class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800,400),
			self.app.config.getint(self.identifier,"sizeY",600,300),
			self.app.config.getint(self.identifier,"positionX",50,0),
			self.app.config.getint(self.identifier,"positionY",50,0)
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)

		self.service=service.Service()
		self.answerIdList=[]

		self.lst,dummy = self.creator.virtualListCtrl("",style=wx.LC_SINGLE_SEL|wx.LC_REPORT,proportion=1,sizerFlag=wx.EXPAND)
		self.creator.GetPanel().Layout()

		self.lst.AppendColumn("名前",width=200)
		self.lst.AppendColumn("質問",width=200)
		self.lst.AppendColumn("回答",width=200)
		self.lst.AppendColumn("日時",width=200)
		self.lst.AppendColumn("種別",width=100)
		self.lst.Bind(wx.EVT_CONTEXT_MENU, self.events.ContextMenu)

		self.refresh()

	#DBの内容でビューを更新する
	def refresh(self):
		self.log.debug("refresh view")
		index = self.lst.GetFirstSelected()
		if index!=-1:
			index=self.answerIdList[index]

		data=self.service.getViewData()
		self.answerIdList=[]
		self.lst.DeleteAllItems()
		for i in data:
			s=self.answerFlag2String(i[5])
			if not self.testFilter(i):
				continue
			self.lst.Append((i[1],i[2],i[3],i[4],s))
			self.answerIdList.append(i[0])

		if index!=-1:
			for i,id in enumerate(self.answerIdList):
				if id <= index:
					self.lst.Select(i)
					self.lst.Focus(i)
					break
		self.lst.SetFocus()
		self.log.debug("refresh finished.")
		return 

	def answerFlag2String(self,flag):
		ret=[]
		dic={
			constants.FLG_ANSWER_AUTOQUESTION:_("運営"),
			constants.FLG_ANSWER_BATON_QUESTION:_("バトン"),
		}
		for i,s in dic.items():
			if flag&i==i:
				ret.append(s)
		return ",".join(ret)

	#表示情報タプルiを基に、有効になっているフィルタにかけた結果、表示すべきか否かを判断して返す
	def testFilter(self,i):
		for f in filter.getFilterList():
			if not f.test(userId=i[6],answerFlag=i[5]):
				return False
		return True

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hFilterMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu,[
			"FILE_ADD_USER",
			"FILE_POST_QUESTION",
			"FILE_RELOAD",
			"FILE_DELETE_USER",
			"FILE_SHOW_DETAIL",
			"FILE_SHOW_USER_DETAIL",
			"FILE_EXPORT",
			"FILE_EXIT",
		])

		#フィルタメニュー
		self.RegisterCheckMenuCommand(self.hFilterMenu,[
			"FILTER_AUTO_QUESTION",
			"FILTER_BATON",
			"FILTER_USER",
		])

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu,[
				"HELP_UPDATE",
				"HELP_VERSIONINFO",
		])

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル"))
		self.hMenuBar.Append(self.hFilterMenu,_("フィルタ"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る

		if selected==menuItemsStore.getRef("FILE_ADD_USER"):
			d = SimpleImputDialog.Dialog("ユーザの追加","peingページURLまたはTwitterユーザ名")
			d.Initialize()
			r = d.Show()
			if r==wx.ID_CANCEL:
				return
			prm=d.GetValue()
			#TODO:URLでの登録に対応する
			if self.parent.service.isUserRegistered(prm)==True:
				errorDialog(_("指定されたユーザは既に登録済みです。"),self.parent.hFrame)
				return errorCodes.DUPLICATED
			user = self.parent.service.getUserInfo(prm)
			if user in (errorCodes.PEING_ERROR,errorCodes.NOT_FOUND):
				self.showError(user)
				return user
			if yesNoDialog(_("ユーザ追加"),_("以下のユーザを追加しますか？\n\nID:%d\n%s(%s)") % (user.id,user.name,user.account),self.parent.hFrame)==wx.ID_NO:
				return
			if self.parent.service.addUser(user)==errorCodes.OK:
				dialog(_("登録完了"),_("ユーザの登録に成功しました。今回登録したユーザの回答を表示するには、ビューを再読み込みしてください。"),self.parent.hFrame)
			else:
				errorDialog(_("ユーザの登録に失敗しました。"),self.parent.hFrame)

		if selected==menuItemsStore.getRef("FILE_POST_QUESTION"):
			index = self.parent.lst.GetFirstSelected()
			target = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			d = SimpleImputDialog.Dialog("質問を投稿",_("%sさんへの質問内容") % target.getViewString())
			d.Initialize()
			r = d.Show()
			if r==wx.ID_CANCEL:
				return
			prm=d.GetValue()
			ret = self.parent.service.postQuestion(target,prm)
			if ret == errorCodes.OK:
				dialog(_("投稿完了"),_("質問を投稿しました。"))
			else:
				self.showError(ret)

		if selected==menuItemsStore.getRef("FILE_RELOAD"):
			d=progress.Dialog()
			d.Initialize(_("準備中")+"...",_("回答データを取得しています")+"...")
			d.Show(modal=False)
			self.parent.hFrame.Disable()
			ret = errorCodes.OK

			users = self.parent.service.getEnableUserList()
			for i,user in enumerate(users):
				d.update(None,user.getViewString())
				info = self.parent.service.getUserInfo(user.account)
				if info==None:
					d.update(i,None,len(users))
					self.log.info("skip update because user not found:"+user.account)
					continue
				elif info.id!=user.id:		#当該アカウント名が別ユーザの登録にかわっている
					info.flag|=constants.FLG_USER_DISABLE
					self.log.warning("add exclude flag:"+user.account)
					self.parent.service.updateUserInfo(info)
					dialog(_("登録ユーザの更新除外について"),_("登録していた以下のユーザは、アカウント名が変更されたか、削除されました。その後、同一アカウント名を別のユーザが取得しているため、今後このアカウントの回答は更新から除外します。もし、再取得したアカウントが同一人物であるなど今後もこのアカウントの回答の更新を希望する場合には、再度ユーザ追加を行ってください。\n\n該当ユーザ：%s") % user.getViewString())
					d.update(i,None,len(users))
					continue
				else:
					self.parent.service.updateUserInfo(info)

				ret = self.parent.service.update(user)
				if ret!=errorCodes.OK or (not d.isOk()):
					break
				d.update(i,None,len(users))

			self.showError(ret,d.wnd)
			self.parent.refresh()

			self.parent.hFrame.Enable()
			d.Destroy()

		if selected==menuItemsStore.getRef("FILE_DELETE_USER"):
			index = self.parent.lst.GetFirstSelected()
			user = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			ret = yesNoDialog(_("ユーザの削除"),_("以下のユーザの登録と、過去の回答履歴を削除しますか？\n\n%s")%user.getViewString())
			if ret == wx.ID_NO:
				return
			self.parent.service.deleteUser(user)
			self.parent.refresh()

		if selected==menuItemsStore.getRef("FILE_SHOW_USER_WEB"):
			index = self.parent.lst.GetFirstSelected()
			user = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			if user.flag&constants.FLG_USER_DISABLE==constants.FLG_USER_DISABLE:
				errorDialog(_("このユーザは既に退会したか、peingIDを変更しているため開くことができません。"))
				return
			webbrowser.open_new("https://peing.net/"+user.account)
			return

		if selected==menuItemsStore.getRef("FILE_SHOW_DETAIL"):
			index = self.parent.lst.GetFirstSelected()
			answer = self.parent.service.getAnswer(self.parent.answerIdList[index])
			d = detailDialog.Dialog(answer)
			d.Initialize()
			d.Show()
			return

		if selected==menuItemsStore.getRef("FILE_SHOW_USER_DETAIL"):
			index = self.parent.lst.GetFirstSelected()
			user = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			d = userDetailDialog.Dialog(user)
			d.Initialize()
			d.Show()
			return

		if selected==menuItemsStore.getRef("FILE_EXPORT"):
			d = wx.FileDialog(None, _("出力先ファイルの指定"), style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT, wildcard=_("CSVファイル(*.csv) | *.csv; | すべてのファイル(*.*) | *.*"))
			if d.ShowModal() == wx.ID_CANCEL:
				return
			r = self.parent.service.export(d.GetPath(),self.parent.lst)
			if r != True:
				errorDialog(r,self.parent.hFrame)

		if selected==menuItemsStore.getRef("FILE_EXIT"):
			self.parent.hFrame.Close()

		if selected==menuItemsStore.getRef("FILE_OPEN_CONTEXTMENU"):
			menu=self.parent.service.makeContextMenu()
			self.parent.lst.PopupMenu(menu,self.parent.lst.getPopupMenuPosition())


		if selected==menuItemsStore.getRef("FILTER_AUTO_QUESTION"):
			self.log.debug("set autoQuestionFilter = "+str(event.IsChecked()))
			filter.AutoQuestionFilter().enable(event.IsChecked())
			self.parent.refresh()
			event.Skip()

		if selected==menuItemsStore.getRef("FILTER_BATON"):
			self.log.debug("set battonFilter = "+str(event.IsChecked()))
			filter.BatonFilter().enable(event.IsChecked())
			self.parent.refresh()
			event.Skip()

		if selected==menuItemsStore.getRef("FILTER_USER"):
			index = self.parent.lst.GetFirstSelected()
			target = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			if event.IsChecked():
				self.log.debug("set userFilter = "+str(target.id))
				filter.UserFilter(target).enable(event.IsChecked())
			else:
				self.log.debug("set battonFilter = "+str(event.IsChecked()))
				filter.UserFilter(0).enable(event.IsChecked())
			self.parent.refresh()
			event.Skip()


		if selected == menuItemsStore.getRef("HELP_UPDATE"):
			globalVars.update.update()

		if selected==menuItemsStore.getRef("HELP_VERSIONINFO"):
			d = versionDialog.versionDialog()

	def ContextMenu(self,event):
		menu=self.parent.service.makeContextMenu()
		self.parent.lst.PopupMenu(menu,event)

	#エラーコードを受け取り、必要があればエラー表示
	def showError(self,code,parent=None):
		if parent==None:
			parent=self.parent.hFrame
		if code==None:
			code=errorCodes.UNKNOWN

		if code==errorCodes.OK:
			return
		elif code==errorCodes.PEING_ERROR or code==errorCodes.NOT_FOUND:
			errorDialog(_("指定されたユーザが存在しないか、通信に失敗しました。以下の対処をお試しください。\n\n・入力内容が正しいか、再度お確かめください。\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),parent)
		else:
			errorDialog(_("不明なエラー%dが発生しました。大変お手数ですが、本ソフトの実行ファイルのあるディレクトリに生成された%sを添付し、作者までご連絡ください。") %(code,constants.LOG_FILE_NAME),parent)
		return
