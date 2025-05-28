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
from logsystem import info, debug
import traceback
import sys

_licenseTypeCode = "普通重型機車"
_expectExamDateStr = str(int(date.today().strftime("%Y")) - 1911) + date.today().strftime("%m%d")

class Station:
    def __init__ (self, name, region, place):
        self.region = region
        self.place = place 
        self.name = name
        self.chromeTab = None

    def setChromeTab (self, chrome):
        self.chromeTab = ChromeTab(chrome) 

stations = []
if private.SIGNUP_PREFER_SITE == None:
    stations += [Station("漣江", "臺北市區監理所（含金門馬祖）", "連江監理站(連江縣南竿鄉津沙村155號)")]
else:
    for site in private.SIGNUP_PREFER_SITE.split(";"):
        if site == "漣江":
            stations += [Station("漣江", "臺北市區監理所（含金門馬祖）", "連江監理站(連江縣南竿鄉津沙村155號)")]
        elif site == "板橋":
            stations += [Station("板橋", "臺北區監理所（北宜花）", "板橋監理站(新北市中和區中山路三段116號)")]
        elif site == "士林":
            stations += [Station("士林", "臺北市區監理所（含金門馬祖）", "士林監理站(臺北市士林區承德路5段80號)")]
        elif site == "基隆":
            stations += [Station("基隆", "臺北市區監理所（含金門馬祖）", "基隆監理站(基隆市七堵區實踐路296號)")]
        elif site == "金門":
            stations += [Station("金門", "臺北市區監理所（含金門馬祖）", "金門監理站(金門縣金湖鎮黃海路六之一號)")]
        elif site == "樹林":
            stations += [Station("樹林", "臺北區監理所（北宜花）", "臺北區監理所(新北市樹林區中正路248巷7號)")]
        elif site == "蘆洲":
            stations += [Station("蘆洲", "臺北區監理所（北宜花）", "蘆洲監理站(新北市蘆洲區中山二路163號)")]
        elif site == "屏東":
            stations += [Station("屏東", "高雄區監理所（高屏澎東）", "屏東監理站(屏東市忠孝路222號)")]
        elif site == "恆春":
            stations += [Station("恆春", "高雄區監理所（高屏澎東）", "恆春監理分站(屏東縣恒春鎮草埔11號)")]


#stations += [Station("板橋", "臺北區監理所（北宜花）", "板橋監理站(新北市中和區中山路三段116號)")]
#stations += [Station("士林", "臺北市區監理所（含金門馬祖）", "士林監理站(臺北市士林區承德路5段80號)")]
#stations += [Station("基隆", "臺北市區監理所（含金門馬祖）", "基隆監理站(基隆市七堵區實踐路296號)")]
#stations += [Station("金門", "臺北市區監理所（含金門馬祖）", "金門監理站(金門縣金湖鎮黃海路六之一號)")]
#stations += [Station("漣江", "臺北市區監理所（含金門馬祖）", "連江監理站(連江縣南竿鄉津沙村155號)")]
#stations += [Station("樹林", "臺北區監理所（北宜花）", "臺北區監理所(新北市樹林區中正路248巷7號)")]
#stations += [Station("蘆洲", "臺北區監理所（北宜花）", "蘆洲監理站(新北市蘆洲區中山二路163號)")]
#stations += [Station("屏東", "高雄區監理所（高屏澎東）", "屏東監理站(屏東市忠孝路222號)")]
#stations += [Station("恆春", "高雄區監理所（高屏澎東）", "恆春監理分站(屏東縣恒春鎮草埔路11號)")]

_signupInfos = {
    'id':    private.SIGNUP_ID,
    'birth': private.SIGNUP_BIRTH,
    'name':  private.SIGNUP_NAME,
    'phone': private.SIGNUP_PHONE,
    'email': private.SIGNUP_EMAIL,
    'isFirst': private.SIGNUP_IS_FIRST,
    'preferDate': private.SIGNUP_PREFER_DATE,
}
datePrefer = {}
if _signupInfos['preferDate'] != None:
    preferCount = len(_signupInfos['preferDate'].split(";"))
    for date in _signupInfos['preferDate'].split(";"):
        datePrefer[int(date)] = preferCount
        preferCount -= 1

