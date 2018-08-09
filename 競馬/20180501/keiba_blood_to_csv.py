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
#	for year in [2014]:
#		for place in [1,2,3,4,5,6,7,8,9,10]:
#			for name in [1,2,3,4,5]:
#				for number in [1, 2, 3, 4, 5, 6, 7, 8]:
#					for Round in [1,2,3,4,5,6,7,8,9,10, 11, 12]:

						#0詰め処理
#						fyear = "{0:04d}".format(year)
#						fplace = "{0:02d}".format(place)
#						fname = "{0:02d}".format(name)
#						fnumber = "{0:02d}".format(number)
#						fRound = "{0:02d}".format(Round)
#						file = str(fyear)+str(fplace)+str(fname)+str(fnumber)+str(fRound)
#						print(file)
						link = 'http://db.netkeiba.com/horse/ped/2015104976/'
						URL = urllib.request.urlopen(link).read()
						soup = BeautifulSoup(URL, 'lxml')
						
						horse_name = soup.findAll("title")[0]
						horse_name = horse_name.strip()
						horse_name.decode('utf-8')
						print(horse_name)
						
						#Nname = len(horse_name)-17
						#print(Nname)
						#new_horse_name = horse_name[6:Nname]
						#print(new_horse_name)
						
						tables = soup.findAll("table",{"class":"blood_table detail"})
#						if len(tables)==0:
#							continue
#						else:	
						#tableの中身を取ってくる.from<table>to</table>
						table = soup.findAll("table",{"class":"blood_table detail"})[0]
						#ｔｒ属性をすべて取ってくる
						rows = table.findAll("tr")
						#print (rows)
						# fileOpen準備
						csvFile = codecs.open("BloodKeibaData.csv", "a", "utf-8")
						#csvFileに書き込み準備
						writer = csv.writer(csvFile)
						#direction初期化
						direction=""
						sex=""
						age=""
						i = 0
						try:
							csvRow = []
							for row in rows:
								#print (row)
								
								#csvRow rist初期化
								
								#td or thごとに切ってcsvRowに追加
								count = 1
								for cell in row.findAll(['a']):
									cell = cell.get_text().strip()
									if cell == '血統':
										continue
									if cell == '産駒':
										continue
									#print (cell)
									i=i+1
									#print (i)
									csvRow.append(cell)
									count=count+1
								#記述
							#writer.writerow(csvRow)
						finally:
							csvFile.close()
