#인제대학교병원
#서울 : http://www.paik.ac.kr/seoul/treatment/search.asp
#부산 : http://www.paik.ac.kr/busan/treatment/search.asp
#상계 : http://www.paik.ac.kr/sanggye/treatment/search.asp
#일산 : http://www.paik.ac.kr/ilsan/treatment/search.asp
#해운대 : http://www.paik.ac.kr/haeundae/treatment/search.asp

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymysql

def doctor (conn, cursor, new_table, driver_path):

    main_url_front = 'http://www.paik.ac.kr/'
    main_url_back = '/treatment/search.asp'
    page_list = ['seoul', 'sanggye', 'ilsan', 'busan', 'haeundae']
    depart_list = [['?cid=1015#doctorList'],
                   ['?cid=332&tabIndex=1#doctorList'],
                   ['?cid=727&tabIndex=1#doctorList'],
                   ['?tabIndex=0&cid=858#doctorList', '?tabIndex=0&cid=49#doctorList'],
                   ['?cid=925&tabIndex=1#doctorList', '?cid=787#doctorList']]
    driver = wd.Chrome(executable_path=driver_path)
    
    doctor_list = []
    major_list = []
    dpt_list = []
    education_list = []
    career_list = []
    link_list = []
    belong_list = []
    code_list = []

    for idx, city in enumerate(page_list):
        for depart in depart_list[idx]:
            try:
                driver.get(main_url_front + city + main_url_back + depart)
                time.sleep(2)

                doc_list = driver.find_elements_by_css_selector(
                    '#doctorList > div > ul > li'
                )            
                doc_len = len(doc_list)

                for i in range(1, doc_len+1):
                    try:
                        # 의료진 페이지 이동
                        driver.find_element_by_css_selector(
                            '#doctorList > div > ul > li:nth-child(%s) > div > div > div > a:nth-child(2)'%(i)
                        ).send_keys(Keys.ENTER)
                        time.sleep(2)

                        # 이름 => 교수 제거
                        temp_list = driver.find_element_by_css_selector(
                            '#uiTabPopup01 > div > div.tit-area > h3 > strong'
                        ).text.split(' ')
                        temp_name = temp_list[0]
                        # 진료과
                        temp_dpt = []
                        temp_dpt.append(driver.find_element_by_css_selector(
                            '#uiTabPopup01 > div > div.tit-area > h3 > em'
                        ).text)
                        # 진료분야
                        temp_major = []
                        temp_major.append(driver.find_element_by_css_selector(
                            '#uiTabPopup01 > div > div.cont.clearfix > div.info.fr > dl:nth-child(1) > dd'
                        ).text)

                        # 학력 & 경력
                        temp_career = []
                        temp_edu = []
                        data_list = driver.find_elements_by_css_selector(
                            '#uiTabContent01 > ul:nth-child(2) > li'
                        )
                        for data in data_list:
                            data = data.text
                            if '　　　　　' in data:
                                data = data.replace('　　　　　', ' ')
                            if '\u3000' in data:
                                data = data.replace('\u3000', '')
                            if "학력" in data or "경력" in data or data == "" or len(data) < 5:
                                continue

                            if "졸업" in data or "석사" in data or "박사" in data or "학사" in data:
                                temp_edu.append(data.replace("'", "’"))
                            else:
                                temp_career.append(data.replace("'", "’"))

                        # 링크
                        temp_link = driver.current_url

                        if idx == 0:
                            temp_belong = '인제대학교서울백병원'
                            hospital_code = '100020'
                        elif idx == 1:
                            temp_belong = '인제대학교상계백병원'
                            hospital_code = '139710'
                        elif idx == 2:
                            temp_belong = '인제대학교일산백병원'
                            hospital_code = '411410'
                        elif idx == 3:
                            temp_belong = '인제대학교부산백병원'
                            hospital_code = '614710'
                        else:
                            temp_belong = '인제대학교해운대백병원'
                            hospital_code = '612021'

                        # 의료진 페이지 나가기
                        driver.find_element_by_css_selector(
                            '#doctorIntroduce > button').click()
                        
                        # 데이터 저장
                        doctor_list.append(temp_name)
                        belong_list.append(temp_belong)
                        dpt_list.append(temp_dpt)
                        code_list.append(hospital_code)
                        major_list.append(temp_major)
                        education_list.append(temp_edu)
                        career_list.append(temp_career)
                        link_list.append(temp_link)

                    except Exception as e1:
                        print('의료진 페이지 오류', e1)

            except Exception as e1:
                print('전체 페이지 오류', e1)
                
    # DB 저장
    for i in range(len(doctor_list)):
        try:
            if major_list[i][0] == '':
                major = None
            else:
                major = major_list[i][0]

            if dpt_list[i][0] == '':
                dpt = None
            else:
                dpt = dpt_list[i][0]

            career = ', '.join(career_list[i])
            education = ', '.join(education_list[i])

            if career == '':
                career = None
            if education == '':
                education = None

            print(doctor_list[i])
            print(belong_list[i])
            print(dpt)
            print(major)
            print(education)
            print(career)
            print(link_list[i])
            print(code_list[i])

            # 의료진 DB 추가
            cursor.execute("INSERT INTO " + new_table + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                    (doctor_list[i], belong_list[i], dpt, major, education, career, link_list[i], code_list[i]))
            conn.commit()

        except Exception as e1:
            #DB종류
            print("DB저장 오류 : ", e1)
            conn.close()

            driver.close()
            driver.quit()
            import sys
            sys.exit()            

    driver.close()
    driver.quit()




