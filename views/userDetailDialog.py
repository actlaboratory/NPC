﻿# -*- coding: utf-8 -*-


import wx
import globalVars
import views.ViewCreator
from views.baseDialog import *
import webbrowser

class Dialog(BaseDialog):
	def __init__(self, user):
		super().__init__("userDetailDialog")
		self.user = user

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("詳細情報"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)

		grid=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,20,2)
		name,dummy = grid.inputbox(_("表示名"), None, self.user.name, wx.TE_READONLY|wx.BORDER_RAISED, 320)
		name.hideScrollBar(wx.HORIZONTAL)
		account,dummy = grid.inputbox("ID", None, self.user.account, wx.TE_READONLY|wx.BORDER_RAISED, 320)
		account.hideScrollBar(wx.HORIZONTAL)
		p = 0
		if self.user.items>0:
			p = int(self.user.answers*100/self.user.items)
		status,dummy = grid.inputbox(_("回答状況"), None, "%d/%d(%d%%)" % (self.user.answers,self.user.items,p), wx.TE_READONLY|wx.BORDER_RAISED, 320)
		status.hideScrollBar(wx.HORIZONTAL)
		followees,dummy = grid.inputbox(_("フォロイー"), None, str(self.user.followees), wx.TE_READONLY|wx.BORDER_RAISED, 320)
		followees.hideScrollBar(wx.HORIZONTAL)

		profile,dummy = self.creator.inputbox(_("プロフィール"), None, self.user.profile, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_PROCESS_ENTER|wx.BORDER_RAISED, 500)
		profile.hideScrollBar(wx.VERTICAL)
		profile.Bind(wx.EVT_TEXT_ENTER,self.processEnter)

		self.closeButton=self.creator.okbutton(_("閉じる"), None)

	def processEnter(self,event):
		self.wnd.EndModal(wx.ID_OK)