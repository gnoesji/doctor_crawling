from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import pymysql

def doctor(connect, cursor, table_name, driver_path):

    ### 크롬드라이버 생성 ###
    wd = webdriver.Chrome(executable_path=driver_path)

    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    departmentLink = []
    doctordepartmentLink = []
    doctorLink = []

    ajouURL='http://hosp.ajoumc.or.kr/Center/PartIndex.aspx'
    wd.get(ajouURL)
    time.sleep(2)


    for i in department:
        data = wd.find_elements_by_partial_link_text(i)
        for a in data:
            departmentLink.append(a.get_attribute("href"))

    for i in departmentLink:
        wd.get(i)
        time.sleep(1)
        try:
            doctordepartmentLink.append(wd.find_element_by_link_text("의료진 소개").get_attribute('href'))
        except:
            doctordepartmentLink.append(wd.find_element_by_link_text("의료진").get_attribute('href'))


    for i in doctordepartmentLink:
        wd.get(i)
        time.sleep(2)
        datas = wd.find_elements_by_partial_link_text('자세히 보기')
        for data in datas:
            doctorLink.append(data.get_attribute('href'))


    docs=[]
    for i in doctorLink:
        doc=[]
        career = []
        education = []
        major=''
        wd.get(i)
        time.sleep(2)
        link=wd.current_url
        html=wd.page_source
        soup=BeautifulSoup(html,'html.parser')
        ul = soup.find('ul',{'class','Section'})
        # 이름
        for li in ul.find_all('li'):
            img=li.find('img')
            if '진료과' in img['alt']:
                text=li.get_text()
                text=text.split(' ')[16]
                dpt = text[0:len(text)-1]
            else:
                text=li.get_text()
                text=text.split(' ')[16]
                name=text[0:len(text)-1]
        doc.append(name)
        # 소속
        belong='아주대학교병원'
        doc.append(belong)
        doc.append(dpt)


        # 진료분야
        p=soup.find('p',{'class','Txt'})
        text=p.text
        for txt in text.split(' '):
            if txt!='' and txt !='\n':
                if '\n' in txt:
                    split=txt.split('\n')
                    for tx in split:
                        if tx!='':
                            txt=tx
                major=major+txt
        doc.append(major)
        # 학력
        try:
            ul = soup.find('ul',{'class','BulUl'})
            for li in ul.find_all('li'):
                education.append(li.text)
            education=(',').join(education)
        except:
            education=None
        doc.append(education)
        # 경력
        try:
            elm=wd.find_element_by_css_selector('#DoctorNav > ul > li:nth-child(2) > a')
            elm.click()
            time.sleep(2)
            html=wd.page_source
            soup=BeautifulSoup(html,'html.parser')
            div=soup.find('div',{'class','Career'})
            uls=div.find_all('ul')
            ul=uls[1]
            for li in ul.find_all('li'):
                career.append(li.text)
            career=(',').join(career)
        except:
            career=None
        if career=='':
            career=None
        doc.append(career)
        doc.append(link)
        hospital_code = '442710'
        doc.append(hospital_code)
        docs.append(doc)
        print(name)
        print(belong)
        print(dpt)
        print(major)
        print(education)
        print(career)
        print(link)
    wd.close()

    for i in docs:
        cursor.execute("INSERT INTO "+table_name+" (name_kor, belong, department, major, education, career, link, hospital_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",(i[0],i[1],i[2],i[3],i[4],i[5],i[6],[7]))
        connect.commit()

