# -*- coding: utf-8 -*-
# search Condition dialog view
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>
# Note: All comments except these top lines will be written in Japanese. 

import re
import wx

import views.ViewCreator
import simpleDialog

from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self,parent=None):
		super().__init__("searchConditionDialog")
		if parent!=None:
			self.parent=parent
		else:
			self.parent=self.app.hMainView.hFrame

	def Initialize(self):
		super().Initialize(self.parent,_("回答データの検索"))
		self.InstallControls()
		self.log.debug("Finished creating view")
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator = views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.edit,self.static = self.creator.inputbox(_("検索キーワード"),x=-1,style=wx.BORDER_RAISED|wx.TE_DONTWRAP,sizerFlag=wx.EXPAND)
		self.edit.hideScrollBar(wx.HORIZONTAL)
		self.select,dummy = self.creator.combobox(_("検索対象"), (_("質問"),_("回答"),_("両方")), state=0, proportion=1, textLayout=wx.HORIZONTAL)
		self.check = self.creator.checkbox(_("正規表現を使用(&R)"))

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("ＯＫ"),self.ok)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def ok(self,event):
		# 正規表現として不適切な場合は警告する
		if self.check.GetValue():
			try:
				re.compile(self.edit.GetValue())
			except re.error:
				simpleDialog.errorDialog(_("入力された正規表現が正しくありません。入力内容をご確認ください。"),self.wnd)
				return
		event.Skip()

	def GetData(self):
		return (self.edit.GetLineText(0),self.select.GetSelection(),self.check.GetValue())
