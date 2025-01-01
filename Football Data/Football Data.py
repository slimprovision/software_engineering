# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 14:33:43 2024

@author: Dilara
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from selenium.common.exceptions import NoSuchElementException

# Chrome seçeneklerini ayarla
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")  # Gizli mod ekleniyor

# WebDriver'i başlat
driver_path = "C:/Users/Dilara/Documents/ChromeDriver/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
#kullanıcaıdan alınacak.
league="La Liga"
season="1999-2000"
date="21.08.1999"
day, month, year = date.split(".")

def finding_URL(league,season):
    if league=="Premier League":#England
        lig="ingiltere-premier-lig"
        x="2kwbbcootiqqgmrzs6o5inle5"
    elif league=="Super League":#Turkey
        lig="türkiye-trendyol-süper-lig"
        x="482ofyysbdbeoxauk19yg7tdt"
    elif league=="Serie A":#Italy
        lig="italya-serie-a"
        x="1r097lpxe0xn03ihb7wi98kao"
    elif league=="Bundesliga":#Germany
        lig="almanya-bundesliga"
        x="6by3h89i2eykc341oz7lv1ddd"
    elif league=="Ligue 1":#France
        lig="fransa-ligue-1"
        x="dm5ka0os1e3dxcp3vh05kmp33"
    elif league=="La Liga":#Spain
        lig="ispanya-laliga"
        x="34pl8szyvrbwcmfkuocjm3r6t"
    else:
        print("You write wrong league")
    url=f"https://www.mackolik.com/puan-durumu/{lig}/{season}/fikstur/{x}"
    return url

url=finding_URL(league, season)

def month_to_text(month):
    if month =="01":
        return"Oca"
    elif month =="02":
        return "Şub"
    elif month=="03":
        return "Mar"
    elif month=="04":
        return "Nis"
    elif month=="05":
        return "May"
    elif month=="06":
        return "Haz"
    elif month=="07":
        return "Tem"
    elif month=="08":
        return "Ağu"
    elif month=="09":
        return "Eyl"
    elif month=="10":
        return "Eki"
    elif month=="11":
        return "Kas"
    elif month=="12":
        return "Aralık"

