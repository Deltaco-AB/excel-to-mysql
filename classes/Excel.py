import pandas as pd

class Excel():
	def __init__(self,xlsx):
		self.dataframe = pd.read_excel(xlsx)

	def get_headers(self):
		return list(self.dataframe)

	def is_header(self,name):
		if name not in self.get_headers():
			return False
		return True