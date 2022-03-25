### import ###
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import requests
import re
import pymysql
from selenium.common.exceptions import NoSuchElementException

### 연세대학교원주세브란스기독병원 의료진 테이블 ###
def doctor(connect, cursor, table_name, driver_path):
    ### 크롬드라이버 생성 ###
    wd = webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###
    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    departmentLink = []
    doctocdepartmentLink = []
    doctorLink = []

    severanceWonjuURL = 'https://www.ywmc.or.kr/web/www/medical_office'
    wd.get(severanceWonjuURL)

    contents = wd.find_element_by_class_name('content')
    for i in department:
        data = contents.find_elements_by_partial_link_text(i)
        for a in data:
            departmentLink.append(a.get_attribute("href"))

    for i in departmentLink:
        wd.get(i)
        options = wd.find_elements_by_tag_name('a')
        for i in options:
            if ('의료진' == i.text):
                doctocdepartmentLink.append(i.get_attribute('href'))

    for i in doctocdepartmentLink:
        wd.get(i)
        doclist = wd.find_elements_by_css_selector('div.doct_list > div.d_bx > div.d_info')
        for index, value in enumerate(doclist):
            dpt = None
            major = None
            education = None
            career = None
            link = None
            namelist = value.find_element_by_class_name('name').text
            if namelist != '일반진료':
                ### name_kor 수집 ###
                name_kor = namelist
                ### belong 수집: notion_대학병원이름에서 병원 명칭(홈페이지)이름으로 저장 ###
                belong = "연세대학교원주세브란스기독병원"
                ### hospital_code 수집: notion_대학병원이름에서 병원코드 저장 ###
                hospital_code = "220710"

                ### major 수집 ###
                try:
                    major = value.find_element_by_class_name('dpart').find_element_by_tag_name('p').text
                except NoSuchElementException:
                    pass
                lk = wd.current_url
                raw = requests.get(lk)
                html = BeautifulSoup(raw.text, "html.parser")

                d_list = html.select((
                                             '#_doctorView_WAR_reservportlet_pop_rsv_cplt-%s > div > div.pop_cont > div.doctor_bx > div.info' % index))
                for dlst in d_list:
                    dpt = dlst.select_one('p').text
                # 학력box인지 학회box인지 고르는 부분
                ls = html.select((
                                             '#_doctorView_WAR_reservportlet_pop_rsv_cplt-%s > div > div.pop_cont > div.portfolio > div' % index))
                for lst in ls:
                    op = lst.select_one('p').text
                    ### education 수집 ###
                    try:
                        if op == '학력사항':
                            education = str(lst.select_one("ul > li")).split('<br/>')
                            for j in range(0, len(education)):
                                education[j] = education[j].strip()
                            education = ', '.join(education)

                            if '<li>' in education or '</li>' in education:
                                education = education.replace('<li>', '')
                                education = education.replace('</li>', '')

                    except:
                        pass
                    ### career 수집 ###
                    try:
                        if op == '교육 및 연구 경력':
                            career = str(lst.select_one("ul > li")).split('<br/>')
                            for j in range(0, len(career)):
                                career[j] = career[j].strip()
                            career = ', '.join(career)

                            if '<li>' in career or '</li>' in career:
                                career = career.replace('<li>', '')
                                career = career.replace('</li>', '')
                            career = career.replace(' ? ', '-')
                    except:
                        pass

                print(name_kor)
                print(belong)
                print(dpt)
                print(major)
                print(education)
                print(career)


                ### mysql insert ###
                cursor.execute(
                    "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                    (name_kor, belong, dpt, major, education, career, link, hospital_code))
    connect.commit()
    
    wd.close()
    wd.quit()
