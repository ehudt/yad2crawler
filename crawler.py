from client             import Yad2Client
from mail_notifier      import MailNotifier
from db                 import ApartmentDatabase
from log                import Log
from geo                import haversine_distance
from page_parser        import PageParser
from settings           import *
from datetime           import datetime
from json               import loads
from re                 import findall, search
from time               import sleep
from itertools          import ifilter
from win32com.client    import Dispatch


class Yad2Crawler(object):    
    def __init__(self):
        self.log = Log()

        self.client = Yad2Client()
        self.notifier = MailNotifier(GMAIL_USER, GMAIL_PASS)
        self.db = ApartmentDatabase('yad2.db')

        self.client.add_cookie('PRID', 'xx')


    def get_prid(self, html):
        hf = Dispatch('htmlfile')
        hf.writeln(html + "\n<script>document.write(\"<meta name='PRID' content='\" +genPid()+ \"'>\")</script>")
        prid = next(ifilter(lambda m: m.name == 'PRID', hf.getElementsByTagName('meta')), None)
        return prid.content if prid else None


    def get_prlst(self, html):
        prlst = ''
        for m in findall(r'String.fromCharCode\(\d*\)', html):
            match = search('\d+', m)
            if match:
                prlst += chr(int(match.group()))
                
        return prlst        


    def get_page(self, page = 1):
        url = "http://m.yad2.co.il/API/MadorResults.php"    

        args = {
            "CatID":        CAT_ID,
            "SubCatID":     SUB_CAT_ID,
            "AreaID":       AREA_ID,
            "PriceType":    0,
            "Page":         page,
        }

        if 'HOME_TYPE_ID' in globals():
            args['HomeTypeID'] = HOME_TYPE_ID

        if 'FROM_ROOMS' in globals():
            args['FromRooms'] = FROM_ROOMS

        if 'TO_ROOMS' in globals():
            args['ToRooms'] = TO_ROOMS 

        if 'FROM_PRICE' in globals():
            args['FromPrice'] = FROM_PRICE 

        if 'TO_PRICE' in globals():
            args['ToPrice'] = TO_PRICE

        if 'ONLY_PETS_ALLOWED' in globals():
            args['PetsInHouse'] = 1 if ONLY_PETS_ALLOWED else 0
            
        if 'ONLY_WITH_PARKING' in globals():
            args['Parking'] = 1 if ONLY_WITH_PARKING else 0   

        return self.client.get_url(url, args = args)
    

    def crawl_apartments(self, json):
        for apr in json:
            if apr['Type'] != 'Ad':
                continue

            if not all([val in apr.keys() for val in ['latitude', 'longitude', 'RecordID', 'URL', 'img', 'Line1', 'Line2', 'Line3', 'Line4']]):
                continue

            latitude = apr['latitude']
            longitude = apr['longitude']
            record_id = apr['RecordID']
            url = apr['URL']
            img = apr['img']
            address = apr['Line1']
            description = apr['Line2']
            price = apr['Line3']
            date = apr['Line4']

            self.log.debug(".. Checking %s", record_id)
            
            if 'ONLY_WITH_PHOTO' in globals() and ONLY_WITH_PHOTO and "missingAdPic.jpg" in img:
                self.log.debug(".. Filtering for missing img")
                continue

            area = next(ifilter(lambda (lat, lon, r, name): haversine_distance((latitude, longitude), (lat, lon)) <= r, LOCATIONS), None)
            if not area:
                self.log.debug(".. Filtering for no matching area")
                continue
            
            area_name = area[3]

            if (datetime.now() - datetime.strptime(date, "%d-%m-%Y")).days > MAX_AGE_DAYS:
                self.log.debug(".. Filtering for old update date")
                continue

            if self.db.id_exists(record_id):
                self.log.debug(".. Already exists in database")
                self.db.update_last_seen(record_id)
                continue

            self.log.info(".. Found new match %s at %s", record_id, area_name)

            self.notify_apartment(url, address, area_name)

            self.db.add_new(record_id, area_name, address, description, price, url)
            self.log.debug(".. Added to database")

            self.log.debug(".. OK")


    def notify_apartment(self, url, description, area):
        data = self.get_apartment_page(url)

        self.log.debug(".. Sending notification")

        subject = NOTIFICATION_SUBJECT
        subject = subject.replace("%URL%", url)
        subject = subject.replace("%DESCRIPTION%", description)
        subject = subject.replace("%AREA%", area)

        self.notifier.send_notification(NOTIFICATION_RECIPIENT, subject, data)


    def get_apartment_page(self, url):
        errors = True
        prid = None

        self.log.debug(".. Getting page %s", url)
        
        while errors:        
            
            html = self.client.get_url(url)
            
            if "Please activate javascript to view this site" in html:
                self.log.debug(".... Using IE to calculate PRID")
                prid = self.get_prid(html)            
                
            elif "bot, spider, crawler" in html:
                self.log.debug(".... Clearing cookies")
                self.client.clear_cookies()
  
            else:
                prlst = self.get_prlst(html)
                prid = prlst if prlst != '' else None
                errors = False

            if prid:
                self.log.debug(".... Setting PRID=%s", prid)
                self.client.add_cookie('PRID', prid)

        return self.create_apartment_body(html, url)

    def create_apartment_body(self, html, url):
        pp = PageParser(html)
        return pp.create_apartment_page(url)


    def crawl(self):        
        while True:
            try:
                self.log.info("Starting scan")

                page = 1
                more = True

                while more:
                    self.log.info("Requesting page #%d", page)

                    data = self.get_page(page)
                    json = loads(data)            

                    if 'Private' in json and 'Results' in json['Private']:
                        self.log.info(".. Checking private apartments...")
                        self.crawl_apartments(json['Private']['Results'])

                    if (not 'ONLY_PRIVATE' in globals() or not ONLY_PRIVATE) and 'Trade' in json and 'Results' in json['Trade']:
                        self.log.info(".. Checking trade apartments...")
                        self.crawl_apartments(json['Trade']['Results'])

                    more = True if json['MoreResults'] == 1 else False
                    page += 1

                self.log.info("Scan ended, going to sleep (%d min)", ITERATION_SLEEP_SEC / 60)

                sleep(ITERATION_SLEEP_SEC)
            except Exception as e:
                self.log.error(e)
