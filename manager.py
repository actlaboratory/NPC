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
				name text not null
			);""")
			self.db.execute("""create table answers(
				id integer primary key,
				user_id integer not null,
				question text not null,
				answer text not null,
				answered_at dateTime not null
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
		self.db.execute("""insert into users (user_id, user_name, name) values(
			:user_id, :user_name, :name
			);""", insert_dicts)
		self.db.connection.commit()

	def delete_user(self, userName):
		info = get_userInfo(userName)
		if info == None:
			return False
<<<<<<< HEAD
		self.db.execute("delete from users where id = ?;", (info[0]["id"]))
		self.db.execute("delete from answers where user_id = ?;", (info[0]["id"]))
		self.db.connection.commit()
=======
		self.db.execute("delete * from users where id = ?;", (info[0]["id"],))
		self.db.execute("delete * from answers where user_id = ?;", (info[0]["id"]))
>>>>>>> 6414522b451e34a9c0994318e86b0d4c9c2265aa
		return True

	def get_answers(self, userId = None):
		if userId == None:
			return self.db.select("select * from answers;")
		return self.db.select("select * from answers where user_id = ?;", (userId,))

	def get_userInfo(self, user_name = None):
<<<<<<< HEAD
		if user_name = None:
=======
		if user_name == None:
>>>>>>> 6414522b451e34a9c0994318e86b0d4c9c2265aa
			return self.db.select("select * from users;")
		return self.db.select("select * from users where user_name = ?;", (user_name,))

	def update(self):
		users = self.get_userInfo()
		if users == None:
			return False
		for user in users:
			added_answer = self.get_answers(user["id"])
			if added_answer == None:
				add_answer = peing.getAnswers(user["user_name"])
				insert_list = []
				for answer in add_answer:
					data = (user["id"], answer["body"], answer["answer_body"], answer["answer_created_at"])
					insert_list.append(data)
				self.db.executemany("""insert into answers(
					user_id, question, answer, answered_at)
					values(?,?,?,?);
				""", insert_list)
				self.db.connection.commit()
