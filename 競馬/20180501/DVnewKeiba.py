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
	#Webページ(HTML)の取得
	for year in [2017]:
		for place in [1,4,5,6,7,10]:
			for name in [4,5]:
				for number in [1,2,3,4,5,6,7,8,]:
					for Round in [10,11,12]:

						#0詰め処理
						fyear = "{0:04d}".format(year)
						fplace = "{0:02d}".format(place)
						fname = "{0:02d}".format(name)
						fnumber = "{0:02d}".format(number)
						fRound = "{0:02d}".format(Round)
						file = str(fyear)+str(fplace)+str(fname)+str(fnumber)+str(fRound)
						print(file)
						link = 'http://db.netkeiba.com/race/'+file
						print(link)
						URL = urllib.request.urlopen(link).read()
						soup = BeautifulSoup(URL, 'lxml')
						tables = soup.findAll("table",{"class":"race_table_01 nk_tb_common"})
						
						if len(tables)==0:
							continue
						else:
							date = soup.findAll("li",{"class":"result_link"})[0]
							date = date.get_text().strip()
							date = date[0:4]+'-'+date[5:7]+'-'+date[8:10]
							#tableの中身を取ってくる.from<table>to</table>
							table = soup.findAll("table",{"class":"race_table_01 nk_tb_common"})[0]
							#ｔｒ属性をすべて取ってくる
							rows = table.findAll("tr")
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
										if count%22 == 15:
											cell = cell[:3]
										if count%22 == 21:
											cell = cell.replace(',','')
										if count%22 == 19:
											direction=cell[1:2]
											cell = cell[4:]
										if cell == '':
											cell = '0'
										csvRow.append(cell)
										count=count+1
									if len(csvRow) == 0:
										continue
									else:
										csvRow.append(file)
										csvRow.append(str(direction))
										csvRow.append(date)
									# horse_idがマスターにあるかチェック。
									# あればhorse_idを取得。なければ登録して、登録したhorse_idを取得。
									#!!!!!!!!!!!!!!!!!!!!!動く!!!!!!!!!!!!!!!!!!!!!!
									
									sql = "SELECT horse_id FROM m_horse where horse_name = '" + csvRow[3] + "'"
									print(sql)
									cursor.execute(sql)
									print(1)
									tmpRow = cursor.fetchone()
									print(tmpRow)
									if ( tmpRow == None):
										sql = "INSERT INTO m_horse (horse_name) VALUES ('" + csvRow[3]+ "')"
										print(sql)
										cursor.execute(sql)
										cursor.execute("SELECT max(horse_id) FROM m_horse")
										csvRow[3]=str( cursor.fetchone()[0])
									else:
										csvRow[3] =str( tmpRow[0])
									tmpRow = []
									
									
									# jockey_idがマスターにあるかチェック。
									# あればjockey_idを取得。なければ登録して、登録したjockey_idを取得。
									sql = "SELECT jockey_id FROM m_jockey where jockey_name = '" + csvRow[7] + "'"
									cursor.execute(sql)
									tmpRow = cursor.fetchone()
									if ( tmpRow == None):
										sql = "INSERT INTO m_jockey (jockey_name) VALUES ('" + csvRow[7]+ "')"
										print(sql)
										cursor.execute(sql)
										cursor.execute("SELECT max(jockey_id) FROM m_jockey")
										csvRow[7]=str( cursor.fetchone()[0])
									else:
										csvRow[7] =str( tmpRow[0])

									# 取得したデータが、既にt_keiba_dataに存在するかのチェック（後回しで良い）
									sql="select id from t_keiba_data_result where horse_name_id = '"+ csvRow[3] +"' and jockey_id = '"+ csvRow[7] +"' and dates = '"+csvRow[24]+"'"
									print(sql)
									cursor.execute(sql)
									tmpId = cursor.fetchone()
									if tmpId != None:
										continue

									# trainer_idがマスターにあるかチェック。
									# あればtrainer_idを取得。なければ登録して、登録したtrainer_idを取得。
									sql = "SELECT trainer_id FROM m_trainer where trainer_name = '" + csvRow[19] + "'"
									cursor.execute(sql)
									tmpRow = cursor.fetchone()
									if ( tmpRow == None):
										sql = "INSERT INTO m_trainer (trainer_name) VALUES ('" + csvRow[19]+ "')"
										print(sql)
										cursor.execute(sql)
										cursor.execute("SELECT max(trainer_id) FROM m_trainer")
										csvRow[19]= str(cursor.fetchone()[0])
									else:
										csvRow[19] = str(tmpRow[0])
									
									# owner_idがマスターにあるかチェック。
									# あればowner_idを取得。なければ登録して、登録したowner_idを取得。
									sql = "SELECT owner_id FROM m_owner where owner_name = '" + csvRow[20] + "'"
									cursor.execute(sql)
									tmpRow = cursor.fetchone()
									if ( tmpRow == None):
										sql = "INSERT INTO m_owner (owner_name) VALUES ('" + csvRow[20]+ "')"
										print(sql)
										cursor.execute(sql)
										cursor.execute("SELECT max(owner_id) FROM m_owner")
										csvRow[20]= str(cursor.fetchone()[0])
									else:
										csvRow[20] = str(tmpRow[0])
									tmpRow = []
									
									# INSERT
									
									rowkanma = "','".join(csvRow)
									rowkanma = "'" + rowkanma + "'"
									
									print(len(csvRow))
									sql = "INSERT INTO t_keiba_data_result (rank,frame_number,horse_number,horse_name_id,horse_sex,horse_year,basis_weight,jockey_id,times,margin,time_index,passing,uppers,win,popularity,horse_weight,torture_time,stable_comment,remarks,trainer_id,owner_id,prize,url,trainer_place,dates) VALUES ("+rowkanma+")"
									print(sql)
									cursor.execute(sql)
									connection.commit()
									
							except MySQLdb.Error as e:
								print('MySQLdb.Error: ', e)

	StopSSHSession(server, connection)
