# -*- coding: utf_8 -*-  
#pytho3.5
import csv
import urllib.request
import lxml
from bs4 import BeautifulSoup 
import re
import codecs





# -------------------- main --------------------
if __name__ == '__main__':
	

	#2014-2016年に東京と中山で行われた全大会・全日数・全ラウンドの勝敗データを取得
	#Webページ(HTML)の取得
	for year in [2014]:
		for place in [1,2,3,4,5,6,7,8,9,10]:
			for name in [1,2,3,4,5]:
				for number in [1, 2, 3, 4, 5, 6, 7, 8]:
					for Round in [1,2,3,4,5,6,7,8,9,10, 11, 12]:

						#0詰め処理
						fyear = "{0:04d}".format(year)
						fplace = "{0:02d}".format(place)
						fname = "{0:02d}".format(name)
						fnumber = "{0:02d}".format(number)
						fRound = "{0:02d}".format(Round)
						file = str(fyear)+str(fplace)+str(fname)+str(fnumber)+str(fRound)
						print(file)
						link = 'http://db.netkeiba.com/race/'+file
						URL = urllib.request.urlopen(link).read()
						soup = BeautifulSoup(URL, 'lxml')
						tables = soup.findAll("table",{"class":"race_table_01 nk_tb_common"})
						if len(tables)==0:
							continue
						else:	
							#tableの中身を取ってくる.from<table>to</table>
							table = soup.findAll("table",{"class":"race_table_01 nk_tb_common"})[0]
							#ｔｒ属性をすべて取ってくる
							rows = table.findAll("tr")
							# fileOpen準備
							csvFile = codecs.open("keibaData.csv", "a", "utf-8")
							#csvFileに書き込み準備
							writer = csv.writer(csvFile)
							#direction初期化
							direction=""
							sex=""
							age=""
							try:
								for row in rows:
									#csvRow rist初期化
									csvRow = []
									#td or thごとに切ってcsvRowに追加
									count = 1
									for cell in row.findAll(['td']):
										cell = cell.get_text().strip()
										if count%22 == 5:
											sex = cell[0:1]
											cell = cell[1:]
											csvRow.append(sex)
										if count%22 == 19:
											direction=cell[1:2]
											cell=cell[4:]
										csvRow.append(cell)
										count=count+1
									if len(csvRow) == 0:
										continue
									else:
										csvRow.append(file)
										csvRow.append(str(direction))

									#記述
									writer.writerow(csvRow)
							finally:
								csvFile.close()
