### import ###
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import requests
import re
import pymysql

### 계명대학교동산병원 의료진 테이블 ###
def doctor(connect, cursor, table_name, driver_path):
    ### 크롬드라이버 생성 ###
    wd = webdriver.Chrome(executable_path=driver_path)
    ### 크롤링 코드 시작 ###
    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    departmentLink = []
    doctorLink = []
    keimyungURL = 'http://dongsan.dsmc.or.kr/content/02health/01_01.php'
    wd.get(keimyungURL)
    # 진료과 링크 담기
    for i in department:
        data = wd.find_elements_by_partial_link_text(i)
        for a in data:
            departmentLink.append(a.get_attribute("href"))
    # 의료진 페이지 담기
    for i in departmentLink:
        wd.get(i)
        dpt = wd.find_element_by_css_selector('#cont_wrap > div > div.tit_wrap > div.tit > p.btxt > strong').text
        options = wd.find_elements_by_tag_name('a')
        for i in options:
            if ('의료진소개' in i.text):
                doctorLink.append(i.get_attribute('href'))
    # 각 의료진 페이지
    for doctor in doctorLink:
        major = []
        education = []
        career = []
        d_list = []
        wd.get(doctor)
        time.sleep(2)
        text = wd.find_element_by_css_selector('div.treat_doc_tit > p.btxt').text
        dpt = wd.find_element_by_css_selector('body > div.treat_doc_tit > p.stxt').text
        dpt = dpt[1:-1]
        ### name_kor 수집 ###
        name_kor = text[0:len(text) - 3]
        ### belong 수집: notion_대학병원이름에서 병원 명칭(홈페이지)이름으로 저장 ###
        belong = "계명대학교동산병원"
        ### hospital_code 수집: notion_대학병원이름에서 병원코드 저장 ###
        hospital_code = "700720"

        ### major 수집 ###
        text2 = wd.find_element_by_css_selector('div.history_top > div.wrap > div.box > dl > dd').text
        major = text2
        major = major.replace('()', '')
        major = major.replace('( )', '')
        if major == []:
            major = None
        ### 학력/경력 수집 -> 구분 불가능, career에 함께 저장###
        ls = wd.find_elements_by_css_selector('body > div.doc_cont > div.box1')
        for lst in ls:
            op = lst.find_element_by_tag_name('h3').text
            if op == '학력/경력':
                li = lst.find_elements_by_css_selector('table > tbody > tr > td')
                for list in li:
                    text = list.text
                    d_list.append(text)

        for idx, val in enumerate(d_list):  # val은 한사람의 경력 한개씩
            # 학력
            if "학사" in val or "박사" in val or "석사" in val or "졸업" in val:
                education.append(val)
            # 경력
            else:
                career.append(val)

        education = ", ".join(education)
        career = ", ".join(career)  # 한사람의 학력이 str 뭉텅이로 묶여있음

        if education == "":
            education = None
        if career == "":
            career = None

        ### link 수집 ###
        link = doctor

        ### mysql insert ###
        cursor.execute(
            "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
            (name_kor, belong, dpt, major, education, career, link, hospital_code))

        wd.switch_to.default_content()
    connect.commit()
  
    wd.close()
    wd.quit()
