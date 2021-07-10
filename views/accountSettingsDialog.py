# -*- coding: utf-8 -*-
# アカウント設定ダイアログ
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import wx

import errorCodes
import views.ViewCreator

from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self,service):
		super().__init__("accountSettingsDialog")
		self.service = service

	def Initialize(self,parent=None):
		if parent == None:
			parent = self.app.hMainView.hFrame
		self.log.debug("created")
		super().Initialize(parent,_("アカウント設定"))
		self.InstallControls()
		return self.load()

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,0,style=wx.EXPAND|wx.ALL,margin=20)
		self.name,dummy = self.creator.inputbox(_("名前"),sizerFlag=wx.ALL|wx.EXPAND)
		self.profile,dummy = self.creator.inputbox(_("プロフィール"),style=wx.TE_MULTILINE,sizerFlag=wx.ALL|wx.EXPAND)
		self.getAutoQuestion,dummy = self.creator.combobox(_("運営からの自動質問"),(_("受信する"),_("受信しない")),None,1)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,0,"",wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT,margin=20)
		self.bOk=self.creator.okbutton(_("設定"), self.ok)
		self.bCancel=self.creator.cancelbutton(_("閉じる(&C)"))

	def ok(self,event):
		self.wnd.EndModal(wx.ID_OK)

	def load(self):
		data = self.service.getProfile()
		if type(data)==int:
				return data
		try:
			self.name.SetValue(data["name"])
			self.profile.SetValue(data["profile"])
			if data["is_receive_baton"]:
				self.getAutoQuestion.SetSelection(0)
		except KeyError:
			return errorCodes.PEING_ERROR
		return errorCodes.OK

	def GetData(self):
		r={}
		r["name"]=self.name.GetValue()
		r["profile"]=self.profile.GetValue()
		r["is_receive_baton"]=(self.getAutoQuestion.GetSelection()==0)
		print(self.getAutoQuestion.GetSelection())
		return r