class ChromeTab:
    def __init__ (self, driver, waitSeconds=10):
        self.driver = driver
        self.waitSeconds = 10
        self.driver.execute_script("window.open('https://google.com', '_blank');")
        self.current_tab = self.driver.window_handles[-1]

    def moveToCurrentTab (self):
        self.driver.switch_to.window(self.current_tab)
        wait = WebDriverWait(self.driver, self.waitSeconds)
        return (self.driver, wait)

    def resetWeb (self):
        self.moveToCurrentTab()
        self.driver.get("https://google.com")

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
        self.cancelTab = None
        self.bookingButton = None
        self.bookingTab = None

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
            if not _signupInfos['isFirst']:
                return False
        else:
            if _signupInfos['isFirst']:
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

def findExamRecord (chromeTab):
    driver, wait = chromeTab.moveToCurrentTab()

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
        recordTable = wait.until(lambda d:
            d.find_element(By.ID, "headerMessage").text != "" or
            EC.presence_of_element_located((By.CLASS_NAME, "tb_list_std.gap_b2.gap_t"))
        )
        showmsg = driver.find_element(By.ID, "headerMessage").text 
        if showmsg != "":
            if showmsg.find("已查無報名資料，可「新增報名」") == -1:
                info(f"findExamRecord() error: {showmsg}")
            else:
                debug("無報名資料")
            record.isBook = False

        else:
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
            record.cancelTab = chromeTab 
    except:
        record.isBook = False

    return record

def cancelExam (examInfo):
    driver, wait = examInfo.cancelTab.moveToCurrentTab()
    driver.execute_script(examInfo.cancelAction)

    # Wait until the alert is shown
    wait.until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()
    
    # Click OK again
    wait.until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()

def signupExam (examInfo):
    driver, wait = examInfo.bookingTab.moveToCurrentTab()

    # Go to signup link
    signupLinkTag = examInfo.bookingButton.find_element(By.TAG_NAME, "a")
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

    wait.until(lambda d:
        EC.alert_is_present()(d) or
        d.find_element(By.ID, "headerMessage").text != ""
    )

    isSuccess = False
    try:
        showmsg = driver.find_element(By.ID, "headerMessage").text 
        if showmsg != "":
            info(f"Booking error (Blocking by issues): {showmsg}")
            mail = MailHandler()
            if showmsg.find("查無有效機車危險感知體驗紀錄") >= 0:
                mail.textln(f"查無有效機車危險感知體驗紀錄，請至「機車危險感知教育平台」完成體驗始得報名!!!!!")
                mail.textln(f"- Link: https://hpt.thb.gov.tw/reserve/index")
            else:
                mail.textln(f"Booking error (Blocking by issues): {showmsg}")
            mail.send_dev()
            sys.exit(1)
    except:
        isSuccess = True

def findAvailableDate (station):
    chromeTab = station.chromeTab
    driver, wait = chromeTab.moveToCurrentTab()

    # Open the website 
    driver.get("https://www.mvdis.gov.tw/m3-emv-trn/exm/locations")

    # Fill the form:
    #   報考照類 Type of Test：
    #   預計考試日期 Date of Test：
    #   考試地點 Place of Test：
    examTypeSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "licenseTypeCode"))))
    examTypeSelect.select_by_visible_text(_licenseTypeCode)

    examDateInput = wait.until(EC.presence_of_element_located((By.ID, "expectExamDateStr")))
    examDateInput.send_keys(_expectExamDateStr)

    regionSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "dmvNoLv1"))))
    regionSelect.select_by_visible_text(station.region)

    stationSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "dmvNo"))))
    stationSelect.select_by_visible_text(station.place)
    
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
        examInfo.place = station.place 
        examInfo.number = infos[2]
        examInfo.examType = "普通重型機車"
        examInfo.bookingTab = chromeTab 
        examInfo.bookingButton = cols[3]

        if examInfo.isAvaliable():
            avaliableDates += [examInfo]
        else:
            fullDates += [examInfo]

    return (avaliableDates, fullDates)

def findAllSites (stations):
    avaliableExams = []
    unavaliableExams = []
    for station in stations:
        avaliable, unavaliable = findAvailableDate(station)
        avaliableExams += avaliable
        unavaliableExams += unavaliable
        debug(f"Parsing {station.place} avaliable: {len(avaliable)}, full: {len(unavaliable)}")

    return (avaliableExams, unavaliableExams)

def logUnavailableExams (unavaliableExams):
    locationInfos = defaultdict(list) 
    for exam in unavaliableExams:
        desc = "初考" if exam.isFirstTime() else "重考"
        locationInfos[exam.place].append(f"{exam.chineseDate} {desc} {exam.number}")

    text = f"Detail Information:\n"
    indent = "\t" * 5
    for location, dates in locationInfos.items():
        text += f"{indent}- {location}\n"
        for date in dates:
            text += f"{indent}\t- {date}\n"
    debug(text)

