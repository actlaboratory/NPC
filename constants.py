# -*- coding: utf-8 -*-
#constant values
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import wx

#アプリケーション基本情報
APP_FULL_NAME = "windows Native Peing Connector"#アプリケーションの完全な名前
APP_NAME="NPC"#アプリケーションの名前
APP_ICON = None
APP_VERSION="1.2.0"
APP_LAST_RELEASE_DATE="2021-07-22"
APP_COPYRIGHT_YEAR="2021"
APP_LICENSE="Apache License 2.0"
APP_DEVELOPERS="yamahubuki, ACT Laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL="https://actlab.org/software/NPC"
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All lights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

SUPPORTING_LANGUAGE={"ja-JP": "日本語","en-US": "English"}

#各種ファイル名
LOG_PREFIX="npc"
LOG_FILE_NAME="npc.log"
SETTING_FILE_NAME="settings.ini"
KEYMAP_FILE_NAME="keymap.ini"
DB_FILE_NAME="save.db"


#フォントの設定可能サイズ範囲
FONT_MIN_SIZE=5
FONT_MAX_SIZE=35

#３ステートチェックボックスの状態定数
NOT_CHECKED=wx.CHK_UNCHECKED
HALF_CHECKED=wx.CHK_UNDETERMINED
FULL_CHECKED=wx.CHK_CHECKED

#build関連定数
BASE_PACKAGE_URL = "https://github.com/actlaboratory/NPC/releases/download/1.0.0/NPC-1.0.0.zip"
PACKAGE_CONTAIN_ITEMS = ()#パッケージに含めたいファイルやfolderがあれば指定
NEED_HOOKS = ()#pyinstallerのhookを追加したい場合は指定
STARTUP_FILE = "npc.py"#起動用ファイルを指定
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"


# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_VERSION = "1.0.0"
UPDATER_WAKE_WORD = "hello"


#Twitter認証情報
TWITTER_CONSUMER_KEY = "JEhuJyFSovxDa8bqeXElqHKsT"
TWITTER_CONSUMER_SECRET = "kIe1Ne9gR1h3mbvOBFVcFA3FWYysDKdqwdq9atRE1RaQWdTvbl"
LOCAL_SERVER_PORT = 9401

#ユーザテーブルのフラグ
FLG_USER_DISABLE=1			#アカウント名が変更されている
FLG_USER_NOT_REGISTERED=2	#登録されていない。送信済み質問リストのためだけにこのテーブルに追加されている

#質問種別フラグ
FLG_ANSWER_AUTOQUESTION=1		#運営からの自動質問
FLG_ANSWER_BATON_QUESTION=4		#バトン質問

#受信した質問の現況フラグ
RECEIVED=0
ARCHIVED=1

#ログインID種別設定
LOGIN_PEING=0
LOGIN_TWITTER=1
