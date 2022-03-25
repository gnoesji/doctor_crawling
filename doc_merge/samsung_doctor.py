from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import pymysql

def doctor(conn, cur, tablename, driver_path):
    wd = webdriver.Chrome(executable_path=driver_path)

    department = ['순환기내과','심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    departmentLink = []
    doctocdepartmentLink = []
    doctorLink = []

    samsungseoulURL = 'http://samsunghospital.com/home/reservation/deptSearch.do?DP_TYPE=O'

    wd.get(samsungseoulURL)
    time.sleep(2)

    for i in department:
        data = wd.find_elements_by_partial_link_text(i)
        for a in data:
            departmentLink.append(a.get_attribute("href"))

    for i in departmentLink:
        wd.get(i)
        try:
            doctocdepartmentLink.append(wd.find_element_by_link_text("의료진 소개").get_attribute('href'))
        except:
            doctocdepartmentLink.append(wd.find_element_by_link_text("의료진").get_attribute('href'))

    for i in doctocdepartmentLink:
        wd.get(i)
        options = wd.find_elements_by_tag_name('button')
        for i in options:
            if (i.text == '상세소개'):
                i.send_keys(Keys.ENTER)
                time.sleep(1)
                wd.switch_to.window(wd.window_handles[1])
                doctorLink.append(wd.current_url)
                wd.close()
                wd.switch_to.window(wd.window_handles[0])

    docs=[]
    for i in doctorLink:
        doc=[]
        wd.get(i)
        time.sleep(1)
        link=wd.current_url
        major=''
        html = wd.page_source
        soup = BeautifulSoup(html, "html.parser")
        datas = wd.find_elements_by_tag_name('table')
        # 이름
        name = wd.find_element_by_name('fullName').text
        doc.append(name)
        # 소속병원
        belong = '삼성서울병원'
        # 병원코드
        hospital_code = '135230'
        doc.append(belong)
        # 진료과
        try:
            dpt = wd.find_element_by_css_selector('#doctor-paper-section01 > div > div > h2 > span.info-field').text
        except:
            dpt = None
        if dpt=='':
            dpt = None
        doc.append(dpt)
        # 진료분야
        try:
            major = wd.find_element_by_class_name('doctor-paper-field').find_element_by_tag_name('dd').text
        except:
            major = None
        if major=='':
            major = None
        doc.append(major)
        # 학력
        try:
            education = datas[2].find_elements_by_tag_name('td')
            for i in range(0, len(education)):
                education[i] = education[i].text
            education = ",".join(education)
        except:
            education=None
        if education==',,,,,,,,,,,,':
            education=None
        doc.append(education)
        # 경력
        try:
            career = datas[3].find_elements_by_tag_name('td')
            for i in range(0, len(career)):
                career[i] = career[i].text
            career = ",".join(career)
        except:
            career=None
        doc.append(career)
        doc.append(link)
        doc.append(hospital_code)
        docs.append(doc)
        
    wd.close()
    wd.quit()

    for i in docs:
        cur.execute("INSERT INTO "+tablename+" (name_kor, belong, department, major, education, career, link, hospital_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7]))
        conn.commit()
