import sqlite3

class dbManager():
	def __init__(self, db_name):
		self.connection = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		self.connection.row_factory = sqlite3.Row
		sqlite3.dbapi2.converters["DATETIME"] = sqlite3.dbapi2.converters["TIMESTAMP"]
		sqlite3.register_converter("BOOL", self._convert_boolean)
		sqlite3.register_adapter(bool, self._adapt_boolean)
		self.cursor = self.connection.cursor()

	def _adapt_boolean(value):
		if value:
			return 1
		if not value:
			return 0

	def _convert_boolean(value):
		if int(value) == 0:
			return False
		if int(value) == 1:
			return True

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
