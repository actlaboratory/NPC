# -*- coding: utf-8 -*-
# 回答ダイアログ
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import wx

import errorCodes
import filter
import simpleDialog
import views.ViewCreator
import views.SimpleImputDialog

from views.baseDialog import *


class Dialog(BaseDialog):
	def __init__(self,service,type=type):
		super().__init__("answerDialog")
		self.service = service
		self.type=type
		self.lst=[]

	def Initialize(self,parent=None):
		if parent == None:
			parent = self.app.hMainView.hFrame
		self.log.debug("created")
		super().Initialize(parent,self.getListTitle())
		self.InstallControls()
		return self.load()

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,0,style=wx.EXPAND|wx.ALL,margin=20)
		self.hListCtrl, self.hStatic = self.creator.listCtrl(self.getListTitle(), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,size=(650,-1))
		self.hListCtrl.AppendColumn(_("質問"),width=400)
		self.hListCtrl.AppendColumn(_("日時"),width=100)
		self.hListCtrl.AppendColumn(_("種別"),width=150)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.close)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT,margin=20)
		self.answerButton = self.creator.button(_("回答する(&A)"), self.answer)
		if self.type == constants.RECEIVED:
			self.archiveButton = self.creator.button(_("アーカイブ"), self.archive)
		elif self.type == constants.ARCHIVED:
			self.archiveButton = self.creator.button(_("元に戻す"), self.recycle)
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT,margin=20)
		self.bOk=self.creator.okbutton(_("閉じる(&C)"), self.close)

		self.onItemSelected()

	# self.typeに応じて適切なリストビューのタイトルを返す
	def getListTitle(self):
		if self.type == constants.RECEIVED:
			return _("未回答の質問")
		elif self.type == constants.ARCHIVED:
			return _("アーカイブ済みの質問")
		else:
			raise ValueError

	def close(self,event):
		self.wnd.EndModal(wx.ID_OK)

	def onItemSelected(self, event=None):
		selected = self.hListCtrl.GetFocusedItem()
		self.answerButton.Enable(selected >= 0)
		self.archiveButton.Enable(selected >= 0)

	def load(self):
		ret = self.service.login(self.app.config.getstring("account","id"),self.app.config.getstring("account","password"))
		if ret != errorCodes.OK:
			self.log.error("login failed")
			return ret
		if self.type == constants.RECEIVED:
			qList = self.service.getReceivedItemList()
		elif self.type == constants.ARCHIVED:
			qList = self.service.getArchivedItemList()
		else:
			raise ValueError
		if type(qList)!=list:
			return qList
		for q in qList:
			self.hListCtrl.Append((q.question,q.answered_at,q.getTypeString()))
			self.lst.append(q)
		return errorCodes.OK

	def answer(self,event):
		q = self.lst[self.hListCtrl.GetFocusedItem()].question
		d = views.SimpleImputDialog.Dialog(_("回答の入力"),q,self.wnd)
		d.Initialize()
		if d.Show()==wx.ID_CANCEL:
			return
		ret = self.service.answer(self.lst[self.hListCtrl.GetFocusedItem()].uuid,d.GetValue())
		if ret == errorCodes.OK:
			simpleDialog.dialog(_("回答完了"),_("回答が送信されました。"))
			self._remove()
		else:
			simpleDialog.errorDialog(_("指定された質問が存在しないか、通信に失敗しました。以下の対処をお試しください。\n\n・入力した内容が長すぎるなどの理由で、拒否されている可能性があります。\n・質問一覧を開きなおしてみてください。\n・peing.netにアクセスできるか、ブラウザから確認してください。\n・しばらくたってから再度お試しください。\n・問題が解決しない場合、開発者までお問い合わせください。"),self.wnd)

	def archive(self,event):
		q = self.lst[self.hListCtrl.GetFocusedItem()]
		ret = simpleDialog.yesNoDialog(_("質問をアーカイブ"),_("以下の質問をアーカイブしますか？\n\n%s")%q.question)
		if ret == wx.ID_NO:
			return
		self.service.archive(self.lst[self.hListCtrl.GetFocusedItem()].uuid)
		self._remove()

	def recycle(self,event):
		q = self.lst[self.hListCtrl.GetFocusedItem()]
		ret = simpleDialog.yesNoDialog(_("質問を元に戻す"),_("以下の質問を元に戻しますか？\n\n%s")%q.question)
		if ret == wx.ID_NO:
			return
		self.service.recycle(self.lst[self.hListCtrl.GetFocusedItem()].uuid)
		self._remove()

	def _remove(self):
		del self.lst[self.hListCtrl.GetFocusedItem()]
		self.hListCtrl.DeleteItem(self.hListCtrl.GetFocusedItem())
