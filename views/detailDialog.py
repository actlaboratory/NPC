# -*- coding: utf-8 -*-


import wx
import globalVars
import views.ViewCreator
from views.baseDialog import *
import webbrowser

class Dialog(BaseDialog):
	def __init__(self, answer):
		super().__init__("viewCommentDialog")
		self.answer = answer

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("詳細情報"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
		q,dummy = self.creator.inputbox("Q", None, self.answer.question, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_PROCESS_ENTER|wx.BORDER_RAISED, 500,textLayout=wx.HORIZONTAL)
		q.hideScrollBar(wx.VERTICAL)
		q.Bind(wx.EVT_TEXT_ENTER,self.processEnter)

		a,dummy = self.creator.inputbox("A", None, self.answer.answer, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_PROCESS_ENTER|wx.BORDER_RAISED, 500,textLayout=wx.HORIZONTAL)
		a.hideScrollBar(wx.VERTICAL)
		a.Bind(wx.EVT_TEXT_ENTER,self.processEnter)

		grid=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,20,2)
		user,dummy = grid.inputbox(_("回答者"), None, self.answer.user.name+"(@"+self.answer.user.account+")", wx.TE_READONLY|wx.BORDER_RAISED, 320)
		user.hideScrollBar(wx.HORIZONTAL)
		at,dummy = grid.inputbox(_("回答日時"), None, str(self.answer.answered_at), wx.TE_READONLY|wx.BORDER_RAISED, 320)
		at.hideScrollBar(wx.HORIZONTAL)

		self.closeButton=self.creator.okbutton(_("閉じる"), None)

	def processEnter(self,event):
		self.wnd.EndModal(wx.ID_OK)
