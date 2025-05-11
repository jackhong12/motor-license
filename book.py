from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import private
from sendmail import MailHandler
from datetime import date
from datetime import datetime
from collections import defaultdict

_licenseTypeCode = "普通重型機車"
_expectExamDateStr = str(int(date.today().strftime("%Y")) - 1911) + date.today().strftime("%m%d")
_locations = {
    "板橋": ["臺北區監理所（北宜花）",        "板橋監理站(新北市中和區中山路三段116號)"],
    #"士林": ["臺北市區監理所（含金門馬祖）",  "士林監理站(臺北市士林區承德路5段80號)"],
    #"基隆": ["臺北市區監理所（含金門馬祖）",  "基隆監理站(基隆市七堵區實踐路296號)"],
    #"金門": ["臺北市區監理所（含金門馬祖）",  "金門監理站(金門縣金湖鎮黃海路六之一號)"],
    #"漣江": ["臺北市區監理所（含金門馬祖）",   "連江監理站(連江縣南竿鄉津沙村155號)"],
    #"樹林": ["臺北區監理所（北宜花）",        "臺北區監理所(新北市樹林區中正路248巷7號)"],
    #"蘆洲": ["臺北區監理所（北宜花）",        "蘆洲監理站(新北市蘆洲區中山二路163號)"],
    #"屏東": ["高雄區監理所（高屏澎東）",      "屏東監理站(屏東市忠孝路222號)"],
    #"恆春": ["高雄區監理所（高屏澎東）",      "恆春監理分站(屏東縣恒春鎮草埔路11號)"],
}

_signupInfos = {
    'id':    private.SIGNUP_ID,
    'birth': private.SIGNUP_BIRTH,
    'name':  private.SIGNUP_NAME,
    'phone': private.SIGNUP_PHONE,
    'email': private.SIGNUP_EMAIL,
}

# 設定 Selenium WebDriver（以 Chrome 為例）
options = webdriver.ChromeOptions()
#options.add_argument('--headless')  # 無頭模式
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10) # Wait for 10 second at most

isBooked = False

class ExamInfo:
    def __init__(self):
        self.date = "" 
        self.chineseDate = ""
        self.description = ""
        self.place = ""
        self.number = "額滿" 
        self.isBook = False
        self.examType = False
        self.cancelAction = ""
        self.cancelDriver = None
        self.bookingButton = None
        self.bookingDriver = None

    def addChineseDate (self, date):
        self.chineseDate = date
        self.date = self.chineseDateToInt(date)

    def chineseDateToInt (self, chineseDate):
        year = int(chineseDate.split("年")[0])
        month = int(chineseDate.split("年")[1].split("月")[0])
        day = int(chineseDate.split("月")[1].split("日")[0])
        stryear = str(year)
        if month < 10:
            strmonth = "0" + str(month)
        else:
            strmonth = str(month)
        if day < 10:
            strday = "0" + str(day)
        else:
            strday = str(day)
        return stryear + strmonth + strday

    def isAvaliable (self):
        if self.isFirstTime():
            return False
        if self.number == "0":
            return False
        if self.number == "額滿":
            return False
        return True

    def isFirstTime (self):
        if self.description.find("本場次為初考") >= 0:
            return True
        return False

def findExamRecord (driver):
    wait = WebDriverWait(driver, 10) # Wait for 10 second at most

    # Go to exam record page
    driver.get("https://www.mvdis.gov.tw/m3-emv-trn/exm/query#gsc.tab=0")
    idInput = wait.until(EC.presence_of_element_located((By.ID, "idNo")))
    idInput.send_keys(_signupInfos['id'])
    birthInput = wait.until(EC.presence_of_element_located((By.ID, "birthdayStr")))
    birthInput.send_keys(_signupInfos['birth'])

    # Click on the "查詢報名紀錄" link
    driver.execute_script("query();")

    record = ExamInfo() 
    try:
        recordTable = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tb_list_std.gap_b2.gap_t")))
        rows = recordTable.find_elements(By.TAG_NAME, "tr")
        assert len(rows) == 2
        cols = rows[1].find_elements(By.TAG_NAME, "td")
        assert len(cols) == 5

        record.isBook = True
        record.place = cols[0].text
        record.examType = cols[1].text
        record.addChineseDate(cols[2].text)
        record.description = cols[3].text
        cancelLinkTag = cols[4].find_element(By.TAG_NAME, "a")
        record.cancelAction = cancelLinkTag.get_attribute("onclick")
        record.cancelDriver = driver
    except:
        record.isBook = False

    return record

def signupExam (signupElement):
    global isBooked
    if isBooked:
        return False
    # Go to signup link
    signupLinkTag = signupElement.find_element(By.TAG_NAME, "a")
    signupLink = signupLinkTag.get_attribute("onclick")
    driver.execute_script(signupLink)
    # Get rid of block UI
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "blockUI.blockMsg.blockPage")))
    driver.execute_script("$.unblockUI();	return false;")

    # Register the test
    idInput = wait.until(EC.presence_of_element_located((By.ID, "idNo")))
    idInput.send_keys(_signupInfos['id'])
    birthInput = wait.until(EC.presence_of_element_located((By.ID, "birthdayStr")))
    birthInput.send_keys(_signupInfos['birth'])
    nameInput = wait.until(EC.presence_of_element_located((By.ID, "name")))
    nameInput.send_keys(_signupInfos['name'])
    phoneInput = wait.until(EC.presence_of_element_located((By.ID, "contactTel")))
    phoneInput.send_keys(_signupInfos['phone'])
    emailInput = wait.until(EC.presence_of_element_located((By.ID, "email")))
    emailInput.send_keys(_signupInfos['email'])
    driver.execute_script("add()")
    isBooked = True

    return True

