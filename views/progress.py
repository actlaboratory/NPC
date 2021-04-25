# -*- coding: utf-8 -*-
# progress dialog
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx

import views.ViewCreator

from views.baseDialog import *

MODE_NORMAL = 0		#テキスト１行・プログレスバー・ボタン
MODE_NO_GAUGE = 1	#プログレスバーなし

class Dialog(BaseDialog):
	def __init__(self,mode=0):
		super().__init__("gaugeDialog")
		self.mode = mode
		self._status = None

	def Initialize(self, label, title):
		self.label=label
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,title)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,style=wx.ALL,space=20)
		if self.mode&MODE_NO_GAUGE==0:
			self.gauge,self.static=self.creator.gauge(self.label,x=500)
		else:
			self.static=self.creator.staticText(self.label)
			self.creator.AddSpace()
		self.button = self.creator.button(_("中止(&C)"), self.cancelEvent,sizerFlag=wx.ALIGN_CENTER)

	# プログレス更新（現在値, ラベル, 最大値）
	def update(self, pos=None, label=None, max=None):
		if max != None and self.mode&MODE_NO_GAUGE==0:
			self.gauge.SetRange(max)
		if pos != None and self.mode&MODE_NO_GAUGE==0:
			self.gauge.SetValue(pos)
		if label != None:
			self.static.SetLabel(label)
		wx.YieldIfNeeded()

	def cancelEvent(self, evt):
		self._status = wx.ID_CANCEL

	#キャンセルされていなければTrue
	def isOk(self):
		return self._status==None

