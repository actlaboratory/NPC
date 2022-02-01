# npc service
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import os
import time
import tweepy
import twitterAuthorization
import webbrowser
import wx

import constants
import errorCodes

from logging import getLogger


log = getLogger("%s.twitterService" % (constants.LOG_PREFIX))


# ブラウザを起動し、ユーザからの認証を受ける
# 途中、Bool値を返すpollingFunctionを呼び続け、Falseが返却された場合は強制的に終了する
# 成功時はトークン(dic)、失敗時はNoneを返す
def authorize(pollingFunction=None):
	manager = None
	try:
		log.debug("start authorization")
		manager = twitterAuthorization.TwitterAuthorization(constants.TWITTER_CONSUMER_KEY,constants.TWITTER_CONSUMER_SECRET,constants.LOCAL_SERVER_PORT)
		l="ja"
		try:
			l=globalVars.app.config["general"]["language"].split("_")[0].lower()
		except:
			pass#end うまく読めなかったら ja を採用
		#end except
		manager.setMessage(
			lang=l,
			success=_("認証に成功しました。このウィンドウを閉じて、アプリケーションに戻ってください。"),
			failed=_("認証に失敗しました。もう一度お試しください。"),
			transfer=_("しばらくしても画面が切り替わらない場合は、別のブラウザでお試しください。")
		)
		url = manager.getUrl()
		log.debug("url = %s" % url)
		webbrowser.open(url, new=1, autoraise=True)

		# polling
		while(True):
			wx.YieldIfNeeded()

			# return tupple, "" or None
			token=manager.getToken()
			if token=="":
				log.info("Authorization failed.  May be user disagreed.")
				token = None
				break
			elif token:
				break
			elif pollingFunction()==False:
				token = errorCodes.CANCELED
				log.info("pollingFunction returned False")
				break
			# when token==None: continue polling

		manager.shutdown()
		return token
	except Exception as e:
		log.error(e)
		if manager:
			manager.shutdown()
		return None

def getFollowList(token,target):
	auth = tweepy.OAuthHandler(constants.TWITTER_CONSUMER_KEY, constants.TWITTER_CONSUMER_SECRET)
	auth.set_access_token(*token)
	try:
		twitterApi = tweepy.API(auth,proxy=os.environ['HTTPS_PROXY'])
	except KeyError:
		twitterApi = tweepy.API(auth)

	ret = []
	try:
		user = twitterApi.get_user(screen_name=target)
		friendsCount = user.friends_count
		friends = tweepy.Cursor(twitterApi.get_friends,screen_name=target,include_user_entities=False,skip_status=True,count=200).items()
		for friend in friends:
			ret.append(friend.screen_name)
		return ret
	except tweepy.TooManyRequests:
		log.error("rateLimitError")
		return ret
	except tweepy.TweepyException as e:
		log.error(e)
		log.error("%s" %(e.response))
		return errorCodes.TWITTER_ERROR
	except Exception as e:
		log.error(e)
		return errorCodes.UNKNOWN