def extract_data(date):
    #all_matches_on_date = driver.find_elements(By.CLASS_NAME, "p0c-competition-match-list__days")#günlük oynanan maçlar
    day, month, year = date.split(".")
    x_date=f"{year}-{month}-{day}"
    time.sleep(1)
    matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
    blue_buttons=matches_on_date.find_elements(By.CLASS_NAME, 'p0c-competition-match-list__button')
    matches_data = []
    for button in blue_buttons:
        home_team_members=[]
        away_team_members=[]
        WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(button)
            )
        button.click()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])  # Son açılan sekmeye geçiş yap
        time.sleep(10)  # Sekmenin tamamen yüklenmesi için biraz bekleyin
        try:
            #home teknik direktör
            x=driver.find_elements(By.CLASS_NAME,"widget-match-stats__team--home")
            if len(x)==3:
                home_coach_table=driver.find_elements(By.CLASS_NAME,"widget-match-stats__team--home")[2]
                home_coach=home_coach_table.find_element(By.CLASS_NAME,"widget-match-stats__person-name")
                #away teknik direktör 
                away_coach_table=driver.find_elements(By.CLASS_NAME,"widget-match-stats__team--away")[2]
                away_coach=home_coach_table.find_element(By.CLASS_NAME,"widget-match-stats__person-name")
            
        except NoSuchElementException:
            home_coach="No data"
            away_coach="No data"
        try:
            #home diziliş
            home_formation_container=driver.find_element(By.CLASS_NAME,"Opta-Home")
            home_formation=home_formation_container.find_element(By.CLASS_NAME,"Opta-TeamFormation").text
            #away diziliş
            away_formation_container=driver.find_element(By.CLASS_NAME,"Opta-Away")
            away_formation=away_formation_container.find_element(By.CLASS_NAME,"Opta-TeamFormation").text
        except NoSuchElementException:   
            home_formation="No data"
            away_formation="No data"
        
        #takım isimleri
        home_team=driver.find_element(By.CLASS_NAME, 'p0c-soccer-match-details-header__team-name--home').text
        away_team=driver.find_element(By.CLASS_NAME, 'p0c-soccer-match-details-header__team-name--away').text
        
        home_score=driver.find_element(By.CLASS_NAME, 'p0c-soccer-match-details-header__score-home').text
        away_score=driver.find_element(By.CLASS_NAME, 'p0c-soccer-match-details-header__score-away').text

        #ilk 11 home
        home_team_members_table=driver.find_element(By.CLASS_NAME, 'widget-match-stats__team--home')
        home_team_members_row=home_team_members_table.find_elements(By.CLASS_NAME,"widget-match-stats__row")
        i=1
        for members in home_team_members_row:
            member_name=members.find_element(By.CLASS_NAME,"widget-match-stats__person-name").text
            member_shirt_number=members.find_element(By.CLASS_NAME,"widget-match-stats__cell--shirt-number").text
            member_position=members.find_element(By.CLASS_NAME,"widget-match-stats__cell--person-position").text
            home_team_member={
                f"{i}.Member_name":member_name,
                f"{i}.Member_shirt_number":member_shirt_number,
                f"{i}.Member_position":member_position
                }
            i=i+1
            home_team_members.append(home_team_member)
            
        #home yellow cards
        home_yellow_card_counter=0
        home_yellow_card_elements = home_team_members_table.find_elements(By.CLASS_NAME, "widget-match-stats__icon--yellow-card")
        home_yellow_card_counter = len(home_yellow_card_elements)  # Bulunan tüm sarı kartları say
        #home red cards
        home_red_card_counter=0
        home_red_card_elements = home_team_members_table.find_elements(By.CLASS_NAME, "widget-match-stats__icon--red-card")
        home_red_card_counter = len(home_red_card_elements)  # Bulunan tüm sarı kartları say

        #ilk 11 away
        away_team_members_table=driver.find_element(By.CLASS_NAME, 'widget-match-stats__team--away')
        away_team_members_row=away_team_members_table.find_elements(By.CLASS_NAME,"widget-match-stats__row")
        k=1
        for members in away_team_members_row:
            member_name=members.find_element(By.CLASS_NAME,"widget-match-stats__person-name").text
            member_shirt_number=members.find_element(By.CLASS_NAME,"widget-match-stats__cell--shirt-number").text
            member_position=members.find_element(By.CLASS_NAME,"widget-match-stats__cell--person-position").text
            away_team_member={
                f"{k}.Member_name":member_name,
                f"{k}.Member_shirt_number":member_shirt_number,
                f"{k}.Member_position":member_position
                }
            k=k+1
            away_team_members.append(away_team_member)
        #away yellow cards
        away_yellow_card_counter=0
        away_yellow_card_elements = away_team_members_table.find_elements(By.CLASS_NAME, "widget-match-stats__icon--yellow-card")
        away_yellow_card_counter = len(away_yellow_card_elements)  # Bulunan tüm sarı kartları say
        #away red cards
        away_red_card_counter=0
        away_red_card_elements = away_team_members_table.find_elements(By.CLASS_NAME, "widget-match-stats__icon--red-card")
        away_red_card_counter = len(away_red_card_elements)  # Bulunan tüm sarı kartları say
        
        #istatistik kısmına tıklandığında
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'widget-match-detail-submenu__icon--stats'))
            )
            statistics_button =driver.find_element(
                By.XPATH,
                "//div[contains(@class, 'widget-match-detail-submenu__icon--stats') ]"
            )
            if statistics_button:
                statistics_button=driver.find_element(By.CLASS_NAME,"widget-match-detail-submenu__icon--stats")
                statistics_button.click()
                time.sleep(2)
                all_statistics=driver.find_elements(By.CLASS_NAME,"Opta-Outer")
                i=0
                home_playing_ball_percent=all_statistics[i].text 
                i=i+1
                away_playing_ball_percent=all_statistics[i].text 
                i=i+1
                #İkili Mücadele Kazanma
                home_winning_Binary=all_statistics[i].text 
                i=i+1
                away_winning_Binary=all_statistics[i].text 
                i=i+1
                #Hava Topu Kazanma
                home_winning_AirBall=all_statistics[i].text 
                i=i+1
                away_winning_AirBall=all_statistics[i].text 
                i=i+1
                #Pas Arası
                home_pass_Break=all_statistics[i].text 
                i=i+1
                away_pass_Break=all_statistics[i].text 
                i=i+1
                #Offside
                home_Offside=all_statistics[i].text 
                i=i+1
                away_Offside=all_statistics[i].text 
                i=i+1
                #Corner
                home_corner=all_statistics[i].text 
                i=i+1
                away_corner=all_statistics[i].text 
                i=i+1
                pas_button=driver.find_element(By.XPATH, '//a[text()="Pas"]')
                pas_button.click()
                #total pass
                home_total_pass=all_statistics[i].text 
                i=i+1
                away_total_pass=all_statistics[i].text 
                i=i+1
                #isabetli pas
                home_accurate_pass=all_statistics[i].text 
                i=i+1
                away_accurate_pass=all_statistics[i].text 
                i=i+1
                #Pass Accuracy percent
                home_accuratepass_percent=all_statistics[i].text
                i=i+1
                away_accuratepass_percent=all_statistics[i].text 
                i=i+1
                #Toplam Orta
                home_total_Centerthrows=all_statistics[i].text 
                i=i+1
                away_total_Centerthrows=all_statistics[i].text 
                i=i+1
                #isabetli orta
                home_accurate_Centerthrow=all_statistics[i].text 
                i=i+1
                away_accurate_Centerthrow=all_statistics[i].text 
                i=i+1
                Hücum_button=driver.find_element(By.XPATH, '//a[text()="Hücum"]')
                Hücum_button.click()
                #toplam şut
                home_total_Shot=all_statistics[i].text 
                i=i+1
                away_total_Shot=all_statistics[i].text 
                i=i+1
                #isabetli şut
                home_accurate_Shot=all_statistics[i].text 
                i=i+1
                away_accurate_Shot=all_statistics[i].text 
                i=i+1
                #isabetsiz şut
                home_not_accurate_Shot=all_statistics[i].text 
                i=i+1
                away_not_accurate_Shot=all_statistics[i].text 
                i=i+1
                #engellenen şut
                home_blocked_Shot=all_statistics[i].text 
                i=i+1
                away_blocked_Shot=all_statistics[i].text
                i=i+1
                #gol beklentisi
                home_Goal_Expectancy=all_statistics[i].text
                i=i+1
                away_Goal_Expectancy=all_statistics[i].text
                i=i+1
                #Rakip Ceza Sahasında Topla Buluşma
                home_MeetingBallintheOpponensPenaltyArea=all_statistics[i].text 
                i=i+1
                away_MeetingBallintheOpponensPenaltyArea=all_statistics[i].text 
                Savunma_button=driver.find_element(By.XPATH, '//a[text()="Savunma"]')
                Savunma_button.click()
                i=i+1
                #pas arası
                home_PassInterval=all_statistics[i].text 
                i=i+1
                away_PassInterval=all_statistics[i].text 
                i=i+1
                #Uzaklaştırma
                home_Suspension=all_statistics[i].text 
                i=i+1
                away_Suspension=all_statistics[i].text 
                Faul_button=driver.find_element(By.XPATH, '//a[text()="Faul"]')
                Faul_button.click()
                i=i+1
                #faul
                home_Foul=all_statistics[i].text 
                i=i+1
                away_Foul=all_statistics[i].text 
            
        except NoSuchElementException:
            print("statistics butonu yok")
            home_playing_ball_percent="No Data"
            away_playing_ball_percent="No Data"
            home_winning_Binary="No Data"
            away_playing_ball_percent="No Data"
            home_winning_Binary="No Data"
            away_winning_Binary="No Data"
            home_winning_AirBall="No Data"
            away_winning_AirBall="No Data"
            home_pass_Break="No Data"
            away_pass_Break="No Data"
            home_Offside="No Data"
            away_Offside="No Data"
            home_corner="No Data"
            away_corner="No Data"
            home_total_pass="No Data"
            away_total_pass="No Data"
            home_accurate_pass="No Data"
            away_accurate_pass="No Data"
            home_accuratepass_percent="No Data"
            away_accuratepass_percent="No Data"
            home_total_Centerthrows="No Data"
            away_total_Centerthrows="No Data"
            home_accurate_Centerthrow="No Data"
            away_accurate_Centerthrow="No Data"
            home_total_Shot="No Data"
            away_total_Shot="No Data"
            home_accurate_Shot="No Data"
            away_accurate_Shot="No Data"
            home_not_accurate_Shot="No Data"
            away_not_accurate_Shot="No Data"
            home_blocked_Shot="No Data"
            away_blocked_Shot="No Data"
            home_Goal_Expectancy="No Data"
            away_Goal_Expectancy="No Data"
            home_MeetingBallintheOpponensPenaltyArea="No Data"
            away_MeetingBallintheOpponensPenaltyArea="No Data"
            home_PassInterval="No Data"
            away_PassInterval="No Data"
            home_Suspension="No Data"
            away_Suspension="No Data"
            home_Foul="No Data"
            away_Foul="No Data"
        # Maç verilerini tabloya ekleme
        match_data = {
            "Season":season,
            "Date":date,
            "League":league,
            "Home Team": home_team,
            "Away Team": away_team,
            "Home Score": home_score,
            "Away Score": away_score,
            "Home Team Members": home_team_members,
            "Away Team Members": away_team_members, # Üyeler buraya ekleniyor# Üyeler buraya ekleniyor
            "Home Ball Percent": home_playing_ball_percent,
            "Away Ball Percent": away_playing_ball_percent,
            "Home Winning Binary":home_winning_Binary,
            "Away Winning Binary":away_winning_Binary,
            "Home Winning Air Ball":home_winning_AirBall,
            "Away Winning Air Ball":away_winning_AirBall,
            "Home Pass Break":home_pass_Break,
            "Away Pass Break":away_pass_Break,
            "Home Offside":home_Offside,
            "Away Offside":away_Offside,
            "Home Corner":home_corner,
            "Away Corner":away_corner,
            "Home Total Pass":home_total_pass,
            "Away Total Pass":away_total_pass,
            "Home Accurate Pass":home_accurate_pass,
            "Away Accurate Pass":away_accurate_pass,
            "Home Accuratepass Percent":home_accuratepass_percent,
            "Away Accuratepass Percent":away_accuratepass_percent,
            "Home Total Center Throws":home_total_Centerthrows,
            "Away Total Center Throws":away_total_Centerthrows,
            "Home Accurate Center Throw":home_accurate_Centerthrow,
            "Away Accurate Center Throw":away_accurate_Centerthrow,
            "Home Total Shot":home_total_Shot,
            "Away Total Shot":away_total_Shot,
            "Home Accurate Shot":home_accurate_Shot,
            "Away Accurate Shot":away_accurate_Shot,
            "Home Not Accurate Shot":home_not_accurate_Shot,
            "Away Not Accurate Shot":away_not_accurate_Shot,
            "Home Blocked Shot":home_blocked_Shot,
            "Away Blocked Shot":away_blocked_Shot,
            "Home Goal Expectancy":home_Goal_Expectancy,
            "Away Goal Expectancy":away_Goal_Expectancy,
            "Home Meeting Ball in the Opponen's Penalty Area":home_MeetingBallintheOpponensPenaltyArea,
            "Away Meeting Ball in the Opponen's Penalty Area":away_MeetingBallintheOpponensPenaltyArea,
            "Home Pass Interval":home_PassInterval,
            "Away Pass Interval":away_PassInterval,
            "Home Suspension":home_Suspension,
            "Away Suspension":away_Suspension,
            "Home_Foul":home_Foul,
            "Away_Foul":away_Foul,
            "Home Yellow Cards": home_yellow_card_counter,
            "Home Red Cards": home_red_card_counter,
            "Away Yellow Cards": away_yellow_card_counter,
            "Away Red Cards": away_red_card_counter,
            }
        if match_data not in matches_data:  # Tekrar kontrolü
            matches_data.append(match_data)
        # Sekmeyi kapatıp, orijinal sekmeye geri dönmek için:
        driver.close()  # Yeni sekmeyi kapat
        driver.switch_to.window(driver.window_handles[0])  # İlk sekmeye geri dön
    print(matches_data)

