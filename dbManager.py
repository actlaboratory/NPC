import sqlite3

class dbManager():
	def __init__(self, db_name):
		self.connection = sqlite3.connect(db_name)
		self.connection.row_factory = sqlite3.Row
		self.cursor = self.connection.cursor()

	def select(self, *args):
		self.cursor.execute(*args)
		result = self.cursor.fetchall()
		if len(result) == 0:
			return None
		return result

	def execute(self, *args):
		self.cursor.execute(*args)
		return

	def executemany(self, *args):
		self.cursor.executemany(*args)
		return

	def __del__(self):
		self.connection.close()
		print("closed!")
