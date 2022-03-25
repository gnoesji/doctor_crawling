#서울한양대학교병원
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
    wd = webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###

    # 기본 설정(관련 과 설정)
    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과', '순환기(심장)내과', '심장혈관내과','혈액종양내과']
    departmentLink = []
    doctordepartmentLink = []
    doctorLink = []
    hospital_code = '330710'
    hanyangURL = 'https://seoul.hyumc.com/seoul/mediteam/mediofCent.do'

    wd.get(hanyangURL)
    time.sleep(2)
    datas = wd.find_elements_by_tag_name('button')
    num = len(datas)
    for i in range(0,num):
        if datas[i].text in department:
            datas[i].click()
            wd.find_element_by_link_text('의료진 소개').click()
            departmentLink.append(wd.current_url)
            wd.get(hanyangURL)
            datas = wd.find_elements_by_tag_name('button')
            time.sleep(2)

    #print(departmentLink)

    #의료진 링크로 타고 들어가기

    for i in departmentLink:
        wd.get(i)
        datas = wd.find_elements_by_class_name('doctor_name')
        num = len(datas)
        for now in range(0, num):
            temp = datas[now].find_element_by_tag_name('a')
            temp.click()
            doctor = wd.current_url
            name = wd.find_element_by_class_name('name').text
            belong = '서울한양대학교병원'
            dpt = wd.find_element_by_css_selector('#contents > div > article > div > h1 > span.treatment_part').text
            major = wd.find_element_by_class_name('professional_field').text
            if major == '':
                major = None
            try:
                education = wd.find_element_by_css_selector('#contents > div > section.clfx.mt20 > div > article:nth-child(1) > div > div:nth-child(1)').text
                education = education.split('\n')
                for idx, val in enumerate(education):
                    if val[0:2] == '- ':
                        education[idx] = val[2:]
                education = ', '.join(education)
            except:
                pass
            if education == '':
                education = None

            try:
                career = wd.find_element_by_css_selector('#contents > div > section.clfx.mt20 > div > article:nth-child(1) > div > div:nth-child(2)').text
                career = career.split('\n')
                for idx, val in enumerate(career):
                    if val[0:2] == '- ':
                        career[idx] = val[2:]
                career = ', '.join(career)
            except:
                pass
            if career == '':
                career = None

            print(name)
            print(belong)
            print(dpt)
            print(major)
            print(education)
            print(career)

            link = wd.current_url
            cursor.execute(
                "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                (name, belong, dpt, major, education, career, link, hospital_code))
            connect.commit()

            wd.get(i)
            time.sleep(2)
            datas = wd.find_elements_by_class_name('doctor_name')

    #connect.commit()