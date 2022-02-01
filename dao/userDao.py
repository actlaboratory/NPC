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
		assert type(disableFlag)==int
		return self.select("select * from users WHERE flag&?==0;",(disableFlag,))


	def get(self,id):
		assert type(id)==int
		return self.select("SELECT * FROM users WHERE id = ?;",(id,))

	#指定したフラグが立っていないユーザ１人を得る
	def getWithoutFlag(self,id,disableFlag):
		assert type(id)==int
		ret = self.select("SELECT * FROM users WHERE id = ? AND flag&?==0;",(id,disableFlag))
		if ret:
			return ret[0]
		return ret

	def getFromUserAccount(self, account):
		assert type(account)==str
		return self.select("SELECT * FROM users WHERE account = ?;", (account,))

	def getFromUserAccountWithoutFlag(self,account,disableFlag):
		assert type(account)==str
		assert type(disableFlag)==int
		return self.select("SELECT * FROM users WHERE account=? AND flag&?==0;",(account,disableFlag))



	def insert(self, values):
		return self.connection.execute("""INSERT INTO users (id, account, name, items, answers, profile, followees, flag) VALUES(
			:id, :account, :name, :items, :answers, :profile, :followees, :flag
			);""", values)

	def update(self,values):
		return self.connection.execute("""UPDATE users SET
			account = :account,
			name = :name,
			items = :items,
			answers = :answers,
			profile = :profile,
			followees = :followees,
			flag = :flag
			WHERE id = :id;""", values).rowcount

	def delete(self,id):
		return self.connection.execute("DELETE FROM users WHERE id = ?;",(id,))
