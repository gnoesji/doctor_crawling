#경상국립대학교병원
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import MySQLdb
import pymysql


def doctor(connect, cursor, table_name, driver_path):

    ### 크롬드라이버 생성 ###
    wd = webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###

    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '암센터 흉부외과','혈액종양내과']
    departmentLink = []
    doctordepartmentLink = []
    doctorLink = []
    keyws = ['졸업', '수료','취득','석사','박사','학사','취득']
    #keyws2 = ['(전)', '교수', '위원', '인턴', '전문의', '레지던트', '조교수' ,'회원']
    belong = '경상국립대학교병원'

    gnuhURL = 'https://www.gnuh.co.kr/gnuh/treat/docList.do?rbsIdx=55&it=5'
    hospital_code='660710'

    wd.get(gnuhURL)
    time.sleep(2)

    for i in department:
        try:
            wd.find_element_by_link_text(i).click()
            time.sleep(3)
            datas = wd.find_elements_by_class_name('icoIntro')
            num = len(datas)
            for now in range(0,num):
                datas[now].click()
                time.sleep(3)


                name = wd.find_element_by_class_name('doctor_name').text
                name = name.split(' ')[0]
                dpt = wd.find_element_by_css_selector('#contents_area > div.profile.group > div.cont > div.doctor_major > ul > li:nth-child(1) > h5 > span').text
                dpt = dpt[1:-1]

                try:
                    major = wd.find_element_by_css_selector('#contents_area > div.profile.group > div.cont > div.doctor_major > ul > li.title > span').text
                except:
                    major = None

                ##학력/경력
                temp = wd.find_element_by_css_selector('#eduCareerContents').text
                datas = temp.split('\n')

                career = []
                education = []

                for data in datas:
                    if any(keyw in data for keyw in keyws):
                        education.append(data)
                    elif data == '':
                        del data
                    else:
                        career.append(data)

                career = ', '.join(career)
                education = ', '.join(education)
                if dpt == '':
                    dpt = None
                if major == '':
                    major = None
                if career == "":
                    career = None
                if education == "":
                    education = None

                cursor.execute(
                    "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                    (name, belong, dpt, major, education, career, wd.current_url, hospital_code))
                connect.commit()

                wd.get(gnuhURL)
                time.sleep(1)
                wd.find_element_by_link_text(i).click()
                time.sleep(1)
                datas = wd.find_elements_by_link_text('상세소개')

        except:
            pass

