# -*- coding: utf-8 -*-
#Application Main

import win32api
import win32event
import winerror
import sys
import wx

import AppBase
import constants
import update
import globalVars
import proxyUtil

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()
		self.mutex = 0

	def OnInit(self):
		#多重起動防止
		self.mutex = win32event.CreateMutex(None, 1, constants.APP_FULL_NAME)
		if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
			return False
		return True

	def initialize(self):
		self.setGlobalVars()
		# プロキシの設定を適用
		if self.config.getboolean("network", "auto_proxy"):
			self.proxyEnviron = proxyUtil.virtualProxyEnviron()
			self.proxyEnviron.set_environ()
		else:
			self.proxyEnviron = None
		# アップデートを実行
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		self.hMainView.Show()
		wx.CallAfter(self.autoReload)

	
	def autoReload(self):
		self.log.info("start: auto_reload")
		self.hMainView.events.reload()


	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		import dao
		dao.connectionFactory.getConnection().close()
		self.log.info("DB connection closed.")

		self._releaseMutex()

		#戻り値は無視される
		return 0

	def _releaseMutex(self):
		if self.mutex != 0:
			try: win32event.ReleaseMutex(self.mutex)
			except: pass
			self.mutex = 0
			self.log.info("mutex object released.")

	def __del__(self):
		self._releaseMutex()
