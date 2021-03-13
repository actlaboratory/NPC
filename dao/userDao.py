# user Dao
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>


import dao.baseDao


class UserDao(dao.baseDao.BaseDao):
	def __init__(self):
		super().__init__("users")
		self.connection.execute("""create table if not exists users(
			id INTEGER primary key,
			name TEXT NOT NULL,
			account TEXT NOT NULL,
			items INTEGER DEFAULT 0,
			answers INTEGER DEFAULT 0,
			profile TEXT DEFAULT "",
			followees INTEGER DEFAULT 0,
			flag INTEGER DEFAULT 0
		);""")
		self.connection.commit()

	def getAll(self):
		return self.select("select * from users;")

	#指定したフラグが立っていないユーザの一覧を得る
	def getAllWithoutFlag(self,disableFlag):
		return self.select("select * from users WHERE flag&?==0;",(disableFlag,))


	def get(self,id):
		assert type(id)==int
		return self.select("SELECT * FROM users WHERE id = ?;",(id,))

	def getFromUserName(self, userName):
		assert type(userName)==str
		return self.select("SELECT * FROM users WHERE account = ?;", (userName,))

	def insert(self, values):
		return self.connection.execute("""INSERT INTO users (id, account, name, items, answers, profile, followees) VALUES(
			:id, :account, :name, :items, :answers, :profile, :followees
			);""", values)

	def update(self,values):
		return self.connection.execute("""UPDATE users SET
			account = :account,
			name = :name,
			items = :items,
			answers = :answers,
			profile = :profile,
			followees = :followees
			WHERE id = :id;""", values)

	def delete(self,id):
		return self.connection.execute("DELETE FROM users WHERE id = ?;",(id,))
