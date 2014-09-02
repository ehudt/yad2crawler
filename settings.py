from logging            import DEBUG, INFO, WARN, ERROR

# Crawl settings
ITERATION_SLEEP_SEC =   60*15       # 15 min

# Apartments

# Query settings
CAT_ID                  = 2         # apartment
SUB_CAT_ID              = 2         # rent
AREA_ID                 = 48        # tlv center
FROM_ROOMS              = 2         # min rooms
TO_ROOMS                = 3         # max rooms
FROM_PRICE              = 5000      # min price
TO_PRICE                = 7000      # max price
ONLY_PETS_ALLOWED       = False     # remove without pets
ONLY_WITH_PARKING       = False     # remove without parking
ONLY_PRIVATE            = False     # remove 'tivuh'
ONLY_WITH_PHOTO         = False     # remove without photos
MAX_AGE_DAYS            = 2         # remove older than 2 days

# Locations (latitude, longitude, radius, name)
LOCATIONS = [
    (32.080584, 34.780591, 0.7, "Rabin square"),
    (32.072375, 34.779196, 0.7, "Bima square"),
]

# Mail settings
GMAIL_USER = "<SOME GMAIL USER>"
GMAIL_PASS = "<SOME GMAIL PASS>"
NOTIFICATION_RECIPIENT = "<YOUR MAIL>"
NOTIFICATION_SUBJECT = "Yad2: new @%AREA%: %DESCRIPTION%"

# Log
LOG_LEVEL = DEBUG
LOG_FILE = 'yad2.log'
LOG_FORMAT = "%(asctime)s [%(levelname)-5.5s]  %(message)s"

# Proxy
PROXY = {
    # "http":  "localhost:8888",
    # "https": "localhost:8888",
}