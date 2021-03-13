# -*- coding: utf-8 -*-
# ユーザ一覧ダイアログ

import wx

import filter
import simpleDialog
import views.ViewCreator

from views.baseDialog import *



class Dialog(BaseDialog):
	def __init__(self,lst,service):
		super().__init__("userListDialog")
		self.lst = lst
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
		self.hListCtrl, self.hStatic = self.creator.listCtrl(_("登録済みユーザ"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,sizerFlag=wx.EXPAND)
		self.hListCtrl.AppendColumn(_("表示名"),width=450)
		self.hListCtrl.AppendColumn(_("id"),width=450)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.close)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)

		for user in self.lst:
			self.hListCtrl.Append((user.name,user.account))

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.EXPAND|wx.LEFT|wx.RIGHT,margin=20)
		self.detailButton = self.creator.button(_("詳細"), self.detail)
		self.filterButton = self.creator.button(_("フィルタ(&F)"), self.filter)
		self.removeButton = self.creator.button(_("削除"), self.remove)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("閉じる(&C)"), self.close)

		self.onItemSelected()

	def close(self,event):
		self.wnd.EndModal(wx.ID_OK)

	def onItemSelected(self, event=None):
		selected = self.hListCtrl.GetFocusedItem()
		self.detailButton.Enable(selected >= 0)
		self.filterButton.Enable(selected >= 0)
		self.removeButton.Enable(selected >= 0)

	def remove(self,event):
		user = self.lst[self.hListCtrl.GetFocusedItem()]
		ret = simpleDialog.yesNoDialog(_("ユーザの削除"),_("以下のユーザの登録と、過去の回答履歴を削除しますか？\n\n%s")%user.getViewString())
		if ret == wx.ID_NO:
			return
		self.service.deleteUser(user)
		self.lst.remove(user)
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
