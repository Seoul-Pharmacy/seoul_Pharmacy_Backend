import logging
from datetime import time, datetime

logger = logging.getLogger('django')

from common.exceptions import ApiNotFoundException, ApiInternalServerError, ApiKeyForbidden
import requests

from common import my_settings
from pharmacy.models import Pharmacy

SECRET_KEY = my_settings.SEOUL_API_SECRET_KEY
PHARMACY_HOURS_API_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/%d/%d/"
SIMPLE_PHARMACY_HOURS_API_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/1/1/"
PHARMACY_HOURS_START_INDEX = 1
PHARMACY_HOURS_DATA_UNIT = 1000


# 약국 운영시간 데이터 개수 가져오기
def get_pharmacy_hours_total_count():
    data = requests.get(SIMPLE_PHARMACY_HOURS_API_URL % SECRET_KEY).json()

    logger.info("number of api request data: {}".format(data['TbPharmacyOperateInfo']['list_total_count']))

    return data['TbPharmacyOperateInfo']['list_total_count']


# 모든 약국 운영시간 데이터 가져와서 저장
def post_pharmacy_hours_list():
    Pharmacy.objects.all().delete()

    pharmacy_hours_end_index = get_pharmacy_hours_total_count()

    for i in range(PHARMACY_HOURS_START_INDEX, pharmacy_hours_end_index, PHARMACY_HOURS_DATA_UNIT):
        start = i
        end = min(i + PHARMACY_HOURS_DATA_UNIT - 1, pharmacy_hours_end_index)

        pharmacies = get_pharmacy_hours_list(start, end)

        for pharmacy in pharmacies:
            pharmacy_save(pharmacy)


# 부분 약국 운영시간 데이터 가져오기
def get_pharmacy_hours_list(start_index, end_index):
    data = requests.get(PHARMACY_HOURS_API_URL % (SECRET_KEY, start_index, end_index)).json()

    check_err(data['TbPharmacyOperateInfo']['RESULT']['CODE'])

    return data['TbPharmacyOperateInfo']['row']


# 약국 저장
def pharmacy_save(data):
    address = data['DUTYADDR'].split(' ', maxsplit=2)
    si = address[0]
    gu = address[1]
    road_name_address = address[2]
    pharmacy = Pharmacy(
        name=data['DUTYNAME'],
        si=si,
        gu=gu,
        road_name_address=road_name_address,
        main_number=data['DUTYTEL1'],
        latitude=data['WGS84LAT'],
        longitude=data['WGS84LON'],
        mon_open_time=convert_to_datetime(data['DUTYTIME1S']),
        tue_open_time=convert_to_datetime(data['DUTYTIME2S']),
        wed_open_time=convert_to_datetime(data['DUTYTIME3S']),
        thu_open_time=convert_to_datetime(data['DUTYTIME4S']),
        fri_open_time=convert_to_datetime(data['DUTYTIME5S']),
        sat_open_time=convert_to_datetime(data['DUTYTIME6S']),
        sun_open_time=convert_to_datetime(data['DUTYTIME7S']),
        holiday_open_time=convert_to_datetime(data['DUTYTIME8S']),
        mon_close_time=convert_to_datetime(data['DUTYTIME1C']),
        tue_close_time=convert_to_datetime(data['DUTYTIME2C']),
        wed_close_time=convert_to_datetime(data['DUTYTIME3C']),
        thu_close_time=convert_to_datetime(data['DUTYTIME4C']),
        fri_close_time=convert_to_datetime(data['DUTYTIME5C']),
        sat_close_time=convert_to_datetime(data['DUTYTIME6C']),
        sun_close_time=convert_to_datetime(data['DUTYTIME7C']),
        holiday_close_time=convert_to_datetime(data['DUTYTIME8C']),
        last_modified=datetime.strptime(data['WORK_DTTM'], "%Y-%m-%d %H:%M:%S.%f")
    )
    pharmacy.save()


def convert_to_datetime(time_str):
    if time_str == "":
        return None

    hour = int(time_str[0:2])
    minute = int(time_str[2:4])

    if hour >= 24:
        hour = hour - 24

    return time(hour=hour, minute=minute)


def check_err(code):
    logger.info("api status code : {0}".format(code))

    if code == "INFO-200":
        raise ApiNotFoundException
    if code == "ERROR-500":
        raise ApiInternalServerError
    if code == "INFO-100":
        raise ApiKeyForbidden
