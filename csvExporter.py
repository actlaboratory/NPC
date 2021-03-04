
import csv

class CsvExporter:
	def __init__(self):
		self.error = None

	def exportVirtualList(self,fileName,listCtrl,delimiter=","):
		try:
			with open(fileName, 'w', encoding="utf-8") as f:
				writer = csv.writer(f,delimiter=delimiter)
				for i in range(len(listCtrl)):
					writer.writerow(listCtrl[i])
				return True
		except Exception as e:
			self.error=e
			return False

	def getErrorMessage(self):
		if self.error == None:
			return ""
		else:
			return str(self.error)
