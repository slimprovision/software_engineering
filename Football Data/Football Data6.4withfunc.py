def run_script(league, season, date, driver_path):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import re
    import time
    from selenium.common.exceptions import NoSuchElementException
    import csv
    import pandas as pd

    # Chrome seçeneklerini ayarla
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")  # Gizli mod ekleniyor
    chrome_options.add_argument("--headless")  # Tarayıcı penceresi olmadan çalıştır
    chrome_options.add_argument("--disable-gpu")  # GPU kullanımını devre dışı bırak (bazı sistemlerde gerekli)
    # WebDriver'i başlat 
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
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

    def check_prev_button(date):
        try:
            day, month, year = date.split(".")
            x_date=f"{year}-{month}-{day}"
            # "widget-gameweek__arrow--prev" sınıfını kontrol et
            prev_arrow = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
            
            # Eğer "widget-gameweek__arrow--disabled" sınıfı varsa
            if "widget-gameweek__arrow--disabled" in prev_arrow.get_attribute("class"):
                print("Geri butonu devre dışı. Doğru tarihler kontrol ediliyor...")
                
                # Belirtilen tarihin matches_on_date'te olup olmadığını kontrol et
                try:
                    matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                    print("Tarih bulundu, veri çıkarılıyor.")
                    extract_data(date)
                    driver.quit()
                except NoSuchElementException:
                    print(f"No match played on {date} or you wrote wrong season, maybe you can try next or previous season")
                    driver.quit()
            else:
                while 1:
                    try:
                        prev_arrow.click()  # Geri butonuna tıklayın
                        break
                    except Exception as e:
                        print("Buton bulunamadı veya tıklanamadı: Bidaha basılcak")
        
        except NoSuchElementException:
            print("Geri butonu bulunamadı.")



    def extract_data(date):
        day, month, year = date.split(".")
        x_date=f"{year}-{month}-{day}"
        time.sleep(1)
        try:
            matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
            if matches_on_date:
                blue_buttons=matches_on_date.find_elements(By.CLASS_NAME, 'p0c-competition-match-list__button')
                matches_data = []
                a=1
                for button in blue_buttons:
                    home_team_members=[]
                    away_team_members=[]
                    print(f"{a}.Maç çekiliyor...")
                    WebDriverWait(driver, 50).until(
                            EC.element_to_be_clickable(button)
                        )
                    #button.click()
                    button_try(button)
                    driver.switch_to.window(driver.window_handles[-1])  # Son açılan sekmeye geçiş yap
                    #time.sleep(27)
                    wait_if_boombastic_exists(driver)
                    # Sayfa açıldıktan sonra biraz aşağı kaydırma
                    driver.execute_script("window.scrollBy(0, 100);")  # 100 piksel aşağı kaydırır

                    # Reklamları gizle
                    driver.execute_script(
                       "document.querySelectorAll('iframe').forEach(iframe => iframe.style.visibility = 'hidden');")
                      # Sekmenin tamamen yüklenmesi için biraz bekle
                    try:
                        x=driver.find_elements(By.CLASS_NAME,"widget-match-stats__team--home")
                        if len(x)==3:
                            #home teknik direktör
                            home_coach_table=driver.find_elements(By.CLASS_NAME,"widget-match-stats__team--home")[2]
                            home_coach=home_coach_table.find_element(By.CLASS_NAME,"widget-match-stats__person-name").text
                            #away teknik direktör 
                            away_coach_table=driver.find_elements(By.CLASS_NAME,"widget-match-stats__team--away")[2]
                            away_coach=away_coach_table.find_element(By.CLASS_NAME,"widget-match-stats__person-name").text
                    except NoSuchElementException:
                        home_coach="No data"
                        away_coach="No data"
                    try:
                        #home diziliş
                        home_formation_container=driver.find_element(By.XPATH, "//*[contains(@class, 'Opta-Crest') and contains(@class, 'Opta-Home')]")
                        home_formation=home_formation_container.find_element(By.CLASS_NAME,"Opta-TeamFormation").text
                        #away diziliş
                        away_formation_container=driver.find_element(By.XPATH, "//*[contains(@class, 'Opta-Crest') and contains(@class, 'Opta-Away')]")
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
                    home_red_card_counter = len(home_red_card_elements)  # Bulunan tüm kırmızı kartları say

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
                    away_red_card_counter = len(away_red_card_elements)  # Bulunan tüm kırmızı kartları say
                    
                    #istatistik kısmına tıklandığında
                    try:  
                        statistics_button=driver.find_element(By.CLASS_NAME,"widget-match-detail-submenu__icon--stats")
                        # Eğer "widget-gameweek__arrow--disabled" sınıfı varsa
                        if "widget-match-detail-submenu__icon--disabled" in statistics_button.get_attribute("class"):
                            # Belirtilen tarihin matches_on_date'te olup olmadığını kontrol et
                            print("No statistics button")
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
                            home_Suspension="No Data"
                            away_Suspension="No Data"
                            home_Foul="No Data"
                            away_Foul="No Data"
                        else:
                            wait_if_boombastic_exists(driver)
                            button_try(statistics_button)
                            wait_if_boombastic_exists(driver)
                            driver.execute_script("window.scrollBy(0, 400);")  # 500 piksel aşağı kaydırır
                            driver.execute_script(
                                "document.querySelectorAll('iframe').forEach(iframe => iframe.style.visibility = 'hidden');")
                            all_statistics=driver.find_elements(By.CLASS_NAME,"Opta-Outer")
                            i=0
                            #topla oynama
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
                            button_try(pas_button)
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
                            button_try(Hücum_button)
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
                            button_try(Savunma_button)
                            i=i+1
                            #pas arası iki kere alınmasın diye sildim savunma ve genelde var
                            #home_PassInterval=all_statistics[i].text 
                            i=i+1
                            #away_PassInterval=all_statistics[i].text 
                            i=i+1
                            #Uzaklaştırma
                            home_Suspension=all_statistics[i].text 
                            i=i+1
                            away_Suspension=all_statistics[i].text 
                            Faul_button=driver.find_element(By.XPATH, '//a[text()="Faul"]')
                            button_try(Faul_button)
                            time.sleep(1)
                            #i=i+1
                            #faul i=40 ,41
                            home_Foul=all_statistics[-4].text 
                            #i=i+1
                            away_Foul=all_statistics[-3].text 
                            a=a+1#kaçıncı maç çekildiğini göstermek için
                            

                        
                    except NoSuchElementException:
                        print("No statistics button")
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
                        "1.Home Team Member Name": home_team_members[0]['1.Member_name'],
                        "2.Home Team Member Name": home_team_members[1]['2.Member_name'],
                        "3.Home Team Member Name": home_team_members[2]['3.Member_name'],
                        "4.Home Team Member Name": home_team_members[3]['4.Member_name'],
                        "5.Home Team Member Name": home_team_members[4]['5.Member_name'],
                        "6.Home Team Member Name": home_team_members[5]['6.Member_name'],
                        "7.Home Team Member Name": home_team_members[6]['7.Member_name'],
                        "8.Home Team Member Name": home_team_members[7]['8.Member_name'],
                        "9.Home Team Member Name": home_team_members[8]['9.Member_name'],
                        "10.Home Team Member Name": home_team_members[9]['10.Member_name'],
                        "11.Home Team Member Name": home_team_members[10]['11.Member_name'],
                        "1.Home Team Member Shirt Number": home_team_members[0]['1.Member_shirt_number'],
                        "2.Home Team Member Shirt Number": home_team_members[1]['2.Member_shirt_number'],
                        "3.Home Team Member Shirt Number": home_team_members[2]['3.Member_shirt_number'],
                        "4.Home Team Member Shirt Number": home_team_members[3]['4.Member_shirt_number'],
                        "5.Home Team Member Shirt Number": home_team_members[4]['5.Member_shirt_number'],
                        "6.Home Team Member Shirt Number": home_team_members[5]['6.Member_shirt_number'],
                        "7.Home Team Member Shirt Number": home_team_members[6]['7.Member_shirt_number'],
                        "8.Home Team Member Shirt Number": home_team_members[7]['8.Member_shirt_number'],
                        "9.Home Team Member Shirt Number": home_team_members[8]['9.Member_shirt_number'],
                        "10.Home Team Member Shirt Number": home_team_members[9]['10.Member_shirt_number'],
                        "11.Home Team Member Shirt Number": home_team_members[10]['11.Member_shirt_number'],
                        "1.Home Team Member Position": home_team_members[0]['1.Member_position'],
                        "2.Home Team Member Position": home_team_members[1]['2.Member_position'],
                        "3.Home Team Member Position": home_team_members[2]['3.Member_position'],
                        "4.Home Team Member Position": home_team_members[3]['4.Member_position'],
                        "5.Home Team Member Position": home_team_members[4]['5.Member_position'],
                        "6.Home Team Member Position": home_team_members[5]['6.Member_position'],
                        "7.Home Team Member Position": home_team_members[6]['7.Member_position'],
                        "8.Home Team Member Position": home_team_members[7]['8.Member_position'],
                        "9.Home Team Member Position": home_team_members[8]['9.Member_position'],
                        "10.Home Team Member Position": home_team_members[9]['10.Member_position'],
                        "11.Home Team Member Position": home_team_members[10]['11.Member_position'],
                        "1.Away Team Member Name": away_team_members[0]['1.Member_name'],
                        "2.Away Team Member Name": away_team_members[1]['2.Member_name'],
                        "3.Away Team Member Name": away_team_members[2]['3.Member_name'],
                        "4.Away Team Member Name": away_team_members[3]['4.Member_name'],
                        "5.Away Team Member Name": away_team_members[4]['5.Member_name'],
                        "6.Away Team Member Name": away_team_members[5]['6.Member_name'],
                        "7.Away Team Member Name": away_team_members[6]['7.Member_name'],
                        "8.Away Team Member Name": away_team_members[7]['8.Member_name'],
                        "9.Away Team Member Name": away_team_members[8]['9.Member_name'],
                        "10.Away Team Member Name": away_team_members[9]['10.Member_name'],
                        "11.Away Team Member Name": away_team_members[10]['11.Member_name'],
                        "1.Away Team Member Shirt Number": away_team_members[0]['1.Member_shirt_number'],
                        "2.Away Team Member Shirt Number": away_team_members[1]['2.Member_shirt_number'],
                        "3.Away Team Member Shirt Number": away_team_members[2]['3.Member_shirt_number'],
                        "4.Away Team Member Shirt Number": away_team_members[3]['4.Member_shirt_number'],
                        "5.Away Team Member Shirt Number": away_team_members[4]['5.Member_shirt_number'],
                        "6.Away Team Member Shirt Number": away_team_members[5]['6.Member_shirt_number'],
                        "7.Away Team Member Shirt Number": away_team_members[6]['7.Member_shirt_number'],
                        "8.Away Team Member Shirt Number": away_team_members[7]['8.Member_shirt_number'],
                        "9.Away Team Member Shirt Number": away_team_members[8]['9.Member_shirt_number'],
                        "10.Away Team Member Shirt Number": away_team_members[9]['10.Member_shirt_number'],
                        "11.Away Team Member Shirt Number": away_team_members[10]['11.Member_shirt_number'],
                        "1.Away Team Member Position": away_team_members[0]['1.Member_position'],
                        "2.Away Team Member Position": away_team_members[1]['2.Member_position'],
                        "3.Away Team Member Position": away_team_members[2]['3.Member_position'],
                        "4.Away Team Member Position": away_team_members[3]['4.Member_position'],
                        "5.Away Team Member Position": away_team_members[4]['5.Member_position'],
                        "6.Away Team Member Position": away_team_members[5]['6.Member_position'],
                        "7.Away Team Member Position": away_team_members[6]['7.Member_position'],
                        "8.Away Team Member Position": away_team_members[7]['8.Member_position'],
                        "9.Away Team Member Position": away_team_members[8]['9.Member_position'],
                        "10.Away Team Member Position":away_team_members[9]['10.Member_position'],
                        "11.Away Team Member Position":away_team_members[10]['11.Member_position'],
                        "Home Coach":home_coach,
                        "Away Coach":away_coach,
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
                        "Home Suspension":home_Suspension,
                        "Away Suspension":away_Suspension,
                        "Home_Foul":home_Foul,
                        "Away_Foul":away_Foul,
                        "Home Yellow Cards": home_yellow_card_counter,
                        "Home Red Cards": home_red_card_counter,
                        "Away Yellow Cards": away_yellow_card_counter,
                        "Away Red Cards": away_red_card_counter,
                        "Home Formation":home_formation,
                        "Away Formation":away_formation,
                        }
                    if match_data not in matches_data:  # Tekrar kontrolü
                        matches_data.append(match_data)
                    # Sekmeyi kapatıp, orijinal sekmeye geri dönmek için:
                    driver.close()  # Yeni sekmeyi kapat
                    driver.switch_to.window(driver.window_handles[0])  # İlk sekmeye geri dön
                print(matches_data)
                # CSV dosyasına yazma işlemi
                # 'matches_data' listesindeki sözlüklerden bir DataFrame oluşturun
                df = pd.DataFrame(matches_data)

            # CSV dosyasına yazma
                output_file = "matches_data.csv"
                df.to_csv(output_file, index=False, encoding='utf-8-sig',sep=';')

                print(f"Veriler '{output_file}' dosyasına başarıyla kaydedildi.")
        except NoSuchElementException:
            print(f"No match played on {date}.")

    def wait_if_boombastic_exists(driver):
        try:
            # HTML yapısında "boombastic-takeover-container" class'ını kontrol et
            time.sleep(2)
            driver.find_element(By.CLASS_NAME, "boombastic-takeover-container")
            print("Boombastic element bulundu. 28 saniye bekleniyor...")
            time.sleep(28)  # 28 saniye bekle
        except NoSuchElementException:
            print("Boombastic element bulunamadı. Devam ediliyor...")

    def accept_cookies():
        while 1:
            try:
                consent_button = WebDriverWait(driver, 50).until(
                   EC.element_to_be_clickable((By.CLASS_NAME, 'widget-gdpr-banner__accept'))
               )
                # Çerez kabul et butonunu bul
                consent_button = driver.find_element(By.CLASS_NAME, 'widget-gdpr-banner__accept')
                
                # Butona tıkla
                consent_button.click()
                print("Çerezler kabul edildi.")
                break
            except Exception as e:
                print("Çerez kabul butonu bulunamadı veya tıklanamadı: Bidaha basılcak")

                
    def button_try(button):
        while 1:
            try:
                button.click()  # Geri butonuna tıklayın
                break
            except Exception as e:
                print("Buton bulunamadı veya tıklanamadı: Bidaha basılcak")
                
        


    def get_selected_date_parts(days_for_this_week):
        # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
        selected_month="0"#i=0
        selected_day="0"# i=1
        selected_day_min="0" #i=2
        selected_day_max="0"#i=3
        selected_month_pre="0"#i=4
        selected_month_next="0"#i=5
      
        parts = days_for_this_week.split(" ")
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
            return "length is not correct"
        return [selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next]                    

    def get_selected_label_parts():
        # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
        selected_month="0"#i=0
        selected_day="0"# i=1
        selected_day_min="0" #i=2
        selected_day_max="0"#i=3
        selected_month_pre="0"#i=4
        selected_month_next="0"#i=5
      
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
            return "length is not correct"
        return [selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next]
    def go_week_date(date):
        #hafta kısmındaki günü veya günleri alıyor
        days_for_this_week = driver.find_element(By.CLASS_NAME, 'widget-gameweek__selected-date').text
        if days_for_this_week:
            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_date_parts(days_for_this_week)
            day, month, year = date.split(".")
            text_month=month_to_text(month)
            #istenilen aya gidene kadar geri butonuna basacak
            while 1:
                if text_month==selected_month_next:
                        if int(day)<=int(selected_day_max):
                            try:
                                day, month, year = date.split(".")
                                x_date=f"{year}-{month}-{day}"
                                matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                                display_style = matches_on_date.get_attribute("style")
                                print(display_style)
                                if "display: none;" in display_style:
                                    print('Öğe gizli, geri butonuna basılıyor...')                            
                                    back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                    button_try(back_button)
                                    selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
                                else:
                                    print('Öğe görünür, işlem yapılıyor...')
                                    break
                            except NoSuchElementException:
                                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                button_try(back_button)
                                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                        else:
                            check_prev_button(date)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                        
                elif text_month==selected_month_pre:
                    if int(day)>=int(selected_day_min):
                        try:
                            day, month, year = date.split(".")
                            x_date=f"{year}-{month}-{day}"
                            matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                            display_style = matches_on_date.get_attribute("style")
                            print(display_style)
                            if "display: none;" in display_style:
                                print('Öğe gizli, geri butonuna basılıyor...')
                                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                button_try(back_button)
                                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
                            else:
                                print('Öğe görünür, işlem yapılıyor...')
                                break
                        except NoSuchElementException:
                            back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                            button_try(back_button)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
                                

                    else:
                        check_prev_button(date)
                        selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
                                


                elif selected_month==text_month:
                    if selected_day_min!="0" and selected_day_max!="0":
                        if int(day)>=int(selected_day_min) and int(day)<=int(selected_day_max):
                            try:
                                day, month, year = date.split(".")
                                x_date=f"{year}-{month}-{day}"
                                matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                                display_style = matches_on_date.get_attribute("style")
                                print(display_style)
                                if "display: none;" in display_style:
                                    print('Öğe gizli, geri butonuna basılıyor...')
                                    back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                    button_try(back_button)
                                    selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                                else:
                                    print('Öğe görünür, işlem yapılıyor...')
                                    break
                            except NoSuchElementException:
                                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                button_try(back_button)
                                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                        else:
                            check_prev_button(date)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                   
                    elif selected_day!="0":
                        if day==selected_day:
                            try:
                                day, month, year = date.split(".")
                                x_date=f"{year}-{month}-{day}"
                                matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                                display_style = matches_on_date.get_attribute("style")
                                print(display_style)
                                if "display: none;" in display_style:
                                    print('Öğe gizli, geri butonuna basılıyor...')
                                    back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                    button_try(back_button)
                                    selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                                else:
                                    print('Öğe görünür, işlem yapılıyor...')
                                    break
                            except NoSuchElementException:
                                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                button_try(back_button)
                                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                        else:
                            check_prev_button(date)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                else:
                   check_prev_button(date)
                   selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()


    def go_week_label(date):
        selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
        day, month, year = date.split(".")
        text_month=month_to_text(month)
        #istenilen aya gidene kadar geri butonuna basacak
        while 1:
            if text_month==selected_month_next:
                    if int(day)<=int(selected_day_max):
                        try:
                            day, month, year = date.split(".")
                            x_date=f"{year}-{month}-{day}"
                            matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                            if matches_on_date:
                                break
                        except NoSuchElementException:
                            back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                            button_try(back_button)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                    else:
                        # Geri butonuna tıklayın
                        check_prev_button(date)
                        # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
                        selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                    
            elif text_month==selected_month_pre:
                if int(day)>=int(selected_day_min):
                    try:
                        day, month, year = date.split(".")
                        x_date=f"{year}-{month}-{day}"
                        matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                        display_style = matches_on_date.get_attribute("style")
                        print(display_style)
                        if "display: none;" in display_style:
                            print('Öğe gizli, geri butonuna basılıyor...')
                            back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                            button_try(back_button)
                        else:
                            print('Öğe görünür, işlem yapılıyor...')
                            break
                    except NoSuchElementException:
                        back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                        button_try(back_button)
                        selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
                            

                else:
                    # Geri butonuna tıklayın
                    check_prev_button(date)
                    # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
                    selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
                            


            elif selected_month==text_month:
                if selected_day_min!="0" and selected_day_max!="0":
                    if int(day)>=int(selected_day_min) and int(day)<=int(selected_day_max):
                        try:
                            day, month, year = date.split(".")
                            x_date=f"{year}-{month}-{day}"
                            matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                            display_style = matches_on_date.get_attribute("style")
                            print(display_style)
                            if "display: none;" in display_style:
                                print('Öğe gizli, geri butonuna basılıyor...')
                                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                button_try(back_button)
                                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                            else:
                                print('Öğe görünür, işlem yapılıyor...')
                                break
                        except NoSuchElementException:
                            back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                            button_try(back_button)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                    else:
                        check_prev_button(date)
                        selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

               
                elif selected_day!="0":
                    if day==selected_day:
                        try:
                            day, month, year = date.split(".")
                            x_date=f"{year}-{month}-{day}"
                            matches_on_date = driver.find_element(By.CSS_SELECTOR, f"li.p0c-competition-match-list__day[data-day='{x_date}']")
                            display_style = matches_on_date.get_attribute("style")
                            print(display_style)
                            if "display: none;" in display_style:
                                print('Öğe gizli, geri butonuna basılıyor...')
                                back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                                button_try(back_button)
                                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                            else:
                                print('Öğe görünür, işlem yapılıyor...')
                                break
                        except NoSuchElementException:
                            back_button = driver.find_element(By.CLASS_NAME, "widget-gameweek__arrow--prev")
                            button_try(back_button)
                            selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

                    else:
                        check_prev_button(date)
                        # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
                        selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()

            else:
                # Geri butonuna tıklayın
                check_prev_button(date)
                # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
                selected_month, selected_day, selected_day_min, selected_day_max, selected_month_pre, selected_month_next = get_selected_label_parts()
    try:
        try:
            driver.get(url)
            wait_if_boombastic_exists(driver)
            accept_cookies()
            WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'widget-gameweek__arrow--prev'))
            )
            disabled_arrow =driver.find_element(
                By.XPATH,
                "//div[contains(@class, 'widget-gameweek__arrow') and contains(@class, 'widget-gameweek__arrow--prev') and contains(@class, 'widget-gameweek__arrow--disabled')]"
            )
            if disabled_arrow:
                extract_data(date)
        except NoSuchElementException:#haftalı olanlar
            # Sayfa yüklendikten sonra içeriklerin görünmesini bekleyin
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'widget-gameweek__selected'))
                )   
            try:
                go_week_date(date)

            except NoSuchElementException:
                go_week_label(date)
            extract_data(date) 
            return "success"
    except Exception as e:
        print(e)
            
    finally:
        # Tarayıcıyı kapat
        driver.quit()


if __name__ == "__main__":
    print("Bu modül bir başkası tarafından çağrılmak için tasarlanmıştır.")