def isExamEarlier (exam1, exam2):
    if int(exam1.date) < int(exam2.date):
        return True
    return False

def isBetterExam (current, previous):
    currentWeight = 0
    previousWeight = 0
    currentDate = int(current.date[3:7])
    previousDate = int(previous.date[3:7])
    if currentDate in datePrefer:
        currentWeight = datePrefer[currentDate]
    if previousDate in datePrefer:
        previousWeight = datePrefer[previousDate]
    if currentWeight > previousWeight:
        return current
    return previous

def chooseExam (avaliableExams):
    chosen = avaliableExams[0]
    for exam in avaliableExams:
        if isBetterExam(exam, chosen):
            chosen = exam
    return chosen

def bookExam(oldRecord, avaliableExams):
    if len(avaliableExams) == 0:
        return None

    # Book the first available exam
    exam = chooseExam(avaliableExams) 
    if oldRecord.isBook:
        if isBetterExam(exam, oldRecord):
            # Cancel the booked exam
            info(f"Canceling the old exam {oldRecord.place} {oldRecord.chineseDate}")
            cancelExam(oldRecord)
        else:
            return None

    # Book the new exam
    info(f"Booking the exam {exam.place} {exam.chineseDate}")
    signupExam(exam)
    return exam

def printInfo ():
    mail = MailHandler()
    mail.textln(f"## Started Server!!!!!")
    mail.textln(f"ID: {_signupInfos['id']}")
    mail.textln(f"Birth: {_signupInfos['birth']}")
    mail.textln(f"Name: {_signupInfos['name']}")
    mail.textln(f"Phone: {_signupInfos['phone']}")
    mail.textln(f"Email: {_signupInfos['email']}")
    mail.textln(f"Is First: {_signupInfos['isFirst']}")
    mail.textln(f"Prefer Date: {_signupInfos['preferDate']}")
    mail.textln(f"Prefer Site: {private.SIGNUP_PREFER_SITE}")

    stationStr = ""
    for station in stations:
        stationStr += f" {station.name}"
    mail.textln(f"Station:{stationStr}")
    mail.send_dev()

def parserSleep ():
    longPeriod = 10 * 60 # 10 minutes
    now = datetime.now()
    sec = now.hour * 3600 + now.minute * 60 + now.second
    remain = (24 * 60 * 60) - sec < longPeriod
    sleepSec = longPeriod
    if remain < longPeriod:
        sleepSec = remain
    elif sec < 5 * 60: # first 5 minutes in a day
        sleepSec = 30 # 30 seconds

    debug(f"Sleep for {sleepSec} seconds")
    time.sleep(sleepSec)

if __name__ == "__main__":
    info("Start booking system")
    printInfo()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式
    driver = webdriver.Chrome(options=options)

    recordTab = ChromeTab(driver)
    for station in stations:
        station.setChromeTab(driver)

    try:
        while True:
            info(f"New Parsing")
            recordTab.resetWeb()
            for station in stations:
                station.chromeTab.resetWeb()

            debug("Find old record")
            oldRecord = findExamRecord(recordTab)
            debug("Parse old exam")
            avaliableExams, unavaliableExams = findAllSites(stations)
            debug("Book exam")
            bookedExam = bookExam(oldRecord, avaliableExams)
            if bookedExam:
                info(f"Booking Success: Sending email to {private.EMAIL_RECV}")
                mail = MailHandler()
                mail.textln(f"## 路考申請成功!!!!!")
                mail.textln(f"- 地點: {bookedExam.place}")
                mail.textln(f"- 時段: {bookedExam.chineseDate}")
                mail.textln(f"- 說明: {bookedExam.description}")
                if oldRecord.isBook:
                    mail.textln(f"- 取消以下場次: {oldRecord.place} {oldRecord.chineseDate}")
                mail.plain()
                mail.send_dev()
                mail.send()

            logUnavailableExams(unavaliableExams)
            debug("====================== Parsing Finished ======================\n")

            parserSleep()

    except KeyboardInterrupt:
        info("Process interrupted by user.")
    except:
        stack_str = traceback.format_exc()
        info(f"Stack Trace: {stack_str}")
        info("Process crashed. Sending email.")
        mail = MailHandler()
        mail.textln(f"## Process crashed!!!!!")
        mail.textln(f"Please check the log.")
        mail.textln(f"Called Stack:")
        mail.textln(f"{stack_str}")
        mail.send_dev()

    driver.quit()
