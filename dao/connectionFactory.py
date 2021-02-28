import sqlite3
import constants
import globalVars

from logging import getLogger


connection = None
log = None

def getConnection():
	if not connection:
		getNewConnection()
	return connection


def getNewConnection():
	global connection,log
	connection = sqlite3.connect(
			constants.DB_FILE_NAME,
			detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
			isolation_level='DEFERRED'
			)
	connection.row_factory = sqlite3.Row
	sqlite3.enable_callback_tracebacks(globalVars.app.frozen==False)
	sqlite3.dbapi2.converters['DATETIME'] = sqlite3.dbapi2.converters['TIMESTAMP']
	sqlite3.register_converter("BOOLEAN", _convert_boolean)
	sqlite3.register_adapter(bool, _adapt_boolean)

	if log==None:
		log=getLogger("%s.sql" % (constants.LOG_PREFIX))
	connection.set_trace_callback(sqlLogger)


def _adapt_boolean(value):
	if value:
		return 1
	else:
		return 0

def _convert_boolean(value):
	if int(value) == 0:
		return False
	else:
		return True

def sqlLogger(statement):
	log.debug(statement)
