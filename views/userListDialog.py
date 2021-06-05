# -*- coding: utf-8 -*-
# ユーザ一覧ダイアログ
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import copy
import wx

import filter
import menuItemsStore
import simpleDialog
import views.ViewCreator

from views.baseDialog import *



class Dialog(BaseDialog):
	def __init__(self,lst,service):
		super().__init__("userListDialog")
		self.lst = lst
		self.data = copy.deepcopy(lst)
		self.service = service

	def Initialize(self,title=_("登録済みユーザ一覧"),parent=None):
		if parent == None:
			parent = self.app.hMainView.hFrame
		self.log.debug("created")
		super().Initialize(parent,title)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,0,style=wx.EXPAND|wx.ALL,margin=20)
		self.searchEdit, dummy = self.creator.inputbox(_("絞り込み"), self.search, "", sizerFlag=wx.ALL|wx.EXPAND, proportion=1, margin=5, textLayout=wx.HORIZONTAL)

		self.hListCtrl, self.hStatic = self.creator.listCtrl(_("登録済みユーザ"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,size=(650,-1))
		self.hListCtrl.AppendColumn(_("表示名"),width=350)
		self.hListCtrl.AppendColumn(_("アカウント"),width=280)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.close)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)
		self.hListCtrl.SetFocus()

		for user in self.lst:
			self.hListCtrl.Append((user.name,user.account))

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.EXPAND|wx.LEFT|wx.RIGHT,margin=20)
		self.detailButton = self.creator.button(_("詳細"), self.detail)
		self.creator.AddSpace(-1)
		self.filterButton = self.creator.button(_("フィルタ(&F)"), self.filter)
		self.creator.AddSpace(-1)
		self.removeButton = self.creator.button(_("削除"), self.remove)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALL|wx.RIGHT,margin=20)
		self.postQuestionButton = self.creator.button(_("質問を投稿(&Q)"),self.postQuestion)
		self.creator.AddSpace(-1)
		self.bOk=self.creator.closebutton(_("閉じる(&C)"), self.close)

		self.onItemSelected()


		# delキーを使えるようにする
		keymap = self.app.hMainView.menu.keymap
		keymap.Set(self.identifier,self.wnd,self.onKey)


	def close(self,event):
		self.wnd.EndModal(wx.ID_OK)

	def onItemSelected(self, event=None):
		selected = self.hListCtrl.GetFocusedItem()
		self.detailButton.Enable(selected >= 0)
		self.filterButton.Enable(selected >= 0)
		self.removeButton.Enable(selected >= 0)
		self.postQuestionButton.Enable(selected >= 0)

	def remove(self,event):
		user = self.lst[self.hListCtrl.GetFocusedItem()]
		ret = simpleDialog.yesNoDialog(_("ユーザの削除"),_("以下のユーザの登録と、過去の回答履歴を削除しますか？\n\n%s")%user.getViewString())
		if ret == wx.ID_NO:
			return
		self.service.deleteUser(user)
		self.lst.remove(user)
		self.data.remove(user)
		self.hListCtrl.DeleteItem(self.hListCtrl.GetFocusedItem())

	def detail(self,event):
		d = views.userDetailDialog.Dialog(self.lst[self.hListCtrl.GetFocusedItem()])
		d.Initialize(self.wnd)
		d.Show()

	def filter(self,event):
		target = self.lst[self.hListCtrl.GetFocusedItem()]
		self.log.debug("set userFilter = "+str(target.account))
		filter.UserFilter().enable(False)			#重複設定防止
		filter.UserFilter(target).enable(True)
		self.wnd.EndModal(wx.ID_OK)

	def postQuestion(self, event):
		target = self.lst[self.hListCtrl.GetFocusedItem()]
		self.app.hMainView.events.postQuestion(target,self.wnd)

	def onKey(self,event):
		selected=event.GetId()#メニュー識別しの数値が出る
		if self.hListCtrl.GetFocusedItem()>=0 and selected==menuItemsStore.getRef("DELETE"):
			self.remove(None)
		else:
			event.Skip()

	def search(self,event):
		if self.hListCtrl.GetFocusedItem()!=-1:
			focusedUser = self.lst[self.hListCtrl.GetFocusedItem()]
		else:
			focusedUser = None
		kwd = self.searchEdit.GetValue()

		if kwd.startswith("@"):		#ユーザ名指定
			if len(kwd)==1:			#@のみの入力では何もしない
				return
			self.lst.clear()
			for u in self.data:
				if u.account.startswith(kwd[1:]):
					self.lst.append(u)
		else:
			self.lst.clear()
			for u in self.data:
				if kwd in u.account or kwd in u.name:
					self.lst.append(u)

		self.hListCtrl.DeleteAllItems()
		for user in self.lst:
			self.hListCtrl.Append((user.name,user.account))

		if focusedUser in self.lst:
			self.hListCtrl.Select(-1,-1)
			self.hListCtrl.Focus(self.lst.index(focusedUser))
			self.hListCtrl.Select(self.lst.index(focusedUser))
		self.onItemSelected()
