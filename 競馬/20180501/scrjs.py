# -*- coding: utf_8 -*-  
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import lxml
import codecs
import csv
# PhantomJSをSelenium経由で利用します.
driver = webdriver.PhantomJS()

# PhantomJSで該当ページを取得＆レンダリングします
driver.get("http://www.tenki.jp/past/2017/06/26/amedas/3/16/44116.html")

# ちょっと待つ
# （ページのJS実行に時間が必要あれば）
# time.sleep(5) # 5s

# レンダリング結果をPhantomJSから取得します.
html = driver.page_source
bs = BeautifulSoup(html, 'lxml')
table = bs.findAll("table",{"class":"amedas_table_entries"})[0]
print(table)
rows = table.findAll("tr")
# fileOpen準備
csvFile = codecs.open("weather.csv", "a", "utf-8")
#csvFileに書き込み準備
writer = csv.writer(csvFile)

try:
	for row in rows:
		#csvRow rist初期化
		csvRow = []
		for cell in row.findAll(['td']):
			cell = cell.get_text().strip()
			csvRow.append(cell)

		writer.writerow(csvRow)
finally:
	csvFile.close()

# 終了
driver.quit()