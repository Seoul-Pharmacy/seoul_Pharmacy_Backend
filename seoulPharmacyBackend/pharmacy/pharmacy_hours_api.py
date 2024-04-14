import json
import logging
from venv import logger
import requests
import my_settings

SECRET_KEY = my_settings.SEOUL_API_SECRET_KEY
PHARMACY_HOURS_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/%d/%d/"
SIMPLE_PHARMACY_HOURS_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/1/1/"
PHARMACY_HOURS_START_INDEX = 1



def get_pharmacy_hours_total_count():
    data = requests.get(SIMPLE_PHARMACY_HOURS_URL % SECRET_KEY).json()

    logging.warning(data['TbPharmacyOperateInfo']['list_total_count'])
    return data['TbPharmacyOperateInfo']['list_total_count']


