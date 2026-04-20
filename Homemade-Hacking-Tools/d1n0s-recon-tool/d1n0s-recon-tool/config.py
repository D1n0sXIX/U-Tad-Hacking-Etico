# config.py
import os

HTTP_TIMEOUT     = 10
DNS_TIMEOUT      = 5
SHODAN_API_KEY   = os.getenv("SHODAN_API_KEY", "")
WHOISXML_API_KEY = os.getenv("WHOISXML_API_KEY", "")