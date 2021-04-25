# -*- coding: utf-8 -*-
# 登録候補ユーザ一覧ダイアログ
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import wx

import constants
import simpleDialog
import views.ViewCreator

from views.baseDialog import *


class Dialog(BaseDialog):
	def __init__(self,lst):
		super().__init__("candidateUserListDialog")
		self.lst = lst

	def Initialize(self,title=_("登録候補ユーザの確認"),parent=None):
		if parent == None:
			parent = self.app.hMainView.hFrame
		self.log.debug("created")
		super().Initialize(parent,title)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,0,style=wx.EXPAND|wx.ALL,margin=20)
		self.hListCtrl, self.hStatic = self.creator.listCtrl(_("登録候補ユーザ"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,size=(650,-1))
		self.hListCtrl.AppendColumn(_("表示名"),width=350)
		self.hListCtrl.AppendColumn(_("アカウント"),width=280)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.close)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)

		for user in self.lst:
			self.hListCtrl.Append((user.name,user.account))

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT,margin=20)
		self.detailButton = self.creator.button(_("詳細"), self.detail)
		self.removeButton = self.creator.button(_("削除"), self.remove)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALL|wx.RIGHT,margin=20)
		self.bOk=self.creator.okbutton(_("登録(&R)"), self.close)
		self.bCancel=self.creator.cancelbutton(_("キャンセル(&C)"))

		self.onItemSelected()

	def onItemSelected(self, event=None):
		selected = self.hListCtrl.GetFocusedItem()
		self.detailButton.Enable(selected >= 0)
		self.removeButton.Enable(selected >= 0)

	def remove(self,event):
		user = self.lst[self.hListCtrl.GetFocusedItem()]
		ret = simpleDialog.yesNoDialog(_("ユーザの削除"),_("以下のユーザを登録候補の一覧から削除しますか？\n\n%s")%user.getViewString(),self.wnd)
		if ret == wx.ID_NO:
			return
		self.lst.remove(user)
		self.hListCtrl.DeleteItem(self.hListCtrl.GetFocusedItem())

	def detail(self,event):
		d = views.userDetailDialog.Dialog(self.lst[self.hListCtrl.GetFocusedItem()])
		d.Initialize(self.wnd)
		d.Show()

	def close(self,event):
		ret = simpleDialog.yesNoDialog(_("一括登録の確認"),_("表示している%d件のアカウントを登録しますか？") % len(self.lst),self.wnd)
		if ret == wx.ID_NO:
			return
		event.Skip()

	def GetData(self):
		return self.lst
