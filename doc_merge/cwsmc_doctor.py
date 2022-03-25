#삼성창원병원
#순환기내과 : http://smc.skku.edu/smc_main/care/treatDoctor.smc?meddept=IC
#흉부외과 : http://smc.skku.edu/smc_main/care/treatDoctor.smc?meddept=TS

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymysql

def doctor(conn, cursor, new_table, driver_path):

    driver = wd.Chrome(executable_path=driver_path)

    department = ["순환기내과", "심장내과", "심장외과", "흉부외과", "심장혈관외과", "소아심장과"]
    cwsmc_url = "https://smc.skku.edu/smc/medical/intro.do?mId=100"
    driver.get(cwsmc_url)
    # 진료과 링크 담기
    departmentLink = []
    doctor_list = []
    major_list = []
    education_list = []
    career_list = []
    link_list = []
    hospital_code = "630520"

    names = driver.find_elements_by_class_name('group')
    size = len(names)
    for m in range(0, size):
        name = names[m].find_element_by_tag_name('strong').text
        if name in department:
            #options = names[m].find_elements_by_tag_name('a')
            #departmentLink.append(options[1].get_attribute('href'))

            try:
                driver.execute_script('fn_goLink(1)')
                driver.implicitly_wait(5)
                doc_list = driver.find_elements_by_css_selector(
                    '#contents > form > div > div > ul > li'
                )
                doc_len = len(doc_list)
                #contents > form > div > div > ul > li:nth-child(1) > div.txt_box > a

                for i in range(1, doc_len+1):
                    try:
                        time.sleep(2)
                        driver.find_element_by_css_selector(
                            '#contents > form > div > div > ul > li:nth-child(%s) > div.txt_box > a'%(i)
                        ).send_keys(Keys.ENTER)

                        #이름
                        temp_list = driver.find_element_by_css_selector(
                                '#contents > form > div > div > div.basic > div.txt_box02 > dl.first > dd:nth-child(2)'
                        ).text.split(' ')
                        temp_name = temp_list[0]

                        #진료분야
                        temp_major = []
                        temp_major.append(driver.find_element_by_css_selector(
                            '#contents > form > div > div > div.basic > div.txt_box02 > dl:nth-child(2) > dd'
                        ).text)

                        #학력, 경력
                        data_list = driver.find_element_by_xpath(
                            '//*[@id="contents"]/form/div/div/div[2]/div[2]/dl[3]/dd'
                        ).text.split("\n")

                        temp_edu = []
                        temp_career = []

                        edu = False
                        career = False
                        academic = False

                        for data in data_list:
                            if data == "▶ 학력":
                                edu = True
                                career = False
                                academic = False
                                continue
                            elif data == "▶ 경력":
                                edu = False
                                career = True
                                academic = False
                                continue
                            elif data == "▶ 학회 및 기타활동":
                                edu = False
                                career = False
                                academic = True
                                continue
                            elif "현)" in data:
                                edu = False
                                career = True
                                academic = False
                            elif data == "":
                                continue

                            data = data.replace("-", "")
                            data = data.strip(" ")

                            if edu:
                                temp_edu.append(data)
                            elif career:
                                temp_career.append(data)

                        #의료진 페이지
                        temp_link = driver.current_url

                        driver.back()

                        #데이터 저장
                        doctor_list.append(temp_name)
                        major_list.append(temp_major)
                        education_list.append(temp_edu)
                        career_list.append(temp_career)
                        link_list.append(temp_link)


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

            if not career_list:
                career = None
            else:
                career = ', '.join(career_list[i])

            #의료진 DB 추가
            sql = """INSERT INTO """+new_table+"""(name_kor, belong, major, education, career, link, hospital_code)
            VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')
            """%(doctor_list[i], "삼성창원병원", major, education, career, link_list[i], hospital_code)

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





