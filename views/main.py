﻿# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2022 yamahubuki <itiro.ishino@gmail.com>


import wx
import re
import simpleDialog
import webbrowser

import ConfigManager
import constants
import entity.answer
import errorCodes
import filter
import globalVars
import menuItemsStore
import service
import update

from .base import *
from simpleDialog import *
from views import accountSettingsDialog
from views import answerDialog
from views import candidateUserListDialog
from views import detailDialog
from views import globalKeyConfig
from views import listConfigurationDialog
from views import progress
from views import searchConditionDialog
from views import sentQuestionDialog
from views import settingsDialog
from views import SimpleInputDialog
from views import userDetailDialog
from views import userListDialog
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

		self.lst,dummy = self.creator.virtualListCtrl("",style=wx.LC_SINGLE_SEL|wx.LC_REPORT,proportion=1,sizerFlag=wx.EXPAND,textLayout=None)
		self.creator.GetPanel().Layout()

		self.lst.AppendColumn("名前",width=200)
		self.lst.AppendColumn("質問",width=200)
		self.lst.AppendColumn("回答",width=200)
		self.lst.AppendColumn("日時",width=320)
		self.lst.AppendColumn("種別",width=130)
		self.lst.loadColumnInfo(self.identifier, "lst")
		self.lst.Bind(wx.EVT_CONTEXT_MENU, self.events.ContextMenu)
		self.lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.events.listActivated)
		self.lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.events.listSelectEvent)
		self.lst.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.events.listSelectEvent)
		self.lst.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.events.updateFocus)
		self.events.listSelectEvent()		#最初に１度実行し、未選択状態をメニューに反映

		self.hFrame.CreateStatusBar()

		self.hFrame.Bind(wx.EVT_MENU_OPEN, self.events.OnMenuOpen)

		self.refresh()

		# 最終閲覧位置への復帰
		index = self.app.config.getint(self.identifier,"last_cursor_item",-1)
		if self.app.config.getboolean("general","keep_cursor",True) and index in self.answerIdList:
			index = self.answerIdList.index(index)
			self.lst.Select(index)
			self.lst.Focus(index)

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
			s=entity.answer.getTypeString(i[5])
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

	#表示情報タプルiを基に、有効になっているフィルタにかけた結果、表示すべきか否かを判断して返す
	def testFilter(self,i):
		for f in filter.getFilterList():
			if not f.test(userId=i[6],answerFlag=i[5],q=i[2],a=i[3]):
				return False
		return True

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニュー内容をいったんクリア
		self.hMenuBar=wx.MenuBar()

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hFilterMenu=wx.Menu()
		self.hAccountMenu=wx.Menu()
		self.hOptionMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu,[
			"FILE_ADD_USER",
			"FILE_POST_QUESTION",
			"FILE_RELOAD",
			"FILE_DELETE_USER",
			"FILE_SHOW_DETAIL",
			"FILE_SHOW_USER_DETAIL",
			"FILE_SHOW_USER_WEB",
			"FILE_EXPORT",
			"FILE_USER_LIST",
			"FILE_ADD_USER_FROM_TWITTER_FOLLOW_LIST",
			"FILE_EXIT",
		])

		self.RegisterMenuCommand(self.hOptionMenu,[
			"OPTION_OPTION",
			"OPTION_LIST_CONFIG",
			"OPTION_KEY_CONFIG",

		])

		#フィルタメニュー
		self.RegisterCheckMenuCommand(self.hFilterMenu,[
			"FILTER_AUTO_QUESTION",
			"FILTER_BATON",
			"FILTER_USER",
			"FILTER_SEARCH",
		])
		self.RegisterMenuCommand(self.hFilterMenu,[
			"FILTER_CLEAR",
		])

		#アカウントメニューの中身
		self.RegisterMenuCommand(self.hAccountMenu,[
			"ACCOUNT_ANSWER",
			"ACCOUNT_ARCHIVED",
			"ACCOUNT_SENT_LIST",
			"ACCOUNT_SETTINGS",
		])

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu,[
				"HELP_UPDATE",
				"HELP_VERSIONINFO",
		])

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル(&F)"))
		self.hMenuBar.Append(self.hFilterMenu,_("フィルタ(&I)"))
		self.hMenuBar.Append(self.hAccountMenu,_("アカウント(&A)"))
		self.hMenuBar.Append(self.hOptionMenu,_("オプション(&O)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ(&H)"))
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
			d = SimpleInputDialog.Dialog(_("ユーザの追加"),_("peingページURLまたはTwitterユーザ名"))
			d.Initialize()
			r = d.Show()
			if r==wx.ID_CANCEL:
				return
			# peingではユーザ名は小文字固定で大文字はエラーとなるため対策
			prm = re.sub("https://peing.net/[^/]+/","", d.GetValue().lower())
			#先頭の@はいらないので対策。入力時はあってもなくても良い
			prm = re.sub("@?(.*)","\\1", prm)

			user = self.parent.service.getUserInfo(prm)
			if user in (errorCodes.PEING_ERROR,errorCodes.NOT_FOUND):
				self.showError(user)
				return user
			if yesNoDialog(_("ユーザ追加"),_("以下のユーザを追加しますか？\n\nID:%(id)d\n%(name)s(%(account)s)") % {"id":user.id,"name":user.name,"account":user.account},self.parent.hFrame)==wx.ID_NO:
				self.log.debug("add user:canceled by user")
				return
			ret = self.parent.service.addUser(user)
			if ret==errorCodes.OK:
				dialog(_("登録完了"),_("ユーザの登録に成功しました。今回登録したユーザの回答を表示するには、ビューを再読み込みしてください。"),self.parent.hFrame)
				self.log.info("user %s added!" % prm)
			else:
				self.showError(ret)
				self.log.error("add user:failed.")

		if selected==menuItemsStore.getRef("FILE_POST_QUESTION"):
			index = self.parent.lst.GetFirstSelected()
			target = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			self.postQuestion(target)
			return

		if selected==menuItemsStore.getRef("FILE_RELOAD"):
			return self.reload()

		if selected==menuItemsStore.getRef("FILE_DELETE_USER"):
			index = self.parent.lst.GetFirstSelected()
			user = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			ret = yesNoDialog(_("ユーザの削除"),_("以下のユーザの登録と、過去の回答履歴を削除しますか？\n\n%s")%user.getViewString(),self.parent.hFrame)

			if ret == wx.ID_NO:
				return
			self.log.debug("deleteUser:%s" % user)
			self.parent.service.deleteUser(user)
			return self.parent.refresh()

		if selected==menuItemsStore.getRef("FILE_SHOW_USER_WEB"):
			index = self.parent.lst.GetFirstSelected()
			user = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
			if user.flag&constants.FLG_USER_DISABLE==constants.FLG_USER_DISABLE:
				self.log.warning("open web:failed. user has been deleted or account changed.")
				errorDialog(_("このユーザは既に退会したか、peingIDを変更しているため開くことができません。"),self.parent.hFrame)
				return
			self.log.debug("open web:https://peing.net/"+user.account)
			webbrowser.open_new("https://peing.net/"+user.account)
			return

		if selected==menuItemsStore.getRef("FILE_SHOW_DETAIL"):
			self.listActivated()

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
			self.log.debug("export:to=%s" % d.GetPath())
			r = self.parent.service.export(d.GetPath(),self.parent.lst)
			if r != True:
				self.log.warning("export:failed. %s" % r.getErrorMessage())
				errorDialog(r.getErrorMessage(),self.parent.hFrame)

		if selected==menuItemsStore.getRef("FILE_USER_LIST"):
			users = self.parent.service.getUserList()
			d = userListDialog.Dialog(users,self.parent.service)
			d.Initialize()
			d.Show()
			self.parent.refresh()

		if selected==menuItemsStore.getRef("FILE_ADD_USER_FROM_TWITTER_FOLLOW_LIST"):
			self.log.debug("addListFromTwitterUser:start")

			# ダイアログ表示用パラメータ
			title = _("対象ユーザの指定")
			msg = _("対象アカウントの@からはじまるアカウント名を、\n改行区切りで入力してください。")
			pattern = "^(@?[a-zA-Z0-9_]*)$"
			style = wx.TE_MULTILINE
			d = views.SimpleInputDialog.Dialog(title, msg, validationPattern=pattern, style=style)
			d.Initialize()
			d.edit.SetMinSize((-1,200))
			if d.Show() == wx.ID_CANCEL:
				return
			# 改行区切りの文字列
			users = d.GetValue()
			users = users.split("\n")
			# 先頭の'@'があれば削除
			for i in range(len(users)):
				if users[i][0] == "@":
					users[i] = users[i][1:]

			d=progress.Dialog()
			d.Initialize(_("登録済みユーザのリストを取得しています。")+"...",_("ユーザの一括追加"))
			d.gauge.Hide()
			d.Show(modal=False)
			self.parent.hFrame.Disable()

			follows=set(users)

			userList = self.parent.service.getEnableUserList()
			users = set()
			if type(users)==int:
				self.showError(users,d.wnd)
				self.parent.hFrame.Enable()
				d.Destroy()
				return
			for user in userList:
				users.add(user.account.lower())
			target = follows - users

			d.update(label=_("Peingへの登録状況を調べています。")+"...",max=len(target))
			d.gauge.Show()
			d.panel.Layout()
			d.sizer.Fit(d.wnd)
			result = []
			for i,account in enumerate(target):
				d.update(i)
				wx.YieldIfNeeded()
				info = self.parent.service.getUserInfo(account)
				if not d.isOk():
					break
				elif info == errorCodes.NOT_FOUND:
					continue
				elif info == errorCodes.PEING_ERROR:
					dialog(_("通信エラー"),_("Peingとの通信でエラーが発生しました。インターネット接続を確認し、しばらくたってから再度お試しください。状況が改善しない場合は、Twitterでのフォロー数が多すぎる可能性があります。\n\nこのメッセージを閉じた後、もしもこのエラー発生時までに取得できたアカウントがあれば一覧が表示されます。"),self.parent.hFrame)
					break
				result.append(info)

			if len(result)==0:
				dialog(_("処理終了"),_("一括登録を試みましたが、登録の候補となるユーザが見つかりませんでした。"),d.wnd)
				self.parent.hFrame.Enable()
				d.Destroy()
				return

			d2 = candidateUserListDialog.Dialog(result)
			d2.Initialize(parent=d.wnd)
			r = d2.Show()
			if r==wx.ID_CANCEL:
				self.parent.hFrame.Enable()
				d.Destroy()
				return

			#登録
			if len(d2.GetValue())>0:
				d.update(0,_("指定されたユーザを登録しています。"),len(d2.GetValue()))
				for i,user in enumerate(d2.GetValue()):
					self.parent.service.addUser(user)
					d.update(i)
					wx.YieldIfNeeded()
				dialog(_("登録完了"),_("ユーザの一括登録に成功しました。今回登録したユーザの回答を表示するには、ビューを再読み込みしてください。"),d.wnd)

			self.parent.hFrame.Enable()
			d.Destroy()


		if selected==menuItemsStore.getRef("FILE_EXIT"):
			self.parent.hFrame.Close()

		if selected==menuItemsStore.getRef("FILE_OPEN_CONTEXTMENU"):
			if self.parent.lst.HasFocus() == True and self.parent.lst.GetFirstSelected() >= 0:
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
			if event.IsChecked():
				index = self.parent.lst.GetFirstSelected()
				target = self.parent.service.getAnswer(self.parent.answerIdList[index]).user
				self.log.debug("set userFilter = "+str(target.id))
				filter.UserFilter(target).enable(event.IsChecked())
			else:
				self.log.debug("set userFilter = "+str(event.IsChecked()))
				filter.UserFilter().enable(event.IsChecked())
			self.parent.refresh()
			event.Skip()

		if selected==menuItemsStore.getRef("FILTER_SEARCH"):
			if event.IsChecked():
				d = views.searchConditionDialog.Dialog()
				d.Initialize()
				if d.Show() == wx.ID_CANCEL:
					return
				self.log.debug("set searchFilter = "+str(d.GetValue()))
				filter.SearchFilter(*d.GetValue()).enable(event.IsChecked())
			else:
				self.log.debug("set searchFilter = "+str(event.IsChecked()))
				filter.SearchFilter().enable(event.IsChecked())
			self.parent.refresh()
			event.Skip()

		if selected == menuItemsStore.getRef("FILTER_CLEAR"):
			self.log.debug("Clear Filter")
			for f in filter.getFilterList():
				f.enable(False)
			self.parent.refresh()
			event.Skip()

		if selected == menuItemsStore.getRef("ACCOUNT_ANSWER"):
			if not self.loginCheck():
				return
			d = answerDialog.Dialog(self.parent.service,constants.RECEIVED)
			if d.Initialize()==errorCodes.OK:
				d.Show()
			else:
				errorDialog(_("質問の取得に失敗しました。以下の対処をお試しください。\n\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),self.parent.hFrame)

		if selected == menuItemsStore.getRef("ACCOUNT_ARCHIVED"):
			if not self.loginCheck():
				return
			d = answerDialog.Dialog(self.parent.service,constants.ARCHIVED)
			if d.Initialize()==errorCodes.OK:
				d.Show()
			else:
				errorDialog(_("質問の取得に失敗しました。以下の対処をお試しください。\n\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),self.parent.hFrame)

		if selected == menuItemsStore.getRef("ACCOUNT_SENT_LIST"):
			if not self.loginCheck():
				return
			d = sentQuestionDialog.Dialog(self.parent.service)
			if d.Initialize()==errorCodes.OK:
				d.Show()
			else:
				errorDialog(_("質問の取得に失敗しました。以下の対処をお試しください。\n\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),self.parent.hFrame)

		if selected == menuItemsStore.getRef("ACCOUNT_SETTINGS"):
			if not self.loginCheck():
				return
			d = accountSettingsDialog.Dialog(self.parent.service)
			if d.Initialize()==errorCodes.OK:
				if d.Show()==wx.ID_CANCEL:
					return
			else:
				errorDialog(_("ログインまたはアカウント設定の取得に失敗しました。以下の対処をお試しください。\n\n・設定されたアカウント情報が誤っていないか、設定画面から再度ご確認ください。\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),self.parent.hFrame)
				return
			ret = self.parent.service.setProfile(d.GetValue())
			if ret == errorCodes.OK:
				dialog(_("設定完了"),_("設定しました。"))
			else:
				self.showError(ret)

		if selected == menuItemsStore.getRef("OPTION_OPTION"):
			d = settingsDialog.Dialog()
			d.Initialize()
			if d.Show()==wx.ID_OK:
				self.log.debug("setting dialog returned ID_OK. logout session.")
				self.parent.service.logout()

		if selected == menuItemsStore.getRef("OPTION_KEY_CONFIG"):
			if self.setKeymap(self.parent.identifier,_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
				#ショートカットキーの変更適用とメニューバーの再描画
				self.parent.menu.InitShortcut()
				self.parent.menu.ApplyShortcut(self.parent.hFrame)
				self.parent.menu.Apply(self.parent.hFrame)

		if selected == menuItemsStore.getRef("OPTION_LIST_CONFIG"):
			d = listConfigurationDialog.Dialog(self.parent.lst)
			d.Initialize()
			d.Show()

		if selected == menuItemsStore.getRef("HELP_UPDATE"):
			update.checkUpdate()

		if selected==menuItemsStore.getRef("HELP_VERSIONINFO"):
			d = versionDialog.versionDialog()

	def ContextMenu(self,event):
		if self.parent.lst.HasFocus() == True and self.parent.lst.GetFirstSelected() >= 0:
			menu=self.parent.service.makeContextMenu()
			self.parent.lst.PopupMenu(menu,event)

	#lst上でのEnterキー処理
	def listActivated(self,event=None):
		index = self.parent.lst.GetFirstSelected()
		answer = self.parent.service.getAnswer(self.parent.answerIdList[index])
		d = detailDialog.Dialog(answer)
		d.Initialize()
		d.Show()
		return

	#lst上での項目選択/選択解除
	def listSelectEvent(self,event=None):
		enable = self.parent.lst.HasFocus() == True and self.parent.lst.GetFirstSelected() >= 0
		self.parent.menu.EnableMenu([
			"FILE_POST_QUESTION",
			"FILE_DELETE_USER",
			"FILE_SHOW_DETAIL",
			"FILE_SHOW_USER_DETAIL",
			"FILE_SHOW_USER_WEB",
			"FILTER_USER",
		], enable)

		self.parent.menu.EnableMenu([
			"FILTER_CLEAR",
		], (filter.getFilterList()))

	def OnMenuOpen(self,event):
		menuObject = event.GetEventObject()
		if event.GetMenu()==self.parent.menu.hFilterMenu:
			menuObject.Check(menuItemsStore.getRef("FILTER_AUTO_QUESTION"),filter.AutoQuestionFilter().isEnable())
			menuObject.Check(menuItemsStore.getRef("FILTER_BATON"),filter.BatonFilter().isEnable())
			menuObject.Check(menuItemsStore.getRef("FILTER_USER"),filter.UserFilter().isEnable())
			menuObject.Check(menuItemsStore.getRef("FILTER_SEARCH"),filter.SearchFilter().isEnable())


	def reload(self):
		self.log.debug("reload:start")
		d=progress.Dialog()
		d.Initialize(_("準備中")+"...",_("回答データを取得しています")+"...")
		d.Show(modal=False)
		self.parent.hFrame.Disable()
		ret = errorCodes.OK

		users = self.parent.service.getEnableUserList()
		for i,user in enumerate(users):
			d.update(None,"%d / %d " % (i+1,len(users)) + user.getViewString())
			info = self.parent.service.getUserInfo(user.account)
			if info==errorCodes.NOT_FOUND:
				d.update(i+1,None,len(users))
				self.log.info("skip update because user not found:"+user.account)
				continue
			elif info==errorCodes.PEING_ERROR:
				ret = info
				break
			elif info.id!=user.id:		#当該アカウント名が別ユーザの登録にかわっている
				user.flag|=constants.FLG_USER_DISABLE
				self.log.warning("add exclude flag:"+user.account)
				self.parent.service.updateUserInfo(user)
				dialog(_("登録ユーザの更新除外について"),_("登録していた以下のユーザは、アカウント名が変更されたか、削除されました。その後、同一アカウント名を別のユーザが取得しているため、今後このアカウントの回答は更新から除外します。もし、再取得したアカウントが同一人物であるなど今後もこのアカウントの回答の更新を希望する場合には、再度ユーザ追加を行ってください。\n\n該当ユーザ：%s") % user.getViewString())
				d.update(i+1,None,len(users))
				continue
			else:
				self.parent.service.updateUserInfo(info)

			ret = self.parent.service.update(user)
			if ret!=errorCodes.OK or (not d.isOk()):
				break
			d.update(i+1,None,len(users))

		self.showError(ret,d.wnd)
		self.parent.refresh()

		self.parent.hFrame.Enable()
		d.Destroy()


	#targetで指定したユーザに対して質問を投稿する
	def postQuestion(self,target,parent=None):
		useSession = self.parent.app.config.getboolean("account","use_always",False)
		if useSession:
			if not self.loginCheck():
				return

		style = 0
		if self.parent.app.config.getboolean("view", "enableMultiline", False):
			style = wx.TE_MULTILINE
		d = SimpleInputDialog.Dialog(_("質問を投稿"),_("%sさんへの質問内容") % target.getViewString(), parent, style=style)
		d.Initialize()
		r = d.Show()
		if r==wx.ID_CANCEL:
			return
		prm=d.GetValue()
		self.log.debug("post question:%s,%s" % (target,prm))
		if useSession:
			if not self.loginCheck():
				return
		ret = self.parent.service.postQuestion(target,prm,useSession)
		if ret == errorCodes.OK:
			dialog(_("投稿完了"),_("質問を投稿しました。"))
			self.log.debug("post question success")
		else:
			self.showError(ret)

	#エラーコードを受け取り、必要があればエラー表示
	def showError(self,code,parent=None):
		if parent==None:
			parent=self.parent.hFrame
		if code==None:
			code=errorCodes.UNKNOWN

		if code!=errorCodes.OK:
			self.log.warning("show error:%d" % code)
		if code==errorCodes.PEING_ERROR or code==errorCodes.NOT_FOUND:
			errorDialog(_("指定されたユーザが存在しないか、通信に失敗しました。以下の対処をお試しください。\n\n・入力内容が正しいか、再度お確かめください。\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),parent)
		elif code==errorCodes.TWITTER_ERROR:
			errorDialog(_("Twitterとの通信でエラーが発生しました。指定したユーザ名が間違っているか、インターネット接続に問題が発生した可能性があります。"),parent)
		elif code==errorCodes.LOGIN_WRONG_PASSWORD:
			errorDialog(_("ログインに失敗しました。設定されたアカウント情報に誤りがあります。\n\n・設定内容が正しいか、設定したものと同じ情報でブラウザからログインできるかを再度確認してください。\n・ブラウザから正しくログインできる場合には、サイトの仕様変更が考えられます。このメッセージと使用したIDの種類を添えて開発者までお問い合わせください。\n"),parent)
		elif code==errorCodes.LOGIN_CONFIRM_NEEDED:
			errorDialog(_("ログインに失敗しました。ログインに際して権限の認可が要求されています。同じIDでブラウザからログインした後、再度お試しください。"),parent)
		elif code==errorCodes.LOGIN_PEING_ERROR:
			errorDialog(_("ログインに失敗しました。Peingのサーバやお使いのインターネット接続に障害が発生している可能性があります。ブラウザから同じIDでログインできるか確認してください。\nブラウザから正常にログインできる場合には、サイトの仕様変更が考えられますので、このメッセージと利用したIDの種類を添えて開発者までお問い合わせください。"),parent)
		elif code==errorCodes.LOGIN_TWITTER_ERROR:
			errorDialog(_("ログインに失敗しました。Twitterのサーバやお使いのインターネット接続に障害が発生している可能性があります。ブラウザから同じIDでログインできるか確認してください。\nブラウザから正常にログインできる場合には、サイトの仕様変更が考えられますので、このメッセージと利用したIDの種類を添えて開発者までお問い合わせください。"),parent)
		elif code==errorCodes.LOGIN_UNKNOWN_ERROR:
			errorDialog(_("不明なエラーの為、ログインに失敗しました。サイトの仕様変更や、お使いのインターネット接続の障害が考えられます。まずは、ブラウザから同じIDでログインできるか確認してください。\nブラウザから正常にログインできる場合には、サイトの仕様変更が考えられますので、このメッセージと利用したIDの種類を添えて開発者までお問い合わせください。"),parent)
		elif code==errorCodes.LOGIN_RECAPTCHA_NEEDED:
			errorDialog(_("ログインに失敗しました。ログインに際してRECAPTCHA(ロボットでないことの確認)が要求されています。同じIDでブラウザからログインした後、再度お試しください。"),parent)
		elif code == errorCodes.DUPLICATED:
			errorDialog(_("指定されたユーザは既に登録済みです。"))
		elif code != errorCodes.OK:
			errorDialog(_("不明なエラー%(code)dが発生しました。大変お手数ですが、本ソフトの実行ファイルのあるディレクトリに生成された%(log)sを添付し、作者までご連絡ください。") %{"code":code,"log":constants.LOG_FILE_NAME},parent)
		return

	def OnExit(self, event):
		# 最終閲覧位置を記録
		index = self.parent.lst.GetFirstSelected()
		if index >= 0:
			self.parent.app.config[self.parent.identifier]["last_cursor_item"] = self.parent.answerIdList[index]

		# リスト表示設定の保存
		self.parent.lst.saveColumnInfo()

		super().OnExit(event)

	def setKeymap(self, identifier,ttl, keymap=None,filter=None):
		if keymap:
			try:
				keys=keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		else:
			try:
				keys=self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		keyData={}
		menuData={}
		for refName in defaultKeymap.defaultKeymap[identifier].keys():
			title=menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title]=keys[refName]
			else:
				keyData[title]=_("なし")
			menuData[title]=refName

		d=views.globalKeyConfig.Dialog(keyData,menuData,[],filter)
		d.Initialize(ttl)
		if d.Show()==wx.ID_CANCEL: return False

		keyData,menuData=d.GetValue()

		#キーマップの既存設定を置き換える
		newMap=ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name,key in keyData.items():
			if key!=_("なし"):
				newMap[identifier.upper()][menuData[name]]=key
			else:
				newMap[identifier.upper()][menuData[name]]=""
		if newMap.write() != errorCodes.OK:
			errorDialog(_("設定の保存に失敗しました。下記のファイルへのアクセスが可能であることを確認してください。") + "\n" + self.config.getAbsFileName())
		return True

	# ログイン状態を確認し、必要ならログインする
	def loginCheck(self):
		ret = self.parent.app.config.getstring("account","id")!="" and self.parent.app.config.getstring("account","password")!=""
		if not ret:
			errorDialog(_("この機能を利用するには、ログインが必要です。\n[オプション]→[設定]にて、アカウント情報を設定してください。詳細は、readme.txtをご確認ください。"))
			return False

		ret = self.parent.service.login(
			constants.LOGIN_PEING,
			self.parent.app.config.getstring("account","id"),
			self.parent.app.config.getstring("account","password")
		)
		if ret != errorCodes.OK:
			self.log.error("login failed")
			self.showError(ret)
			return False
		return True

	def updateFocus(self, event):
		if event.GetIndex():
			self.parent.hFrame.SetStatusText(_("%d個中%d個目を選択中" % (self.parent.lst.GetItemCount(), event.GetIndex())))
		else:
			self.parent.hFrame.SetStatusText(_("%d個表示中、選択項目なし" % self.parent.lst.GetItemCount()))

