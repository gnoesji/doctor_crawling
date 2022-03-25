#고려대학교 안암/구로/안산
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import pymysql


def doctor(connect, cursor, table_name, driver_path):
    ### 크롬드라이버 생성 ###
    wd = webdriver.Chrome(executable_path=driver_path)

    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과', '심혈관센터(순환기)']

    koreaanamURL = 'http://anam.kumc.or.kr/department/treatDept.do'  # 안암
    koreaguroURL = 'http://guro.kumc.or.kr/department/treatDept.do'  # 구로
    koreaansanURL = 'http://ansan.kumc.or.kr/department/treatDept.do'  # 안산
    koreaUrl = [koreaanamURL, koreaguroURL, koreaansanURL]
    docs = []
    for u in koreaUrl:
        departmentLink = []
        doctorLink = []
        wd.get(u)
        time.sleep(2)

        html = wd.page_source
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all('a'):
            img = a.find('img')
            try:
                if img['alt'] in department:
                    if '안암' in wd.title:
                        departmentLink.append('http://anam.kumc.or.kr' + a['href'])

                    elif '구로' in wd.title:
                        departmentLink.append('http://guro.kumc.or.kr' + a['href'])

                    elif '안산' in wd.title:
                        departmentLink.append('http://ansan.kumc.or.kr' + a['href'])

            except:
                continue

        for i in departmentLink:
            wd.get(i)
            html = urlopen(wd.current_url)
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all('a', {'class', 'btn_detail'}):
                if '안암' in wd.title:
                    doctorLink.append('http://anam.kumc.or.kr' + a['href'])
                elif '구로' in wd.title:
                    doctorLink.append('http://guro.kumc.or.kr' + a['href'])
                elif '안산' in wd.title:
                    doctorLink.append('http://ansan.kumc.or.kr' + a['href'])

        for i in doctorLink:
            doc = []
            wd.get(i)
            time.sleep(2)
            link = wd.current_url
            html = urlopen(wd.current_url)
            soup = BeautifulSoup(html, "html.parser")
            education = []
            career = []
            major = None
            p = soup.find('p', {'class', 'docName'})
            # 이름
            name = p.text
            doc.append(name)
            # 소속
            if '안암' in wd.title:
                belong = '고려대학교안암병원'
                hospital_code = '136010'
            elif '구로' in wd.title:
                belong = '고려대학교구로병원'
                hospital_code = '152710'
            elif '안산' in wd.title:
                belong = '고려대학교안산병원'
                hospital_code = '425010'
            doc.append(belong)
            # 진료과
            try:
                dpt = wd.find_element_by_css_selector(
                    'body > div.docPOP > div > div.doctop > div.doctop_text > div > div.doc_info > ul > li:nth-child(1) > p:nth-child(2)'
                ).text.strip()
            except:
                dpt = None
            doc.append(dpt)
            # 진료분야
            try:
                elm = wd.find_element_by_css_selector(
                    'body > div.docPOP > div > div.doctop > div.doctop_text > div > div.doc_info > ul > li:nth-child(2) > p:nth-child(2)')
                major = elm.text
            except:
                major = None
            doc.append(major)
            # 학력
            uls = soup.find_all('ul', {'class', 'cl list_type_01 mb20'})
            try:
                ul = uls[0]
                for li in ul.find_all('li'):
                    text = li.text
                    texts = text.split('\t')
                    text = texts[len(texts) - 1]
                    education.append(text)
                education = (', ').join(education)
            except:
                education = None
            doc.append(education)
            # 경력
            try:
                ul = uls[1]
                for li in ul.find_all('li'):
                    text = li.text
                    texts = text.split('\t')
                    text = texts[len(texts) - 1]
                    career.append(text)
                career = (', ').join(career)
            except:
                career = None
            doc.append(career)
            doc.append(link)
            doc.append(hospital_code)
            docs.append(doc)

            print(name)
            print(belong)
            print(dpt)
            print(major)
            print(education)
            print(career)
            print(link)
            print(hospital_code)

    wd.close()

    for i in docs:
        cursor.execute(
            "INSERT INTO " + table_name + " (name_kor, belong, department, major, education, career, link, hospital_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
            (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
        connect.commit()
