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

    ### 크롤링 코드 시작 ###

    # # 진료과 링크 담기
    # department = ["순환기내과", "심장내과", "심장외과", "흉부외과", "심장혈관외과", "소아심장과"]
    # URL = "https://www.pnuh.or.kr/pnuh/treat/list.do?rbsIdx=116"
    # wd.get(URL)
    # departmentLink = []
    # names = wd.find_elements_by_class_name('#contents_area > div.contentsWrap > article > div.medicalGrp > div.grp_list > div.grp.noTit > ul > li')
    # size = len(names)
    # for m in range(0, size):
    #     name = names[m].find_element_by_tag_name('h4').text
    #     if name in department:
    #         options = names[m].find_elements_by_tag_name('a')
    #         departmentLink.append(options[0].get_attribute('href'))

    BUSANURLLIST = ["https://www.pnuh.or.kr/pnuh/treat/info.do?rbsIdx=116&code=I2&type=2",
                    "https://www.pnuh.or.kr/pnuh/treat/info.do?rbsIdx=116&code=TS&type=2"]

    for urlitem in BUSANURLLIST:
        time.sleep(2)
        wd.get(urlitem)
        link = urlitem
        ### 의사 리스트가 존재하고, 상세페이지를 하나씩 접속하는 방식 ###
        doctorlist=wd.find_elements_by_css_selector("div.btn > a:nth-child(1) > span")
        for i in range(len(doctorlist)):
            wd.get(urlitem)
            time.sleep(2)
            doctorlist = wd.find_elements_by_css_selector("div.btn > a:nth-child(1) > span")
            button=doctorlist[i]
            button.click()
            time.sleep(1)
            wd.switch_to.window(wd.window_handles[-1])
            time.sleep(2)

            ### name_kor 수집 ###
            name_kor=wd.find_element_by_css_selector("#contents_area > div.teamIntro_doctor > div.mTit > h2 > strong").text
            # contents_area > div.teamIntro_doctor > div.mTit > h2 > strong
            ### belong 수집: notion_대학병원이름에서 병원 명칭(홈페이지)이름으로 저장 ###
            belong="부산대학교병원"
            ### hospital_code 수집: notion_대학병원이름에서 병원코드 저장 ###
            hospital_code ="602720"
            ### dpt 수집 ###
            dpt=wd.find_element_by_css_selector('#contents_area > div.teamIntro_doctor > div.mTit > h2').text
            dpt = dpt.split('\n')[0]
            ### major 수집 ###
            major=wd.find_element_by_css_selector("#contents_area > div.teamIntro_doctor > div.mInfo > dl > dd").text
            if major == '':
                major = None
            ### 학력 수집 ###
            education = None
            education_temp = []
            educationlist=wd.find_elements_by_css_selector("#contents_area > article > div > div > div:nth-child(3) > table > tbody > tr > td")
            for i in educationlist:
                if (i.text != ""):
                    education_temp.append(i.text)
                education = ", ".join(education_temp)
            ### 경력 수집 ###
            career = None
            career_temp = []
            time.sleep(1)
            careerlist=wd.find_elements_by_css_selector("#contents_area > article > div > div > div:nth-child(5) > table > tbody > tr > td")
            for j in careerlist:
                if (j.text != ""):
                    career_temp.append(j.text)
                career = ", ".join(career_temp)

            wd.close()
            wd.switch_to.window(wd.window_handles[0])

            ### mysql insert ###
            cursor.execute("INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);", (name_kor, belong, dpt, major, education, career, link, hospital_code))
            connect.commit()

    wd.close()
    wd.quit()

