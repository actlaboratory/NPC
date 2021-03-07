
import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"FILE_ADD_USER":_("ユーザの追加")+"...",
	"FILE_POST_QUESTION":_("質問を投稿"),
	"FILE_RELOAD":_("最新の情報に更新"),
	"FILE_DELETE_USER":_("ユーザを削除"),
	"FILE_OPEN_CONTEXTMENU":_("コンテキストメニューを開く"),
	"FILE_SHOW_DETAIL":_("詳細情報を表示")+"...",
	"FILE_SHOW_USER_DETAIL":_("ユーザ情報を表示")+"...",
	"FILE_EXPORT":_("表示中のリスト内容をCSVファイルにエクスポート"),
	"FILE_SHOW_USER_WEB":_("ブラウザでユーザのページを開く"),
	"FILE_EXIT":_("終了(&X)"),

	"FILTER_AUTO_QUESTION":_("運営からの質問を非表示(&A)"),
	"FILTER_BATON":_("バトン質問を非表示(&B)"),
	"FILTER_USER":_("選択中ユーザのみ表示(&U)"),

	"OPTION_OPTION":_("設定(&S)")+"...",
	"OPTION_KEY_CONFIG":_("ショートカットキーの設定(&K)")+"...",
	"OPTION_LIST_CONFIG":_("リスト表示設定(&L)")+"...",

	"HELP_UPDATE":_("最新バージョンを確認(&U)")+"...",
	"HELP_VERSIONINFO":_("バージョン情報(&V)")+"...",
}
