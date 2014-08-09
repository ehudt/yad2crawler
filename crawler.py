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
            "CatID":        "2",
            "SubCatID":     "2",
            "AreaID":       AREA_ID,
            "FromRooms":    FROM_ROOMS,
            "ToRooms":      TO_ROOMS,
            "FromPrice":    FROM_PRICE,
            "ToPrice":      TO_PRICE,
            "PriceType":    "0",
            "PetsInHouse":  "1" if ONLY_PETS_ALLOWED else "0",
            "Parking":      "1" if ONLY_WITH_PARKING else "0",
            "Page":         page,
        }

        return self.client.get_url(url, args = args)
    

    def crawl_apartments(self, json):
        found_new = None

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
            
            if ONLY_WITH_PHOTO and "missingAdPic.jpg" in img:
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

            found_new = False

            if self.db.id_exists(record_id):
                self.log.debug(".. Already exists in database")
                self.db.update_last_seen(record_id)
                continue

            self.log.info(".. Found new match %s at %s", record_id, area_name)

            self.notify_apartment(url, address, area_name)

            self.db.add_new(record_id, area_name, address, description, price, url)
            self.log.debug(".. Added to database")

            found_new = True

            self.log.debug(".. OK")

        return found_new


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

        self.log.debug(".. Getting apartment page %s", url)
        
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
            self.log.info("Starting sweep")

            page = 1
            more = True
            found_new = True

            while more and found_new:
                self.log.info("Requesting page #%d", page)

                data = self.get_page(page)
                json = loads(data)            

                found_new = False

                if 'Private' in json and 'Results' in json['Private']:
                    self.log.info(".. Checking private apartments...")
                    found_new = (self.crawl_apartments(json['Private']['Results']) == True) or found_new

                if not ONLY_PRIVATE and 'Trade' in json and 'Results' in json['Trade']:
                    self.log.info(".. Checking trade apartments...")
                    found_new = (self.crawl_apartments(json['Trade']['Results']) == True) or found_new

                more = True if json['MoreResults'] == 1 else False

                if more and not found_new:
                    self.log.info("No new results on page %d, stopping browsing", page)

                page += 1

            self.log.info("Sweep ended, going to sleep (%d min)", ITERATION_SLEEP_SEC / 60)

            sleep(ITERATION_SLEEP_SEC)

