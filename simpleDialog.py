# -*- coding: utf-8 -*-
#Simple dialog
#Copyright (C) 2020 guredora <contact@guredora.com>

import ctypes
import winsound
import wx
import constants

def winDialog(title,message):
	ctypes.windll.user32.MessageBoxW(0,message,title,0x00000040)
def qDialog(message, title="確認"):
	dialog = wx.MessageDialog(None,message,title,wx.YES_NO|wx.ICON_QUESTION)
	winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
	result = dialog.ShowModal()
	dialog.Destroy()
	return result
def dialog(message, title=constants.APP_NAME):
	dialog = wx.MessageDialog(None,message,title,wx.OK|wx.ICON_INFORMATION)
	winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
	dialog.ShowModal()
	dialog.Destroy()
	return
def errorDialog(message):
	dialog = wx.MessageDialog(None, message, _("エラー"), wx.OK|wx.ICON_ERROR)
	winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
	dialog.ShowModal()
	dialog.Destroy()
	return
