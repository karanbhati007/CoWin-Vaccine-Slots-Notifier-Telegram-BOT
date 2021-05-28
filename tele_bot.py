# ScripTed BY KSB007


import requests
from datetime import datetime
import time
import schedule

base_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
api_url_telegram = "https://api.telegram.org/bot__token__/sendMessage?chat_id=@__channelId__&text="
register_cowin_url = "https://selfregistration.cowin.gov.in"

now = datetime.now()
today_date = now.strftime("%d-%m-%Y")
DAILY_SCHEDULED_TIME = "00:00"
telegram_channel_id = "<YOUR_TELEGRAM_CHANNEL_ID>"
telegram_bot_token = "<YOUR_BOT_TOKEN>"
district_ids = [199] # Faridabad
dis_id = 199 # For Test 142, West Delhi
save_data=[]

def fetchData(district_id):
    query = "?district_id={}&date={}".format(district_id,today_date)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = base_url + query
    response = requests.get(url,headers=headers)
    getInfo(response.json())

# For Multiple Districts
# def fetchDistrictData(district_ids):
#     for dis_id in district_ids:
#         fetchData(dis_id)


def getInfo(json_response):
    for center in json_response["centers"]:
        if(center not in save_data):
            save_data.append(center)

            center_name = center["name"]
            fee_type = center["fee_type"]
            block_name = center["block_name"]
            district_name = center["district_name"]
            pincode = center["pincode"]

            #### if vaccine is Paid

            covishield_price = "Free"
            covaxin_price = "Free"
            
            if fee_type == "Paid":
                for vf in center["vaccine_fees"]:
                    if vf["vaccine"] == "COVISHIELD":
                        covishield_price = vf["fee"]
                    else:
                        covaxin_price = vf["fee"]

            ####

            for session in center["sessions"]:
                session_date = session["date"]
                available_capacity = session["available_capacity"]
                min_age_limit = session["min_age_limit"]
                vaccine_type = session["vaccine"]
                dose1 = session["available_capacity_dose1"]
                dose2 = session["available_capacity_dose2"]
                session_formated_date = datetime.strptime(session_date, '%d-%m-%Y').strftime('%b %d')
                vaccine_cost = "Free"

            
                if fee_type == "Paid":
                    if vaccine_type == "COVISHIELD":
                        vaccine_cost = covishield_price
                    else:
                        vaccine_cost = covaxin_price

                if block_name == "Not Applicable":
                    block_name = district_name

                if(min_age_limit == 18 and session_date==today_date and dose1>0): # min_age_limit == 18
                    tele_message = (
                    f"\nAge Group for {min_age_limit}+:\n"
                    f"Name: {center_name} ({district_name})\n"
                    f"Block: {block_name}\n"
                    f"Pin Code: {pincode}\n" 
                    f"Vaccine: {vaccine_type}\n"
                    f"Fees: {vaccine_cost}\n"
                    f"Total Available: {available_capacity} slots as on {session_formated_date}\n" 
                    f"Dose 1: {dose1} , Dose 2: {dose2}\n\n"
                    
                    f"Book Slots Fast -> {register_cowin_url}\n\n"
                    "-------------------------")

                    send_to_telegram_bot(tele_message)
                    time.sleep(5)



def send_to_telegram_bot(tele_message):
    print(tele_message)
    tele_url = api_url_telegram.replace("__channelId__",telegram_channel_id)
    tele_url = tele_url.replace("__token__",telegram_bot_token)
    final_tele_url = tele_url + tele_message
    response = requests.get(final_tele_url)
    print(response)


def runScript():
    while(1):
        fetchData(dis_id)
        time.sleep(20) # fetch in every 20 sec


def attemptRoutine():
    save_data.clear
    try:
        runScript()
    except Exception as err:
        print(f"Routine Failed !!\n {err}")
        time.sleep(60*60)
        runScript()



# Daily Routine
attemptRoutine()
schedule.every().day.at(DAILY_SCHEDULED_TIME).do(attemptRoutine)



while True:
    schedule.run_pending()
    time.sleep(60*60) # wait one hour

# if __name__ == "__main__":
#     runScript()

