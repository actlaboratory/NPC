import dbManager
import peing
import dateTime

class manager():
	def __init__(self):
		self.db = dbManager.dbManager("npc.db")
		self.db.execute("""create table if not exists users(
				id integer primary key,
				user_id text not null,
				user_name text not null,
				name text not null
			);""")
			self.db.execute("""create table if not exists answers(
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
		self.db.execute("delete * from users where id = ?;", (info[0]["id"],))
		self.db.execute("delete * from answers where user_id = ?;", (info[0]["id"]))
		return True

	def get_answers(self, userId = None):
		if userId == None:
			return self.db.select("select * from answers order by answered_at desc;")
		return self.db.select("select * from answers order by answered_at desc where user_id = ?;", (userId,))

	def get_userInfo(self, user_name = None):
		if user_name == None:
			return self.db.select("select * from users;")
		return self.db.select("select * from users where user_name = ?;", (user_name,))

	def update(self):
		users = self.get_userInfo()
		if users == None:
			return False
		for user in users:
			added_answer = self.get_answers(user["id"])
			if added_answer == None:
				self._first_answer_add(user)
			else:
				self._add_answer_to_time(user, added_answer[1]["answered_at"])
		return True

	def _fast_answer_add(self, user):
		add_answer = peing.getAnswers(user["user_name"])
		insert_list = []
		for answer in add_answer:
			answered_at = datetime.datetime.fromisoformat(answer["answer_created_at"])
			data = (user["id"], answer["body"], answer["answer_body"], answered_at)
			insert_list.append(data)
		self.db.executemany("""insert into answers(
			user_id, question, answer, answered_at)
		values(?,?,?,?);			""", insert_list)
		self.db.connection.commit()
		return True

	def _add_answer_to_time(self, user, time):
		page = 1
		while True:
			add_answer = peing.getAnswers(user["user_name"], page=page)
			for answer in add_answer:
				answered_at = datetime.datetime.fromisoformat(answer["answer_created_at"])
				if answered_at == time:
					all = True
					break
				data = (user["id"], answer["body"], answer["answer_body"], answered_at)
				self.db.execute("""insert into answers(
					user_id, question, answer, answered_at)
					values(?,?,?,?);
				""", data)
			if all:
				break
			page += 1
		self.db.connection.commit()
		return
