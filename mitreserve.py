import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

with open('credentials.json') as f:
    credentials = json.load(f)
username = credentials['username']
password = credentials['password']
# Every user has a system user_id
user_id = credentials['user_id']
# And also a constant event token for reservations. Not sure why they have this
event_member_token_reserve_court = credentials['event_member_token_reserve_court']

login_page_url = 'https://mit.clubautomation.com/'
login_submit_url = 'https://mit.clubautomation.com/login/login'
auth_url = 'https://mit.clubautomation.com/client/auth/authorize-current-user'
reserve_url = 'https://mit.clubautomation.com/event/reserve-court-new-do?ajax=true'

# Courts can be reserved at most 2 days in advance
days_in_advance = 2
hours = [19, 18, 20]

session = requests.Session()

# Need to retrieve a login token from the login page
login_page_content = session.get(login_page_url).text
soup = BeautifulSoup(login_page_content, 'html.parser')
login_token = soup.find('input', {'name': 'login_token'})['value']

# All login form data needed
form_data = {
    'email': username,
    'password': password,
    'login_token': login_token
}

# Making POST to actually login
phpsessid = session.cookies['PHPSESSID']
headers = {
    'Host': 'mit.clubautomation.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'X-INSTANA-T': '30a351f964f33a8f',
    'X-INSTANA-S': '30a351f964f33a8f',
    'X-INSTANA-L': '1,correlationType=web;correlationId=30a351f964f33a8f',
    'Content-Length': '79',
    'Origin': 'https://mit.clubautomation.com',
    'Connection': 'keep-alive',
    'Referer': 'https://mit.clubautomation.com/',
    'Cookie': f'PHPSESSID={phpsessid}',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=1'
}
session.post(login_submit_url, data=form_data, headers=headers)
# The SessionExpirationTime and isLoggedIn cookies aren't filled in until another request is made
session.get(login_page_url)

# Making POST to the authentiation url to get bearer token
# Cloudflare bot management cookie. Hasn't been a problem
__cf_bm = session.cookies['__cf_bm']
headers = {
    'Host': 'mit.clubautomation.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Origin': 'https://mit.clubautomation.com',
    'Connection': 'keep-alive',
    'Referer': 'https://mit.clubautomation.com/member',
    'Cookie': f'PHPSESSID={phpsessid}; __cf_bm={__cf_bm}; isLoggedIn=1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Content-Length': '0',
    'TE': 'trailers'
}
session.post(auth_url, headers=headers)

session_expiration_time = session.cookies['SessionExpirationTime']
future_date = datetime.now() + timedelta(days=days_in_advance)
formatted_date = future_date.strftime('%m/%d/%Y')

# Send POST to reserve courts
def reservation_call(hour: int):
    headers = {
        'Host': 'mit.clubautomation.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'X-INSTANA-T': '58d4bfbcea0d46cc',
        'X-INSTANA-S': '58d4bfbcea0d46cc',
        'X-INSTANA-L': '1,correlationType=web;correlationId=58d4bfbcea0d46cc',
        'Content-Length': '315',
        'Origin': 'https://mit.clubautomation.com',
        'Connection': 'keep-alive',
        'Referer': 'https://mit.clubautomation.com/event/reserve-court-new',
        'Cookie': f'PHPSESSID={phpsessid}; __cf_bm={__cf_bm}; SessionExpirationTime={session_expiration_time}; isLoggedIn=1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=1',
    }
    future_date_time = future_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    epoch_seconds = str(int(future_date_time.timestamp()))
    data = {
        'reservation-list-page': '1',
        'user_id': user_id,
        'event_member_token_reserve_court': event_member_token_reserve_court,
        'current_guest_count': '0',
        'component': '2',
        'club': '-1',
        'court': '-1', # -1 is the value for any court
        'host': user_id,
        'date': formatted_date,
        'interval': '60',
        'time-reserve': epoch_seconds,
        'location-reserve': '32', # Tennis courts have value 32
        'surface-reserve': '0',
        'courtsnotavailable': '',
        'join-waitlist-case': '1',
        'is_confirmed': '1'
    }
    return session.post(reserve_url, headers=headers, data=data)


for hour in hours:
    logging.info(f'Attempting reservation for {formatted_date} hour {hour}:00')
    response = reservation_call(hour)
    if ('Reservation Completed' in response.text):
        logging.info(f'Reservation successful for {formatted_date} at {hour}:00')
        break
    else:
        logging.info(f'Unable to reserve court for {formatted_date} at {hour}:00')