def findAvailableDate (driver, location):
    # Open the website 
    driver.get("https://www.mvdis.gov.tw/m3-emv-trn/exm/locations")
    wait = WebDriverWait(driver, 10) # Wait for 10 second at most

    # Fill the form:
    #   報考照類 Type of Test：
    #   預計考試日期 Date of Test：
    #   考試地點 Place of Test：
    examTypeSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "licenseTypeCode"))))
    examTypeSelect.select_by_visible_text(_licenseTypeCode)

    examDateInput = wait.until(EC.presence_of_element_located((By.ID, "expectExamDateStr")))
    examDateInput.send_keys(_expectExamDateStr)

    regionSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "dmvNoLv1"))))
    regionSelect.select_by_visible_text(location[0])

    stationSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "dmvNo"))))
    stationSelect.select_by_visible_text(location[1])
    
    #import pdb; pdb.set_trace()
    # Submit the form and get avaliable dates.
    driver.execute_script("query()")

    # Click "選擇場次繼續報名"
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "msg_box_success")))
    driver.execute_script("$.unblockUI();")

    # Data
    titles = [] 

    tables = driver.find_elements(By.ID, "trnTable")
    assert len(tables) == 1
    table = tables[0]
    
    tableHeads = table.find_elements(By.TAG_NAME, "thead")
    assert len(tableHeads) == 1
    tableHead = tableHeads[0]
    tableTitles = tableHead.find_elements(By.TAG_NAME, "th")
    for tableTitle in tableTitles:
        titles += [tableTitle.text]

    tableBodies = table.find_elements(By.TAG_NAME, "tbody")
    assert len(tableBodies) == 1
    tableBody = tableBodies[0]

    rows = tableBody.find_elements(By.TAG_NAME, "tr")
    avaliableDates = []
    fullDates = []

    for row in rows:
        infos = []
        cols = row.find_elements(By.TAG_NAME, "td")
        for col in cols:
            infos += [col.text]
        assert len(infos) == len(titles) 
        infos[1] = infos[1].replace("\n", " ")

        examInfo = ExamInfo()
        examInfo.addChineseDate(infos[0])
        examInfo.description = infos[1]
        examInfo.place = location[1]
        examInfo.number = infos[2]
        examInfo.examType = "普通重型機車"
        examInfo.bookingDriver = driver
        examInfo.bookingButton = cols[3]

        if examInfo.isAvaliable():
            avaliableDates += [examInfo]
        else:
            fullDates += [examInfo]

    return (avaliableDates, fullDates)
    #if len(avaliableDates) > 0:
    #    if isBook:
    #        target = avaliableDates[0]
    #        if signupExam(target['link']):
    #            mail.textln(f"## 成功申請!!!!!")
    #            mail.textln(f"- 地點: {location[1]}")
    #            mail.textln(f"- 時間: {target['date']}")
    #            mail.textln(f"- 名額: {target['number']}")
    #            mail.textln(f"- 說明: {target['description']}")
    #            mail.textln(f"- 身分: {_signupInfos['id']}")
    #            mail.textln(f"- 名字: {_signupInfos['name']}")
    #            mail.textln(f"- 生日: {_signupInfos['birth']}")
    #            mail.textln(f"- 手機: {_signupInfos['phone']}")
    #            mail.textln(f"- 信箱: {_signupInfos['email']}")
    #            mail.textln("")

    #    mail.textln(f"#### {location[1]}")
    #if len(fullDates) > 0:
    #    mail.textln(f"#### {location[1]}", False)

    #for date in avaliableDates:
    #    mail.textln(f"##### {date['date']}")
    #    mail.textln(f"- 名額: {date['number']}")
    #    mail.textln(f"- 說明: {date['description']}")
    #    mail.textln("")

    #for date in fullDates:
    #    mail.textln(f"- {date['date']}", False)


def findAllSites (driver):
    #mail.textln("### 有名額時段:")
    #mail.textln("### 額滿時段:", False)
    
    avaliableExams = []
    unavaliableExams = []
    for loc, details in _locations.items():
        avaliable, unavaliable = findAvailableDate(driver, details)
        avaliableExams += avaliable
        unavaliableExams += unavaliable
        print(f"  - Parsing {details[1]} avaliable: {len(avaliable)}, full: {len(unavaliable)}")

    return (avaliableExams, unavaliableExams)

tmp="""
while True:
    print(f"\n-> {datetime.now()}")
    if tryAllSites():
        break
    time.sleep(10 * 60) # every 10 sec
"""

def logUnavailableExams (unavaliableExams):
    locationInfos = defaultdict(list) 
    for exam in unavaliableExams:
        desc = "初考" if exam.isFirstTime() else "重考"
        locationInfos[exam.place].append(f"{exam.chineseDate} {desc} {exam.number}")

    for location, dates in locationInfos.items():
        print(f"### {location}")
        for date in dates:
            print(f"  - {date}")

if __name__ == "__main__":
    recordWebsite = webdriver.Chrome(options=options)
    bookWebsite = webdriver.Chrome(options=options)
    mail = MailHandler()

    oldRecord = findExamRecord(recordWebsite)
    avaliableExams, unavaliableExams = findAllSites(bookWebsite)

    logUnavailableExams(unavaliableExams)

    bookWebsite.quit()
    recordWebsite.quit()

driver.quit()
