#단국대학교병원
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
    wd=webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###

    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과', '순환기(심장)내과', '심장혈관내과','혈액종양내과']
    departmentLink = []
    doctordepartmentLink = []
    doctorLink = []
    hospital_code = '330710'
    dankookURL = 'https://www.dkuh.co.kr/html_2016/03/02'

    wd.get(dankookURL)
    result = urlopen(dankookURL)
    html = result.read()
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(2)
    datas = soup.find_all('a')
    origin = 'https://www.dkuh.co.kr/html_2016/03/'



    for data in datas:
        try:
            if data.attrs['title'] in department and '02.php' in data.attrs['href'] and not('www' in data.attrs['href']):
                departmentLink.append(origin + data.attrs['href'])

        except:
            pass

    #print(departmentLink)

    #각 과별로 의료진 링크가져오기
    for i in departmentLink:
        wd.get(i)
        #print(i)
        time.sleep(2)
        temp = wd.find_elements_by_class_name('viewBtn')
        num = len(temp)
        for a in range(0, num):
            if  '자세히보기' in temp[a].text:
                temp[a].click()
                doctorLink.append(wd.current_url)
                wd.get(i)
                temp = wd.find_elements_by_class_name('viewBtn')
                time.sleep(2)

    #각 의료진에서 정보 가져오기
    for doctor in doctorLink:
        wd.get(doctor)
        time.sleep(2)

        name = wd.find_element_by_class_name('name').text

        belong = '단국대학교병원'
        dpt = wd.find_element_by_css_selector('#contents_area > div.doctorIntro > ul > li.icon01.on > div > ul > li:nth-child(1) > ul > li').text
        if dpt == '':
            dpt = None


        career = []
        academy = []
        temp = []
        major = wd.find_element_by_css_selector('#contents_area > div.doctorIntro > ul > li.icon01.on > div > ul > li:nth-child(2) > ul > li').text
        major = major.split(', ')
        for m in major:
            if not('*' in m or '진료' in m):
                temp.append(m)

        major = ', '.join(temp)

        if major == '':
            major = None

        education = wd.find_element_by_css_selector('#contents_area > div.doctorIntro > ul > li.icon01.on > div > ul > li:nth-child(4) > ul > div').text
        if '\n\n' in education:
            education = education.split('\n\n')[0]
        education = education.replace('[경력사항]\n','')

        if education == '':
            education = None

        try:
            wd.find_element_by_link_text('경력').click()
            time.sleep(2)
            career = wd.find_element_by_css_selector('#contents_area > div.doctorIntro > ul > li.icon02.on > div > ul > li > ul > div').text
            if '\n\n' in career:
                career = career.split('\n\n')[0]
            if career == '':
                career = None

        except:
            career = None

        print(name)
        print(belong)
        print(dpt)
        print(education)
        print(career)

        link = wd.current_url

        cursor.execute(
            "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
            (name, belong, dpt, major, education, career, link, hospital_code))

        connect.commit()
