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
    url="https://www.cbnuh.or.kr/sub03/sub03_01.jsp"
    wd.get(url)

    #department=['심장내과','흉부외과']
    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    departmentLink=[]
    doctordepartmentLink=[]
    doctorLink=[]

    ###한번에 커밋하기 위한 작업###
    name_kor=[]
    belong=[]
    dpt = []
    major=[]
    education=[] #학력
    career=[] #경력
    link=[]
    education_list = []
    career_list = []


    ###진료과 링크 담은 후 크롤링하기###
    for i in department:
        data=wd.find_elements_by_partial_link_text(i)
        for a in data:
            departmentLink.append(a.get_attribute("href"))
    for i in departmentLink:
        wd.get(i)
        time.sleep(1)
        buttons=wd.find_elements_by_partial_link_text("상세보기")
        for j in range(0,len(buttons)):
            doctordepartmentLink.append(buttons[j].get_attribute('href'))
        
    #print(len(doctordepartmentLink))

    j=0
    k=1
    s=0
    for i in doctordepartmentLink:
        wd.get(i)
        ###name_kor수집###
        name_kor.append(wd.find_element_by_xpath('//*[@id="content_area"]/div/div[1]/ul/li[1]'))
        name_kor[j]=name_kor[j].text
        #print(name_kor[j])
        ###belong수집: notion_대학병원이름에서 병원 명칭(홈페이지)이름으로 저장 ###
        belong="충북대학교병원"
        ###hospital_code수집: notion_대학병원이름에서 병원코드 저장 ###
        hospital_code ="361710"
        ###dpt###
        dpt.append(wd.find_element_by_xpath('//*[@id="content_area"]/div/div[1]/ul/li[2]'))
        dpt[j] = dpt[j].text[6:len(dpt[j].text)]
        #print(dpt[j])
        ###major수집###
        major.append(wd.find_element_by_xpath('//*[@id="content_area"]/div/div[2]/table/tbody/tr[1]/td'))
        major[j] = major[j].text
        #print(belong)
        #print(major[j])

        temp_edu = []
        temp_career = []
        d_list = []
        data_list = wd.find_elements_by_css_selector('#content_area > div > div.table_area > table > tbody > tr:nth-child(2) > td > dl > dd')
        for data in data_list:
            data = data.text
            data = data.replace('\n\n', '\n')
            d_list = data.split('\n')
            del d_list[0]

        for idx, val in enumerate(d_list):
            if '▣' in val:
                d_list = d_list[0:idx]
        #print(d_list)

        for idx, val in enumerate(d_list):
            # 학력
            if "학사" in val or "박사" in val or "석사" in val or "졸업" in val:
                temp_edu.append(val)
            # 경력
            else:
                temp_career.append(val)
        print(temp_edu)
        print(temp_career)
        print('\n')

        education_list.append(temp_edu)
        career_list.append(temp_career)

        ###link수집###
        link.append(wd.current_url)
        #print(link[j])

        j = j + 1
        k = k + 1

    for i in range(len(name_kor)):

        if not education_list[i]:
            education = None
        else:
            education = ', '.join(education_list[i])

        if not career_list[i]:
            career = None
        else:
            career = ', '.join(career_list[i])

        cursor.execute("insert into "+ table_name+"(name_kor, belong,department, major,education,career,link,hospital_code) values( %s,%s,%s,%s,%s,%s,%s,%s);",(name_kor[i],belong, dpt[i], major[i],education, career,link[i],hospital_code))
    connect.commit()
    
    wd.close()
    wd.quit()
