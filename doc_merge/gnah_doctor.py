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
    url="https://www.gnah.co.kr/kor/CMS/DeptMgr/list.do?mCode=MN021"
    wd.get(url)
    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    #심장내과, 흉부외과
    departmentLink=[]
    doctordepartmentLink=[]
    doctorLink=[]

    ###한번에 커밋하기 위한 작업###
    name_kor=[]
    belong=[]
    major=[]

    careers=[]
    link=[]
    data=[]
    educations=[]
    buttons=[]
    dpt=[]

    data.append(wd.find_element_by_xpath('/html/body/div[3]/article/div[2]/div[2]/div[2]/div[1]/ul/li[32]/div/div/a[1]'))
    data.append(wd.find_element_by_xpath("/html/body/div[3]/article/div[2]/div[2]/div[2]/div[1]/ul/li[16]/div/div/a[1]"))
    k=0
    s=0

    for a in data:
        departmentLink.append(a.get_attribute("href"))

    for i in departmentLink:
        wd.get(i)
        time.sleep(1)
        temp=wd.find_element_by_css_selector('#tab3 > a').click()
        time.sleep(2)
        buttons = wd.find_elements_by_css_selector('#intro3 > div > div.wrap-timeDoctors > ul > li')
        temp_edu = []
        temp_career = []
        for j in range(1, len(buttons)+1):
            wd.find_element_by_css_selector(
                '#intro3 > div > div.wrap-timeDoctors > ul > li:nth-child(%s) > div.side-R > div.btnBox.has2 > a.detail.bg-btn'%(j)
            ).send_keys(Keys.ENTER)
            ### name_kor 수집 ###
            name_kor.append(wd.find_element_by_css_selector('#cont > div > div.dv-mainShot > div.dvMsg > div > p > span.doctName'))
            name_kor[k]=name_kor[k].text

            ### belong 수집: notion_대학병원이름에서 병원 명칭(홈페이지)이름으로 저장 ###
            belong="강릉아산병원"
            ### hospital_code 수집: notion_대학병원이름에서 병원코드 저장 ###
            hospital_code ="210810"

            ### dpt 수집 ###
            dpt.append(wd.find_element_by_css_selector('#cont > div > div.dv-mainShot > div.dvMsg > div > span'))
            dpt[k]=dpt[k].text

            for j in range(0,len(dpt)):
                if dpt[j] == '':
                    dpt[j] = None

            ### major 수집 ###
            major.append(wd.find_element_by_css_selector('#cont > div > div.dv-mainShot > div.dvMsg > div > dl > dd'))
            major[k]=major[k].text

            education = []  # 학력
            career = []  # 경력
            ###education, career수집###
            d_list = wd.find_elements_by_class_name('tText')
            for i in range(len(d_list)):
                d_list[i] = d_list[i].text

            for idx, val in enumerate(d_list): #val은 한사람의 경력 한개씩
                # 학력
                if "학사" in val or "박사" in val or "석사" in val or "졸업" in val:
                    education.append(val)
                # 경력
                else:
                    career.append(val)

            education = ", ".join(education)
            career = ", ".join(career) # 한사람의 학력이 str 뭉텅이로 묶여있음

            if education == '':
                education = None
            if career == '':
                career = None

            print(education)
            print(career)
            print('!!')
            educations.append(education)
            careers.append(career)


            ###link수집###
            link.append(wd.current_url)
            k=k+1
            wd.back()
            time.sleep(2)


    for i in range(len(name_kor)):
        cursor.execute("insert into "+table_name+"(name_kor, belong, department, major,education,career,link,hospital_code) values(%s, %s,%s,%s,%s,%s,%s,%s);",(name_kor[i],belong, dpt[i], major[i],educations[i],careers[i],link[i],hospital_code))
    connect.commit()
    
    wd.close()
    wd.quit()

