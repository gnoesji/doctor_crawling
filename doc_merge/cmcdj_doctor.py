from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymysql


def doctor(conn, cursor, new_table, driver_path):

    main_url = 'https://www.cmcdj.or.kr/servlet/MainSvl?_tc=F001001001001&cd2=001&cd3=001&cd4=001&cd5=001&idx='
    depart_list = ['111', '156']
    driver = wd.Chrome(executable_path=driver_path)
    
    doctor_list = []
    major_list = []
    education_list = []
    career_list = []
    link_list = []
    hospital_code = "301710"

    for depart in depart_list:
        try:
            driver.implicitly_wait(10)
            driver.get(main_url + depart)

            click_page = 'body > div.container > div.row > div > div.col-xs-12 > ul > li'

            doc_list = driver.find_elements_by_css_selector(click_page)
            print(doc_list)
            doc_num = len(doc_list)

            for i in range(1, doc_num+1):
                try:
                    if i%3 == 0:
                        continue

                    driver.find_element_by_css_selector(
                        click_page + ':nth-child(%s) > article > section.doctor-content-down > div > div:nth-child(2) > a'%(i)
                    ).send_keys(Keys.ENTER)
                    driver.implicitly_wait(10)

                    #이름
                    temp_name = driver.find_element_by_css_selector(
                        'body > div.section-white> div > div > div > h2'
                    ).text.split(" ")
                    temp_name = temp_name[0]

                    #진료분야
                    temp_major = []

                    major = driver.find_element_by_css_selector(
                        'body > div.section-white > div > div > div > article > section > div.doctor-view-content-text > table > tbody > tr:nth-child(3) > td'
                    ).text
                    temp_major.append(major)

                    #학력/경력/학회활동
                    temp_edu = []
                    temp_career = []

                    data_list = driver.find_elements_by_css_selector(
                        'body > div.section-white > div > div > div > ul > li'
                    )
                    for data in data_list:
                        data = data.text
                        #학력
                        if "박사" in data or "석사" in data or "졸업" in data:
                            temp_edu.append(data)
                        #경력
                        else:
                            temp_career.append(data)

                    temp_link = driver.current_url

                    #데이터 저장
                    doctor_list.append(temp_name)
                    major_list.append(temp_major)
                    education_list.append(temp_edu)
                    career_list.append(temp_career)
                    link_list.append(temp_link)
                    
                    driver.back()
                    driver.implicitly_wait(10)

                except Exception as e1:
                    print("의료진 페이지 오류 : ", e1)

        except Exception as e1:
            print("전체 페이지 오류 : ", e1)
            
    #DB 저장
    for i in range(len(doctor_list)):   
        try:
            major = major_list[i][0]

            if not education_list[i]:
                education = None
            else:
                education = ', '.join(education_list[i])

            if not career_list[i]:
                career = None
            else:
                career = ', '.join(career_list[i])

            #의료진 DB 추가
            sql = """INSERT INTO """+new_table+"""(name_kor, belong, major, education, career, link, hospital_code)
            VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')
            """%(doctor_list[i], "가톨릭대학교대전성모병원", major, education, career, link_list[i], hospital_code)

            cursor.execute(sql)
            conn.commit()

        except Exception as e1:
            print("DB 저장 오류 : ", e1)
            conn.close()

            driver.close()
            driver.quit()
            import sys
            sys.exit()

    driver.close()
    driver.quit()
