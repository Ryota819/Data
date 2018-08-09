# -*- coding: utf_8 -*-  
#pytho3.5
import csv
import urllib.request
import lxml
from bs4 import BeautifulSoup 
import re
import codecs

import MySQLdb
from sshtunnel import SSHTunnelForwarder
from time import sleep

import DBconnection

# -------------------- main --------------------


if __name__ == '__main__':
	
	server = StartSSHSession()
	connection = GetConnection(server.local_bind_port)
	cursor = connection.cursor()

	#2014-2016年に東京と中山で行われた全大会・全日数・全ラウンドの勝敗データを取得
	for year in [2018]:
		for place in [1,2,3,4,5,6,7,8,9,10]:
			for name in [1,2,3]:
				for number in [1,2,3,4,5]:
					for Round in [10, 11, 12]:

						#0詰め処理
						fyear = "{0:04d}".format(year)
						fplace = "{0:02d}".format(place)
						fname = "{0:02d}".format(name)
						fnumber = "{0:02d}".format(number)
						fRound = "{0:02d}".format(Round)
						file = str(fyear)+str(fplace)+str(fname)+str(fnumber)+str(fRound)

						#Webページ(HTML)の取得
						#URLルール:'http://db.netkeiba.com/race/'+出走年（４桁）+場所（２桁）+大会名（２桁）+第何回（２桁）+何ラウンド（２桁）
						link = 'http://race.netkeiba.com/?pid=race_old&id=c'+file
						URL = urllib.request.urlopen(link).read()
						soup = BeautifulSoup(URL, 'lxml')
						table = soup.findAll("table",{"class":"race_table_old nk_tb_common"})
						if len(table)==0:
							continue
						else:
						#tableの中身を取ってくる.from<table>to</table>
							table = table[0]
							date = soup.findAll("title")[0]
							print(date)
							date = date.get_text().strip()
							print(date)
							date = date[0:4]+'-'+date[5:7]+'-'+date[8:10]
							print(date)
							#ｔｒ属性をすべて取ってくる
							rows = table.findAll("tr")
							
							sex = "" 
							try:
								for row in rows:
									#csvRow rist初期化
									csvRow = []
									count = 1
									#td or thごとに切ってcsvRowに追加
									for cell in row.findAll(['td']):
										cell = cell.get_text().strip()
										if count == 5: 
											sex = cell[0:1]
											cell = cell[1:]
											csvRow.append(sex)

										csvRow.append(cell)
										if count == 1:
											csvRow.pop()
										if count == 2:
											csvRow.pop()
										if count == 3:
											csvRow.pop()
										if count == 9:
											csvRow.pop()
										if count == 12:
											csvRow.pop()
										if count == 13:
											csvRow.pop()
										count += 1
									if len(csvRow) == 0:
										continue
									else:
										csvRow.append(file)
										csvRow.append(str(date))
									
									# horse_idがマスターにあるかチェック。
									# あればhorse_idを取得。なければ登録して、登録したhorse_idを取得。
									#!!!!!!!!!!!!!!!!!!!!!動く!!!!!!!!!!!!!!!!!!!!!!
									#print(csvRow[0])
									sql = "SELECT horse_id FROM m_horse where horse_name = '" + csvRow[0] + "'"
									#print(sql)
									cursor.execute(sql)
									tmpRow = cursor.fetchone()
									#print(tmpRow)
									if ( tmpRow == None):
										sql = "INSERT INTO m_horse (horse_name) VALUES ('" + csvRow[0]+ "')"
										#print(sql)
										cursor.execute(sql)
										cursor.execute("SELECT max(horse_id) FROM m_horse")
										csvRow[0]=str( cursor.fetchone()[0])
									else:
										csvRow[0] =str( tmpRow[0])
									tmpRow = []
									
									# jockey_idがマスターにあるかチェック。
									# あればjockey_idを取得。なければ登録して、登録したjockey_idを取得。
									sql = "SELECT jockey_id FROM m_jockey where jockey_name like '" + csvRow[4] + "%'"
									#print(sql)
									cursor.execute(sql)
									tmpRow = cursor.fetchone()
									#print(tmpRow)
									if ( tmpRow != None):
										csvRow[4] =str( tmpRow[0])
									tmpRow = []
									
									# trainer_idがマスターにあるかチェック。
									# あればtrainer_idを取得。なければ登録して、登録したtrainer_idを取得。
									sql = "SELECT trainer_id FROM m_trainer where trainer_name like '" + csvRow[5] + "%'"
									#print(sql)
									cursor.execute(sql)
									tmpRow = cursor.fetchone()
									#print(tmpRow)
									if ( tmpRow != None):
										csvRow[5] = str(tmpRow[0])
									tmpRow = []

									# INSERT
									
									rowkanma = "','".join(csvRow)
									rowkanma = "'" + rowkanma + "'"
									
									#print(len(csvRow))
									sql = "INSERT INTO t_keiba_predata (horse_name_id,horse_sex,horse_year,basis_weight,jockey_id,trainer_id,preOdds,popularity,url,date) VALUES ("+rowkanma+")"
									#print(sql)
									cursor.execute(sql)
									connection.commit()
									
									
							except MySQLdb.Error as e:
								print('MySQLdb.Error:' , e)
	StopSSHSession(server , connection)