def accept_cookies():
    try:
        consent_button = WebDriverWait(driver, 10).until(
           EC.element_to_be_clickable((By.CLASS_NAME, 'widget-gdpr-banner__accept'))
       )
        # Çerez kabul et butonunu bul
        consent_button = driver.find_element(By.CLASS_NAME, 'widget-gdpr-banner__accept')
        
        # Butona tıkla
        consent_button.click()
        print("Çerezler kabul edildi.")
    except Exception as e:
        print(f"Çerez kabul butonu bulunamadı veya tıklanamadı: {e}")

try:
    try:
        driver.get(url)
        accept_cookies()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__arrow--prev'))
        )
        disabled_arrow =driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'widget-gameweek__arrow') and contains(@class, 'widget-gameweek__arrow--prev') and contains(@class, 'widget-gameweek__arrow--disabled')]"
        )
        if disabled_arrow:
            selected_month=""
            extract_data(date)
    except NoSuchElementException:
        # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__selected'))
            )   
        #hafta kısmındaki günü veya günleri alıyor
        days_for_this_week = driver.find_element(By.CLASS_NAME, 'widget-gameweek__selected-date').text
    
        selected_month_pre=""
        selected_month_next=""
        # İlk olarak ay ve günleri ayır
        parts = days_for_this_week.split(" ")
        # May 16 şeklinde ise 16 yı alır
        if len(parts) ==2:
            selected_month = parts[0]
            selected_day=parts[1]
            # May 16 - 20 şeklinde ise 16 min değer 20 max değer olarak alır
        elif len(parts)==4:
            selected_month = parts[0]
            selected_day_min = parts[1]
            selected_day_max = parts[3]
        elif len(parts)==5:
             selected_month_pre = parts[0]
             selected_month_next = parts[3]
             selected_day_min = parts[1]
             selected_day_max = parts[4]
        else:
            print("length is not correct")
        
        text_month=month_to_text(month)
        #istenilen aya gidene kadar geri butonuna basacak
        while text_month:
            if text_month==selected_month or text_month==selected_month_next or text_month==selected_month_pre:
                break
            else:
                # Geri butonuna tıklayın
                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                back_button.click()  # Geri butonuna tıklayın
                # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__selected'))
                    )
                #hafta kısmındaki günü veya günleri alıyor
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__selected-label'))
                    )
                text = driver.find_element(By.CLASS_NAME, 'widget-gameweek__selected-label').text
                match = re.search(r"\((.*?)\)", text)
                days_for_this_week = match.group(1)
                parts=days_for_this_week.split(" ")
                if len(parts) ==2:
                    selected_month = parts[0]
                    selected_day=parts[1]
                    # May 16 - 20 şeklinde ise 16 min değer 20 max değer olarak alır
                elif len(parts)==4:
                    selected_month = parts[0]
                    selected_day_min = parts[1]
                    selected_day_max = parts[3]
                    # Mar 29 - Nis 1 şeklinde ise "Mar"selected_month_pre, "Nis"selected_month_next, "29"selected_day_min,"1"selected_day_max
                elif len(parts)==5:
                    selected_month_pre = parts[0]
                    selected_month_next = parts[3]
                    selected_day_min = parts[1]
                    selected_day_max = parts[4]
                else:
                    print("length is not correct")
        while day:
            if day <= selected_day_max or day >= selected_day_min:
                break
            else:
                # Geri butonuna tıklayın
                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                back_button.click()  # Geri butonuna tıklayın
                # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__selected'))
                    )
                #hafta kısmındaki günü veya günleri alıyor
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__selected-label'))
                    )
                text = driver.find_element(By.CLASS_NAME, 'widget-gameweek__selected-label').text
                match = re.search(r"\((.*?)\)", text)
                days_for_this_week = match.group(1)
                parts=days_for_this_week.split(" ")
                if len(parts) ==2:
                    selected_month = parts[0]
                    selected_day=parts[1]
                    # May 16 - 20 şeklinde ise 16 min değer 20 max değer olarak alır
                elif len(parts)==4:
                    selected_month = parts[0]
                    selected_day_min = parts[1]
                    selected_day_max = parts[3]
                    #Mar 29 - Nis 1 şeklinde ise "Mar"selected_month_pre, "Nis"selected_month_next, "29"selected_day_min,"1"selected_day_max
                elif len(parts)==5:
                    selected_month_pre = parts[0]
                    selected_month_next = parts[3]
                    selected_day_min = parts[1]
                    selected_day_max = parts[4]
                else:
                    print("length is not correct")
                    
        extract_data(date)
        
except Exception as e:
    print(e)
        
finally:
    # Tarayıcıyı kapat
    driver.quit()