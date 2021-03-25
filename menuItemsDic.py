#menuItems dictionally
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"FILE_ADD_USER":_("ユーザの追加(&A)")+"...",
	"FILE_POST_QUESTION":_("質問を投稿(&Q)")+"...",
	"FILE_RELOAD":_("最新の情報に更新(&R)"),
	"FILE_DELETE_USER":_("ユーザを削除(&D)"),
	"FILE_OPEN_CONTEXTMENU":_("コンテキストメニューを開く"),
	"FILE_SHOW_DETAIL":_("詳細情報を表示(&V)")+"...",
	"FILE_SHOW_USER_DETAIL":_("ユーザ情報を表示(&U)")+"...",
	"FILE_EXPORT":_("表示中のリスト内容をCSVファイルにエクスポート(&E)"),
	"FILE_SHOW_USER_WEB":_("ブラウザでユーザのページを開く(&B)"),
	"FILE_USER_LIST":_("登録済みユーザリスト(&L)")+"...",
	"FILE_EXIT":_("終了(&X)"),

	"FILTER_AUTO_QUESTION":_("運営からの質問を非表示(&M)"),
	"FILTER_BATON":_("バトン質問を非表示(&B)"),
	"FILTER_USER":_("選択中ユーザのみ表示(&U)"),

	"ACCOUNT_ANSWER":_("届いている質問に回答"),
	"ACCOUNT_ARCHIVED":_("アーカイブ済みの質問を表示"),

	"ACCOUNT_ADD_FOLLOWEES":_("アカウントのフォロイーから一括登録"),


	"OPTION_OPTION":_("設定(&S)")+"...",
	"OPTION_KEY_CONFIG":_("ショートカットキーの設定(&K)")+"...",
	"OPTION_LIST_CONFIG":_("リスト表示設定(&L)")+"...",

	"HELP_UPDATE":_("最新バージョンを確認(&U)")+"...",
	"HELP_VERSIONINFO":_("バージョン情報(&V)")+"...",
}
