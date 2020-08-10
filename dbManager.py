import sqlite3

class dbManager():
	def __init__(self, db_name):
		self.connection = sqlite3.connect(db_name)
		self.connection.row_factory = sqlite3.Row
		self.cursor = self.connection.cursor()

	def select(*args):
		self.cursor.execute(*args)
		result = cursor.fetchall()
		if len(result) == 0:
			return None
		return result

	def execute(*args):
		self.cursor(*args)
		return

	def __del__(self):
		self.connection.close()
		print("closed!")
