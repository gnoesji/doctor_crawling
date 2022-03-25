#영남대학교병원
import re
from urllib.request import urlopen

import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import MySQLdb


def doctor(connect, cursor, table_name, driver_path):

    ### 크롬드라이버 생성 ###
    wd=webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###
    # 기본 설정(관련 과 설정)
    department = ['순환기', '심장', '흉부', '혈관', '혈액', '내분비']
    departmentLink = []
    doctordepartmentLink = []
    doctorLink = []
    keyws = ['졸업', '수료', '취득', '석사', '박사', '학사', '취득']
    keyws2 = ['(전)', '교수', '위원', '인턴', '전문의', '레지던트', '조교수', '회원']
    belong = '영남대학교병원'
    hospital_code = '705040'

    yumcURL = 'https://yumc.ac.kr:8443/PageLink.do?link=yumc/08_minihp/contents_depart'

    wd.get(yumcURL)

    for i in department:
        try:
            data = wd.find_element_by_partial_link_text(i)
            departmentLink.append(data.get_attribute("href"))
        except:
            pass

    #print(departmentLink)

    # 의료진 링크 타고 들어가기
    for i in departmentLink:
        wd.get(i)
        wd.find_element_by_css_selector(
            '#yumccon > div.col-sm-3 > div > div.con-left.col-md-10.col-sm-11.p0 > nav > ul > li:nth-child(3) > a').click()
        origin = wd.current_url
        time.sleep(2)
        datas = wd.find_elements_by_class_name('bg2')
        num = len(datas)
        # 의료진 안으로 들어가기
        for now in range(0, num):
            major = None
            education = None
            career = None
            try:
                datas[now].find_element_by_tag_name('a').click()
                time.sleep(2)

                name = wd.find_element_by_class_name('mt0.blue').text

                try:
                    dpt = wd.find_element_by_class_name('d02.ml10.mb4').text
                    dpt_st = wd.find_element_by_css_selector('li.d02.ml10.mb4 > strong').text ## [진료과] 문자 제거
                    dpt = dpt.replace(dpt_st, '').strip()
                except NoSuchElementException:
                    dpt = None

                try:
                    major = wd.find_element_by_class_name('d05.ml10.mb4').text
                    major_st = wd.find_element_by_css_selector('li.d05.ml10.mb4 > strong').text
                    major = major.replace(major_st, '').strip()
                except NoSuchElementException:
                    major = None

                t = wd.find_element_by_css_selector('div.subbox')
                datas = t.text.split('\n')

                try:
                    ## 학력/경력 수집
                    option = wd.find_elements_by_class_name('blue.mt20')
                    value = wd.find_elements_by_class_name('subbox')

                    for idx, op in enumerate(option):
                        op = op.text
                        if op == '학력':
                            education = value[idx].text
                        elif op == '경력':
                            career = value[idx].text

                    if education is None and career is not None and '학력' in career:
                        temp_career = career
                        d_list = temp_career.split('\n\n')
                        education = d_list[0]
                        career = d_list[1]

                except:
                    pass

            except NoSuchElementException:
                key = now + 1
                name = wd.find_element_by_css_selector('#doc-name-%s > strong'%key).text
                dpt = wd.find_element_by_css_selector('#contentsWrap > div.jumbotron > div > div.col-md-3 > div > div.col-md-10.col-sm-12.p0 > div > h2').text

            if education is not None:
                education = education.split('\n')
                for e, edu in enumerate(education):
                    if '학력' in edu:
                        del education[e]
                    if edu == '':
                        del education[e]
                education = ', '.join(education)

            education_list = []
            career_list = []

            if career is not None:
                career = career.split('\n')
                for c, ca in enumerate(career):
                    if '경력' in ca:
                        del career[c]
                    if ca == '':
                        del career[c]
                if education is None:
                    for ic, vc in enumerate(career):
                        if "학사" in vc or "박사" in vc or "석사" in vc or "졸업" in vc or "졸" in vc:
                            education_list.append(vc)
                        else:
                            career_list.append(vc)

                career_tmp = career
                career = ', '.join(career)

            if education is None and career_tmp != career_list:
                career = ', '.join(career_list)

            if education_list != []:
                education = ', '.join(education_list)

            if career == '':
                career = None
            if education == '':
                education = None

            print(name)
            print(belong)
            print(dpt)
            print(major)
            print(education)
            print(career)

            cursor.execute(
                "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                (name, belong, dpt, major, education, career, wd.current_url, hospital_code))
            connect.commit()

            wd.get(origin)
            time.sleep(3)
            datas = wd.find_elements_by_class_name('bg2')