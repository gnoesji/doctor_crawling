#분당서울대학교병원

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymysql


def doctor(conn, cursor, new_table, driver_path):

    main_url= 'https://www.snubh.org/medical/drMedicalTeam.do?DP_TP='
    depart_list = ['H&DP_CD=CVC#', 'O&DP_CD=IMC', 'O&DP_CD=TS']
    driver = wd.Chrome(executable_path=driver_path)

    doctor_list = []
    dpt_list = []
    major_list = []
    education_list = []
    career_list = []
    link_list = []
    hospital_code = "463812"

    #의료진 페이지
    def doctor_page():
        driver.implicitly_wait(10)

        try:
            #이름
            temp_name = driver.find_element_by_class_name('doc_name').text
            #중복 의료진 검사
            if temp_name in doctor_list:
                #print("중복 : ", temp_name)
                driver.back()
                return
            #진료과
            temp_dpt = []
            temp_dpt.append(driver.find_element_by_css_selector(
                '#bh_container > div > div.contents_form > div.doc_profile_wrap > div > div.doc_info_wrap > dl:nth-child(4) > dt'
            ).text)
            #진료분야
            temp_major = []
            temp_major.append(driver.find_element_by_css_selector(
                '#bh_container > div > div.contents_form > div.doc_profile_wrap > div > div.doc_info_wrap > dl:nth-child(4) > dd'
            ).text.replace(" /", ",", 10))

            #학력/경력/활동 탭
            driver.find_element_by_css_selector('#tab_3 > a').send_keys(Keys.ENTER)
            time.sleep(2)

            #cont_num = driver.find_elements_by_css_selector('#cont_wrap3 > div')
            #cont_len = len(cont_num)

            #학력
            temp_edu = []
            edu_list = driver.find_elements_by_css_selector(
                '#cont_wrap3 > div:nth-child(2) > ul >li')

            for edu in edu_list:
                temp_edu.append(edu.text)

            #경력
            temp_career = []
            data_list = driver.find_elements_by_css_selector(
                '#cont_wrap3 > div:nth-child(3) > ul > li')

            for career in data_list:
                temp_career.append(career.text)

            #의료진 페이지 링크
            temp_link = driver.current_url

            #DB 저장
            doctor_list.append(temp_name)
            dpt_list.append(temp_dpt)
            major_list.append(temp_major)
            education_list.append(temp_edu)
            career_list.append(temp_career)
            link_list.append(temp_link)

        except Exception as e1:
            print("의료진 페이지 오류 : ", e1)

        driver.back()

    for idx, depart in enumerate(depart_list):
        try:
            driver.get(main_url + depart)
            time.sleep(2)

            #심장혈관센터
            if idx == 0:
                doc_list = driver.find_elements_by_css_selector(
                    '#bh_container > div > div.contents_form > div > div.bh_bookmark_list_wrap'
                )
                doc_len = len(doc_list)

                for i in range(doc_len+1):
                    #센터장
                    if i == 0:
                        driver.find_element_by_css_selector(
                            '#bh_container > div > div.contents_form > div > div.bh_bookmark_list_wrap_center > ul > li > div > div.bh_doctor_introduce3 > div.bh_doctor_btn_wrap_n.fix > input'
                        ).send_keys(Keys.ENTER)

                        doctor_page()

                    #그외 진료과
                    else:
                        click_page = '#bh_container > div > div.contents_form > div > div:nth-child(%s) > ul > li'%(i+3)
                        doc_num = driver.find_elements_by_css_selector(click_page)

                        for j in range(1, len(doc_num)+1):
                            driver.find_element_by_css_selector(
                                click_page + ':nth-child(%s) > div > div.bh_doctor_introduce3 > div.bh_doctor_btn_wrap_n.fix > input'%(j)
                            ).send_keys(Keys.ENTER)

                            doctor_page()

            #순환기내과, 흉부외과
            else:

                click_page = '#bh_container > div > div.contents_form > div > div.bh_bookmark_list_wrap > ul > li'
                doc_num = driver.find_elements_by_css_selector(click_page)

                for i in range(1, len(doc_num)+1):
                    driver.find_element_by_css_selector(
                        click_page + ':nth-child(%s) > div > div.bh_doctor_introduce3 > div.bh_doctor_btn_wrap_n.fix > input'%(i)
                    ).send_keys(Keys.ENTER)

                    doctor_page()

        except Exception as e1:
            print("전체 페이지 오류 : ", e1)


    for i in range(len(doctor_list)):
        try:
            if dpt_list[i][0] == '':
                dpt = None
            else:
                dpt = dpt_list[i][0]
            if major_list[i][0] == '':
                major = None
            else:
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
            sql = """INSERT INTO """+new_table+"""(name_kor, belong, department, major, education, career, link, hospital_code)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (doctor_list[i], "분당서울대학교병원", dpt, major, education, career, link_list[i], hospital_code))
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

