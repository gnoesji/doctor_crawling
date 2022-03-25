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
    CHONNAMURLLIST = ["https://www.cnuh.com/medical/info/dept.cs?act=view&mode=doctorList&deptCd=IMC", "https://www.cnuh.com/medical/info/dept.cs?act=view&mode=doctorList&deptCd=CS"]
    for urlitem in CHONNAMURLLIST:
        time.sleep(2)
        wd.get(urlitem)
        dpt_temp = ""
        if 'IMC' in urlitem:
            dpt_temp = '순환기내과'
        elif 'CS' in urlitem:
            dpt_temp = '흉부외과'

        doctorlist=wd.find_elements_by_css_selector("#contents > div.sectionArea > ul > li > div > div.doctor > dl > dd.lkList > ul > li.intro > a > span")
        for i in range(len(doctorlist)):
            wd.get(urlitem)
            time.sleep(2)
            doctorlist = wd.find_elements_by_css_selector("#contents > div.sectionArea > ul > li > div > div.doctor > dl > dd.lkList > ul > li.intro > a > span")
            button=doctorlist[i]
            button.click()
            time.sleep(2)

            ### name_kor 수집 ###
            name_kor=wd.find_element_by_css_selector("#contents > div.doctorIntro > div.introHeader > div > dl > dt").text
            belong="전남대학교병원"
            hospital_code = "501710"
            dpt = dpt_temp
            major=wd.find_element_by_css_selector("#contents > div.doctorIntro > div.introHeader > div > dl > dd").text[4:]
            education = ""
            education_temp = []
            try:
                edu_but = wd.find_element_by_css_selector('#introDetail01 > div:nth-child(1) > p > button')
                edu_but.send_keys(Keys.ENTER)
            except:
                pass
            educationlist = wd.find_elements_by_css_selector(
                "#introDetail01 > div:nth-child(1) > dl > dd > span.txt")
            if educationlist[0].text == "": #txt내용이 date에 들어가있는 경우
                educationlist = wd.find_elements_by_css_selector(
                "#introDetail01 > div:nth-child(1) > dl > dd > span.date")
            for i in educationlist:
                #print(i.text)
                if (i.text != ""):
                    education_temp.append(i.text)
                education = ", ".join(education_temp)
            if education == "":
                education = None

            try:
                car_but = wd.find_element_by_css_selector('#introDetail01 > div:nth-child(2) > p > button')
                car_but.send_keys(Keys.ENTER)
            except:
                pass
            career = ""
            career_temp = []
            careerlist = wd.find_elements_by_css_selector("#introDetail01 > div:nth-child(2) > dl > dd > span.txt")
            if careerlist[0].text == "": #txt내용이 date에 들어가있는 경우
                careerlist = wd.find_elements_by_css_selector(
                "#introDetail01 > div:nth-child(2) > dl > dd > span.date")
            for j in careerlist:
                #print(j.text)
                if (j.text != ""):
                    career_temp.append(j.text)
                career = ", ".join(career_temp)
            if career == "":
                career = None
            link=wd.current_url
            ### mysql insert ###
            cursor.execute(
                "INSERT INTO " + table_name + "(name_kor, belong,department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                (name_kor, belong, dpt, major, education, career, link, hospital_code))

    connect.commit()

    wd.close()
    wd.quit()
