# -*- coding: cp949 -*-
# module import
import requests
import urllib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import numpy as np
import csv
import torch
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import argparse




parser = argparse.ArgumentParser(description='Naver_Comment')
parser.add_argument('--candidate', type=str, default='������', help='candidate')
parser.add_argument('--startpage', type=int, default='1', help='startpage')
parser.add_argument('--endpage', type=int, default='50', help='endpage')
parser.add_argument('--date', type = str, default = '_0201_0308_', help = 'date')
args = parser.parse_args()

# ���� ����

search_QUERY = urllib.parse.urlencode({'query':args.candidate}, encoding='utf-8')
URL = f"https://search.naver.com/search.naver?where=news&query=%EB%8C%80%EC%84%A0&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds=2022.02.01&de=2022.03.09&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom20220201to20220309&is_sug_officeid=0"

LINK_PAT = "naver"
comment_url = "m_view=1&"


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# driver ����vi
s = Service("/NasData/home/ksy/Basic/project/project_test/data/driver_99/chromedriver")
driver = webdriver.Chrome(service = s, chrome_options = chrome_options)

make_file = open("news_comment"+"_"+str(args.startpage)+'_'+str(args.endpage)+"_"+args.date+".txt", 'w', encoding="UTF-8")
make_tot_file = open("news_comments_NAVER_"+str(args.startpage)+'_'+str(args.endpage)+"_"+args.date+".txt", mode="w", encoding="UTF-8")
make_file.close()
make_tot_file.close()



total_comment = 0

		
# �˻���� �� ��ũ ã�� : news.naver.com���� �����ϴ� ��� ��ũ ��ȯ
def get_news_links(startpage, endpage, link_pattern):
		links = set()
		for page in range(startpage, endpage+1):
				print(f"Scrapping page : {page}", end = " ") # Ȯ�ο�
				req = requests.get(f"{URL}&start={page}"); print(req.status_code)
				soup = BeautifulSoup(req.text, 'lxml')
				results = soup.find_all('a', {'href': re.compile(link_pattern), 'class':'info'})
				for result in results:
						links.add(result['href'])

		print(f"�� {len(links)}���� ���� ��ũ�� ã�ҽ��ϴ�.") # Ȯ�ο�
		return list(links)


# �� ������ ���� �ʿ��� ���� ��ũ������
def extract_info(url, wait_time=1,delay_time =0.3):



		try:
				driver.implicitly_wait(wait_time)
				driver.get(url)
				# ��� â ������ �� ������
			
						
						
				print(url)
				for _ in range(30):
						try:
								more_comments = driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div[2]/div[9]/a')
								more_comments.click()
								time.sleep(delay_time)
				
						except:
								break
		
						
				# html ������ �о����
				html = driver.page_source
				
				soup = BeautifulSoup(html, 'lxml')
				     
				
				# ��ó
				site = soup.find('h1').find("span").get_text(strip=True)
				# ��� ����
				title = soup.find('h3', {'id':'articleTitle'}).get_text(strip=True)
				
				# �ۼ� �ð�
				article_time = soup.find('span', {'class':'t11'}).get_text(strip=True)
				
				# ��л�
				press = soup.find('div', {'class':"press_logo"}).find('a').find('img')['title']
				# ��� ��
				
				
				total_com = soup.find("span", {"class" : "u_cbox_info_txt"}).get_text()
				
				
				# ��� �ۼ���
				nicks = soup.find_all("span", {"class":"u_cbox_nick"})
				nicks = [nick.text for nick in nicks]
				
				# ��� ��¥
				dates = soup.find_all("span", {"class":"u_cbox_date"})
				dates = [date.text for date in dates]
				
				# ��� ����
				contents = soup.find_all("span", {"class":"u_cbox_contents"})
				contents = [content.text for content in contents]
				
				
				f = open("news_comment"+"_"+str(args.startpage)+'_'+str(args.endpage)+"_"+args.date+".txt", 'a', encoding="UTF-8")
				reply = []
				for i in range(len(contents)):
						reply.append({'nickname':nicks[i],
						              'date':dates[i],
						              'contents':contents[i]})
				
						f.write(nicks[i]+','+dates[i]+','+ contents[i]+'\n')
				
				f.close()
				print("�Ϸ�", len(reply)) # Ȯ�ο�
				print("save comment number:", total_comment)
				if reply:
						print("comment:", reply[0])
				
				return {'site':site, 'title':title, 'article_time':article_time, 'press':press, 'total_comments':total_com, 'reply_content':reply}
		except:
				print(url)
				return {}	



							
					
# �� ������ ���鼭 ��ũ������
def extract_comments(links):
		contents = []
	
		for link in links:
				content = extract_info(f"{link}&m_view=1") # ������ ��ũ�� ���� extract_info �Լ� ȣ��
				if len(content) == 0: continue
				contents.append(content) # extract_info�� ����� ������ dict ����
		return contents


# main �Լ�
def main():
		news_links = get_news_links(args.startpage, args.endpage, LINK_PAT) 
		result = extract_comments(news_links)
		return result

# ��� ��� ���� �Լ�
def save_to_file(lst):
		print('save_to_file')
		file = open("news_comments_NAVER_"+str(args.startpage)+'_'+str(args.endpage)+"_"+args.date+".txt", mode="a", encoding="UTF-8")
		writer = csv.writer(file) 
		writer.writerow(['site', 'title', 'article_time', 'press', 'total_comments', 'contents'])
		for result in lst:
				writer.writerow(list(result.values()))
		file.close()

# �Լ� ����
NAVER_RESULT = main()
save_to_file(NAVER_RESULT)