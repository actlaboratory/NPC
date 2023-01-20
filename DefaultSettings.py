# -*- coding: utf-8 -*-
#default config

from ConfigManager import *


class DefaultSettings:
	def get():
		config = ConfigManager()
		config["general"]={
			"language": "ja-JP",
			"fileVersion": "100",
			"locale": "ja-JP",
			"update" : True,
			"auto_reload" : False,
			"log_level":"20",
			"keep_filter":"False",
		}
		config["view"]={
			"font": "bold 'ＭＳ ゴシック' 22 windows-932",
			"colorMode":"normal",
			"textwrapping":"off",
			"enableMultiline":False,
		}
		config["speech"]={
			"reader" : "AUTO"
		}
		config["mainView"]={
			"sizeX": "1080",
			"sizeY": "675",
		}
		config["proxy"]={
			"usemanualsetting" : False,
			"server" : "localhost",
			"port" : 8080,
		}
		config["account"]={
			"id" : "",
			"password" : "",
			"use_always" : "false"
		}
		config["filter_status"]={
			"auto_question" : "False",
			"baton" : "False",
		}
		return config

initialValues={}
"""
	この辞書には、ユーザによるキーの削除が許されるが、初回起動時に組み込んでおきたい設定のデフォルト値を設定する。
	ここでの設定はユーザの環境に設定ファイルがなかった場合のみ適用され、初期値として保存される。
"""
