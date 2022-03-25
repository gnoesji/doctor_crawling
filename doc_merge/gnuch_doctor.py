#창원경상국립대학교병원
import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import MySQLdb

def doctor(connect, cursor, table_name, driver_path):
    ### 크롬드라이버 생성 ###
    wd = webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###
    # 기본 설정(관련 과 설정)
    department = ['순환기', '심장', '흉부','혈액']
    departmentLink = []
    doctordepartmentLink = []
    doctorLink = []
    keyws = ['졸업', '수료','취득','석사','박사','학사','취득']
    keyws2 = ['(전)', '교수', '위원', '인턴', '전문의', '레지던트', '조교수' ,'회원']
    belong = '창원경상국립대학교병원'
    memory = []

    gnuhURL = 'https://www.gnuch.co.kr/gnuh/treat/docList.do?rbsIdx=55'
    hospital_code = '641121'
    wd.get(gnuhURL)
    time.sleep(2)

    for i in department:
        try:
            search = wd.find_element_by_id("key")
            search.send_keys(i)
            search.send_keys(Keys.RETURN)
            time.sleep(3)
            datas = wd.find_elements_by_class_name('icoIntro')
            num = len(datas)

            for now in range(0,num):
                datas[now].click()
                time.sleep(3)


                name = wd.find_element_by_class_name('doctor_name').text
                name = name.split('[')[0]
                double = False
                dpt = wd.find_element_by_css_selector('#contents_area > div.profile.group > div.cont > div > ul > li:nth-child(1) > h5 > span').text
                dpt = dpt[1:-1]
                try:
                    major = wd.find_element_by_css_selector('#contents_area > div.profile.group > div.cont > div.doctor_major > ul > li.title > span').text
                except:
                    major = ''
                try:
                    temp = wd.find_element_by_css_selector('#contents_area > div.profile.group > div.cont').text
                    datas = temp.split('\n')
                    career = []
                    education = []

                    for data in datas:
                        if '[학력]' in data:
                            education.append(data.split('[학력] ')[1])
                        elif '[경력] ' in data:
                            career.append(data.split('[경력] ')[1])

                except:
                    career = ''
                    education = ''


                print(name)
                career = ', '.join(career)
                education = ', '.join(education)

                for m in memory:
                    if name == m[0] and major == m[1]:
                        double = True

                memory.append((name, major))

                if dpt == '':
                    dpt = None
                if major == '':
                    major = None
                if education == '':
                    education = None
                if career == '':
                    career = None

                if double == False:
                    ### mysql insert ###
                    cursor.execute(
                        "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                        (name, belong, dpt, major, education, career, wd.current_url, hospital_code))
                    connect.commit()

                wd.get(gnuhURL)
                time.sleep(3)
                search = wd.find_element_by_id("key")
                search.send_keys(i)
                search.send_keys(Keys.RETURN)
                time.sleep(3)
                datas = wd.find_elements_by_link_text('상세소개')

        except:
            pass
