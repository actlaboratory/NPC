﻿# -*- coding: utf-8 -*-
#Application Main
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

import win32api
import win32event
import winerror
import wx

import AppBase
import constants
import errorCodes
import filter
import globalVars
import proxyUtil
import simpleDialog
import update

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def OnInit(self):
		#多重起動防止
		globalVars.mutex = win32event.CreateMutex(None, 1, constants.APP_NAME)
		if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
			globalVars.mutex = None
			return False
		return True

	def initialize(self):
		self.initUpdater()
		# プロキシの設定を適用
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		self.setProxyEnviron()
		# アップデートを実行
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		# 設定されている場合には起動時にフィルタを適用
		if self.config.getboolean("general","keep_filter",False):
			self.log.debug("keepFilter:run")
			filter.loadStatus()

		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		self.hMainView.Show()
		if self.config.getboolean("general","auto_reload",True):
			wx.CallAfter(self.autoReload)

	def setProxyEnviron(self):
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()

	def autoReload(self):
		self.log.info("start: auto_reload")
		self.hMainView.events.reload()


	def initUpdater(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		# フィルタの適用状態を保存
		if self.config.getboolean("general","keep_filter",False):
			self.log.debug("keepFilter:save")
			filter.saveStatus()

		import dao
		dao.connectionFactory.getConnection().close()
		self.log.info("DB connection closed.")

		self._releaseMutex()

		if self.config.write() != errorCodes.OK:
			simpleDialog.errorDialog(_("設定の保存に失敗しました。下記のファイルへのアクセスが可能であることを確認してください。") + "\n" + self.config.getAbsFileName())

		# アップデート
		globalVars.update.runUpdate()

		#戻り値は無視される
		return 0

	def _releaseMutex(self):
		if globalVars.mutex != None:
			try: win32event.ReleaseMutex(globalVars.mutex)
			except Exception as e:
				return
			globalVars.mutex = None
			self.log.info("mutex object released.")

	def __del__(self):
		self._releaseMutex()
