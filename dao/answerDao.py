import dao.baseDao

import datetime
import sqlite3


class AnswerDao(dao.baseDao.BaseDao):
	def __init__(self):
		super().__init__("answers")
		self.execute("""create table if not exists answers(
			id INTEGER PRIMARY KEY,
			user_id INTEGER NOT NULL,
			question text NOT NULL,
			answer text NOT NULL,
			answered_at datetime NOT NULL,
			flag INTEGER DEFAULT 0
		);""")
		self.connection.commit()

	def get(self,id):
		return self.select("SELECT * FROM answers WHERE id = ? ORDER BY answered_at DESC;", (id,))

	def getFromUser(self, userId=-1):
		if userId == -1:
			return self.select("SELECT * FROM answers ORDER BY answered_at DESC;")
		return self.select("SELECT * FROM answers ORDER BY answered_at DESC where user_id = ?;", (userId,))

	def getLast(self,userId):
		assert type(userId)==int
		return self.select("SELECT * FROM answers WHERE user_id = ? ORDER BY answered_at DESC LIMIT 1;", (userId,))

	def getViewData(self,userId=-1):
		if userId==-1:
			return self.select("SELECT answers.id,users.name,question,answer,answered_at,answers.flag,users.id FROM answers INNER JOIN users ON users.id=answers.user_id ORDER BY answered_at DESC;",())
		else:
			return self.select("select answers.id,users.name,question,answer,answered_at,answers.flag,users.id from answers INNER JOIN users ON users.id=answers.user_id ORDER BY answered_at DESC WHERE user_id = ?;", (userId,))

	def insert(self,values):
		return self.connection.execute("""INSERT INTO answers(
			id,user_id, question, answer, answered_at,flag)
			values(?,?,?,?,?,?);
			""", values)

	def insertMany(self,values):
		return self.connection.executemany("""INSERT INTO answers(
			id,user_id, question, answer, answered_at,flag)
			values(?,?,?,?,?,?);
			""", values)

	def deleteFromUser(self,userId):
		return self.connection.execute("DELETE FROM answers WHERE user_id = ?;", (userId,))
