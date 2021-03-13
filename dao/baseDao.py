# base Dao
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import sqlite3

import dao.connectionFactory


class BaseDao():
	def __init__(self, tableName,connection=None):
		self.tableName=tableName
		if connection:		#引数で指定されたものを使用
			self.connection = connection
		else:				#未指定の場合はデフォルトでアプリ共通のコネクションを利用
			self.connection = dao.connectionFactory.getConnection()
		self.cursor = self.connection.cursor()

	def select(self, *args):
		self.cursor.execute(*args)
		result = self.cursor.fetchall()
		if len(result) == 0:
			return []
		return result

	def execute(self, *args):
		self.cursor.execute(*args)
		return

	def executemany(self, *args):
		self.cursor.executemany(*args)
		return
