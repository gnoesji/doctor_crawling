### import ###
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import requests
import re
import pymysql

def doctor(connect, cursor, table_name, driver_path):

    ### 크롬드라이버 생성 ###
    wd=webdriver.Chrome(executable_path=driver_path)

    # 경희대학교

    # kname, belong, major, education, career, link
    KHUNGHEELIST=["https://www.khuh.or.kr/03/01_06.php?section=6","https://www.khuh.or.kr/03/01_29.php?section=29"]
    for urlitem in KHUNGHEELIST:
        wd.get(urlitem)
        list = wd.find_elements_by_css_selector("table > tbody > tr:nth-child(14) > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr")
        for i in range(4, (len(list) - 1), 3):
            info=list[i]
            # detail01
            name_kor=info.find_element_by_css_selector("td:nth-child(2) > b").text
            belong="경희대학교병원"
            hospital_code="130710"
            dpt = None
            major=info.find_element_by_css_selector("td:nth-child(4) > font > table > tbody > tr:nth-child(6) > td:nth-child(2)").text

            education=""
            career=""
            temp=info.find_element_by_css_selector("td:nth-child(4) > font > table > tbody > tr:nth-child(3) > td:nth-child(2)").text
            templist=temp.split("\n")
            cnt=0
            for i in templist:
                if (cnt<3):
                    if (("석사" not in i)&("박사" not in i)&("학사" not in i)&("졸업" not in i)):
                        career=career+i+","
                        cnt = cnt + 1
                        continue
                    education=education+i+","
                    cnt=cnt+1
                    continue
                if(i!="")&("경력" not in i):
                    career=career+i+","
            link=urlitem

            ### mysql insert ###
            cursor.execute(
                "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                (name_kor, belong, dpt, major, education, career, link, hospital_code))
            connect.commit()

    wd.close()
    wd.quit()
