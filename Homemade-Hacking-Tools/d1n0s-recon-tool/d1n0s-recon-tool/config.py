import os
from dotenv import load_dotenv

load_dotenv()

HTTP_TIMEOUT     = 10
DNS_TIMEOUT      = 5
SHODAN_API_KEY   = os.getenv("SHODAN_API_KEY", "")