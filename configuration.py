unix_environ_path = '/usr/lib/chromium/chromium'

foody_account = {
    'username': "mailtemp314@gmail.com",
    'password': "thisistempmail"
}

foody_link = "https://www.foody.vn/ho-chi-minh"

mongodb_connection_string = "mongodb+srv://username:Password123@udptdltm-data.ocmcsqz.mongodb.net/test"

import logging
logging.basicConfig(filename="logger.log",
                    filemode='w',
                    format='%(asctime)s , %(thread)d %(levelname)s : %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)