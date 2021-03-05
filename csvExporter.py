
import csv

class CsvExporter:
	def __init__(self):
		self.error = None

	def exportVirtualList(self,fileName,listCtrl,delimiter=","):
		try:
			with open(fileName, 'w',encoding='cp932',errors="replace") as f:
				writer = csv.writer(f,delimiter=delimiter,lineterminator="\n")
				for i in range(len(listCtrl)):
					writer.writerow([x for x in listCtrl[i]])
				return True
		except Exception as e:
			self.error=e
			return False

	def getErrorMessage(self):
		if self.error == None:
			return ""
		else:
			return str(self.error)
