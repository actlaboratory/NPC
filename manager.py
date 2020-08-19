import dbManager
import peing

class manager():
	def __init__(self):
		self.db = dbManager.dbManager("npc.db")
		if not self.db.select("SELECT * FROM sqlite_master;"):
			self.db.execute("""create table users(
				id integer primary key,
				user_id text not null,
				user_name text not null,
				name text not null,
			);""")
			self.db.execute("""create table answers(
				id integer primary key,
				user_id integer not null,
				question text not null,
				answer text not null,
				answered_add dateTime not null
			);""")
			self.db.connection.commit()

	def add_user(self, userName):
		if self.get_userInfo(userName) != None:
			return False
		info = peing.getUserInfo(userName)
		insert_dicts = {
			"user_id": info["id"],
			"user_name": info["account"],
			"name": info["name"]
		}
		self.db.execute("""insert into users (user_id, user_name, name) value(
			:user_id, :user_name, :name
			);""", insert_dicts)
		self.db.connection.commit()

	def delete_user(self, userName):
		info = get_userInfo(userName)
		if info == None:
			return False
		self.db.execute("delete * from users where id = ?;", (info[0]["id"]))
		self.db.execute("delete * from answers where user_id = ?;", (info[0]["id"]))
		return True

	def get_answers(self, userId = None):
		if userId == None:
			return self.db.select("select * from answers;")
		return self.db.select("select * from answers where user_id = ?;", (userId))

	def get_userInfo(self, user_name = None):
		if user_name = None:
			return self.db.select("select * from users;")
		return self.db.select("select * from users where user_name = ?;", (user_name))

test = manager()
