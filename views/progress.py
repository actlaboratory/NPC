# -*- coding: utf-8 -*-
# progress dialog
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx

import views.ViewCreator

from views.baseDialog import *


class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("gaugeDialog")

	def Initialize(self, label, title):
		self._status = None
		self.label=label
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,title)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,style=wx.ALL,space=20)
		self.gauge,self.static=self.creator.gauge(self.label,x=400)
		self.button = self.creator.button(_("中止") + "(&C)", self.cancelEvent,sizerFlag=wx.ALIGN_CENTER)

	# プログレス更新（現在値, ラベル, 最大値）
	def update(self, pos=None, label=None, max=None):
		if max != None:
			self.gauge.SetRange(max)
		if pos != None:
			self.gauge.SetValue(pos)
		if label != None:
			self.static.SetLabel(label)
		wx.YieldIfNeeded()

	def cancelEvent(self, evt):
		self._status = wx.ID_CANCEL

	#キャンセルされていなければTrue
	def isOk(self):
		return self._status==None

