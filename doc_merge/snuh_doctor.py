#서울대학교병원(본원)
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import pymysql
from selenium import webdriver as wd

def doctor(connect, cursor, table_name, driver_path):
    wd=webdriver.Chrome(executable_path=driver_path)

    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    departmentLink = []
    doctocdepartmentLink = []
    doctorLink = []

    seoulURL = 'https://www.snuh.org/m/reservation/meddept/main.do'

    wd.get(seoulURL)
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
        # 서울대학교 더보기 예외사항 처리
        if '서울대학교' in wd.title:
            button = wd.find_element_by_id('addDrBtn')
            temp1 = button.find_element_by_tag_name('page').text
            temp2 = button.find_element_by_tag_name('pages').text
            while (temp1 != temp2):
                button.click()
                button = wd.find_element_by_id('addDrBtn')
                temp1 = button.find_element_by_tag_name('page').text
                temp2 = button.find_element_by_tag_name('pages').text
        options = wd.find_elements_by_tag_name('a')
        for i in options:
            # print(i.get_attribute('href'))
            if ('자세히보기' in i.text or '의료진소개' in i.text):
                doctorLink.append(i.get_attribute('href').replace('/m', ''))
    docs = []
    for doctor in doctorLink:
        doc = []
        wd.get(doctor)
        time.sleep(1)
        link = wd.current_url
        html = urlopen(wd.current_url)
        soup = BeautifulSoup(html, "html.parser")

        div = soup.find('div', {'class', 'name'})
        # 이름
        name = div.find('strong').text
        doc.append(name)
        # 소속
        belong = '서울대학교병원'
        hospital_code = '110710'
        doc.append(belong)
        dpt = []
        major = []
        education = []
        career = []
        # 진료과
        dpt = wd.find_element_by_css_selector('#pub1 > div.blogLinkWrap > ul > li > a').text
        doc.append(dpt)
        # 진료분야
        try:
            for div in soup.find_all('div'):
                attrs = div.attrs
                if 'id' in attrs:
                    if div['id'] == 'pub1':
                        search = div
                        break
            for p in search.find_all('p'):
                if '진료분야' in p.text:
                    texts = p.text
            texts = texts.split(',')
            for i in range(len(texts)):
                text = texts[i]
                if i != len(texts) - 1:
                    text = text.split('\t')
                    text = text[len(text) - 1]
                else:
                    text = text.split('\r')[2]
                    text = text.split('\t')
                    text = text[len(text) - 1]
                if text == '':
                    continue
                major.append(text)
            major = ','.join(major)
        except:
            major = None
        if major == []:
            major = None
        doc.append(major)
        # 서울대 학력/경력 찾기
        try:
            wd.find_element_by_link_text('학력/경력').click()
            time.sleep(1)
            html = urlopen(wd.current_url)
            soup = BeautifulSoup(html, "html.parser")

            search = ''
            try:
                for div in soup.find_all('div', {'class', 'tableType01'}):
                    if '학력' in div.text:
                        search = div
                        break
                tbody = search.find('tbody')
                for tr in tbody.find_all('tr'):
                    year = tr.find('td').text
                    educ = tr.find('td', {'class', 'alignL'}).text
                    if year != educ:
                        educ = year + ' ' + educ
                    education.append(educ)
                education = ', '.join(education)
            except:
                education = None
            if education == []:
                education = None

            search = ''
            try:
                for div in soup.find_all('div', {'class', 'tableType01'}):
                    if '경력' in div.text:
                        search = div
                        break
                tbody = search.find('tbody')
                for tr in tbody.find_all('tr'):
                    year = tr.find('td').text
                    care = tr.find('td', {'class', 'alignL'}).text
                    if year != care:
                        care = year + ' ' + care
                    career.append(care)
                career = ', '.join(career)
            except:
                career = None
            if career == []:
                career = None
        except:
            education = None
            career = None
        doc.append(education)
        doc.append(career)
        doc.append(link)
        doc.append(hospital_code)
        docs.append(doc)
        """
        print(name)
        print(belong)
        print(dpt)
        print(major)
        print(education)
        print(career)
        print(link)
        """
    wd.close()

    for i in docs:
        cursor.execute(
            "INSERT INTO " + table_name + " (name_kor, belong, department, major, education, career, link, hospital_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
            (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
        connect.commit()
