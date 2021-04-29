# sent Question Dao
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import dao.baseDao


class sentQuestionDao(dao.baseDao.BaseDao):
	def __init__(self):
		super().__init__("sentQuestions")
		self.execute("""create table if not exists sentQuestions(
			id INTEGER PRIMARY KEY,
			user_id INTEGER NOT NULL,
			question text NOT NULL,
			answer text NOT NULL,
			answered_at datetime NOT NULL,
			flag INTEGER DEFAULT 0
		);""")
		self.connection.commit()

	def get(self,id):
		assert type(id)==int
		return self.select("SELECT * FROM sentQuestions WHERE id = ? ORDER BY answered_at DESC;", (id,))

	def getAll(self):
		return self.select("SELECT * FROM sentQuestions ORDER BY answered_at DESC;", ())

	def getFromUser(self, userId=-1):
		assert type(userId)==int
		if userId == -1:
			return self.select("SELECT * FROM sentQuestions ORDER BY answered_at DESC;")
		return self.select("SELECT * FROM sentQuestions ORDER BY answered_at DESC where user_id = ?;", (userId,))

	def getLast(self):
		return self.select("SELECT * FROM sentQuestions ORDER BY answered_at DESC LIMIT 1;", ())

	def getViewData(self,userId=-1):
		assert type(userId)==int
		if userId==-1:
			return self.select("SELECT sentQuestions.id,users.name,question,answer,answered_at,sentQuestions.flag,users.id FROM sentQuestions INNER JOIN users ON users.id=sentQuestions.user_id ORDER BY answered_at DESC;",())
		else:
			return self.select("select sentQuestions.id,users.name,question,answer,answered_at,sentQuestions.flag,users.id from sentQuestions INNER JOIN users ON users.id=sentQuestions.user_id ORDER BY answered_at DESC WHERE user_id = ?;", (userId,))

	# insert
	# valuesにはanswerEntityを指定
	def insert(self,values):
		return self.connection.execute("""INSERT INTO sentQuestions(
			id,user_id, question, answer, answered_at,flag)
			values(:id,:user,:question,:answer,:answered_at,:flag);
			""", values)

	def insertMany(self,values):
		return self.connection.executemany("""INSERT INTO sentQuestions(
			id,user_id, question, answer, answered_at,flag)
			values(?,?,?,?,?,?);
			""", values)

	def deleteFromUser(self,userId):
		return self.connection.execute("DELETE FROM sentQuestions WHERE user_id = ?;", (userId,))
