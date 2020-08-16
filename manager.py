import dbManager
import communication

class manager():
	def __init__(self):
		self.db = dbManager.dbManager("npc.db")
		if not self.db.select("SELECT * FROM sqlite_master;"):
			self.db.execute("""create table users(
				id integer primary key,
				user_id text not null,
				user_name text not null,
				name text not null,
				answer_count integer not null
			);""")
			self.db.execute("""create table answers(
				id integer primary key,
				user_id integer not null,
				user_name text not null,
				question text not null,
				answer text not null,
				answered_add dateTime not null
			);""")
			self.db.connection.commit()

test = manager()
