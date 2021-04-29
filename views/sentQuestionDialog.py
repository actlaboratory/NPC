# -*- coding: utf-8 -*-
# 送信済質問表示ダイアログ
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import wx

import entity
import errorCodes
import filter
import simpleDialog
import views.ViewCreator
import views.SimpleImputDialog

from views.baseDialog import *
from views import detailDialog

class Dialog(BaseDialog):
	def __init__(self,service):
		super().__init__("sentQuestionDialog")
		self.service = service
		self.idList=[]

	def Initialize(self,parent=None):
		if parent == None:
			parent = self.app.hMainView.hFrame
		self.log.debug("created")
		super().Initialize(parent,_("送信した質問"))
		self.InstallControls()
		return self.load()

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,0,style=wx.EXPAND|wx.ALL,margin=20)
		self.hListCtrl, self.hStatic = self.creator.listCtrl(_("送信した質問"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,size=(650,-1))

		self.hListCtrl.AppendColumn(_("宛先"),width=300)
		self.hListCtrl.AppendColumn(_("質問"),width=300)
		self.hListCtrl.AppendColumn(_("回答"),width=300)
		self.hListCtrl.AppendColumn(_("日時"),width=200)
		self.hListCtrl.AppendColumn(_("種別"),width=100)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.close)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT,margin=20)
		self.detailButton = self.creator.button(_("詳細を表示(&D)"), self.detail)
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT,margin=20)
		self.bOk=self.creator.okbutton(_("閉じる(&C)"), self.close)

		self.onItemSelected()

	def close(self,event):
		self.wnd.EndModal(wx.ID_OK)

	def onItemSelected(self, event=None):
		selected = self.hListCtrl.GetFocusedItem()
		self.detailButton.Enable(selected >= 0)

	def load(self):
		ret = self.service.login(self.app.config.getstring("account","id"),self.app.config.getstring("account","password"))
		if ret != errorCodes.OK:
			self.log.error("login failed")
			return ret
		qList = self.service.getSentList()
		if type(qList)!=list:
			return qList
		for q in qList:
			s=entity.answer.getTypeString(q[5])
			self.hListCtrl.Append((q[1],q[2],q[3],q[4],s))

			#self.hListCtrl.Append((self.service.getUser(q.user).name,q.question,q.answer,q.answered_at))
			self.idList.append(int(q[0]))
		return errorCodes.OK

	def detail(self,event):
		index = self.hListCtrl.GetFirstSelected()
		answer = self.service.getSentAnswer(self.idList[index])
		d = detailDialog.Dialog(answer)
		d.Initialize()
		d.Show()
		return
