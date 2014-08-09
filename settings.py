from logging            import DEBUG, INFO, WARN, ERROR

# Crawl settings
ITERATION_SLEEP_SEC =   60*15       # 15 min

# Query settings
AREA_ID                 = 48        # tlv center
FROM_ROOMS              = 2         # min rooms
TO_ROOMS                = 3         # max rooms
FROM_PRICE              = 5000      # min price
TO_PRICE                = 7000      # max price
ONLY_PETS_ALLOWED       = False     # remove without pets
ONLY_WITH_PARKING       = False     # remove without parking
ONLY_RENOVATED          = False     # remove not renovated
ONLY_PRIVATE            = False     # remove 'tivuh'
ONLY_WITH_PHOTO         = False     # remove without photos
MAX_AGE_DAYS            = 2         # remove older than 2 days

# Locations (latitude, longitude, radius, name)
LOCATIONS = [
    (32.080584, 34.780591, 0.7, "Rabin square"),
    (32.072375, 34.779196, 0.7, "Bima square"),
    (32.077957, 34.784367, 0.5, "Dubonov"),
]

# Mail settings
GMAIL_USER = "<GMAIL USER>"
GMAIL_PASS = "<GMAIL PASSWORD>"
NOTIFICATION_RECIPIENT = "<EMAIL ADDRESS TO SEND NOTIFICATIONS>"
NOTIFICATION_SUBJECT = "Yad2: new @%AREA%: %DESCRIPTION%"

# Log
LOG_LEVEL = DEBUG
LOG_FILE = 'yad2.log'
LOG_FORMAT = "%(asctime)s [%(levelname)-5.5s]  %(message)s"