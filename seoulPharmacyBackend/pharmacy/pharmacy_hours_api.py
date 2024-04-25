import logging
from datetime import datetime

import requests
from django.db import IntegrityError

from common import my_settings
from common.exceptions import ApiNotFound, ApiInternalServerError, ApiKeyForbidden, ApiBadRequest
from pharmacy.models import Pharmacy

logger = logging.getLogger('django')

SECRET_KEY = my_settings.SEOUL_API_SECRET_KEY
PHARMACY_HOURS_API_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/%d/%d/"
SIMPLE_PHARMACY_HOURS_API_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/1/1/"
PHARMACY_HOURS_START_INDEX = 1
PHARMACY_HOURS_DATA_UNIT = 1000


# 약국 운영시간 데이터 개수 가져오기
def get_pharmacy_hours_total_count() -> int:
    logger.info("phamacy_hours_api.get_pharmacy_hours_total_count()")
    data = requests.get(SIMPLE_PHARMACY_HOURS_API_URL % SECRET_KEY).json()

    check_statuscode(data['TbPharmacyOperateInfo']['RESULT']['CODE'])

    total_count = data['TbPharmacyOperateInfo']['list_total_count']

    return total_count


# 모든 약국 운영시간 데이터 가져와서 저장
def update_pharmacy_hours_list():
    pharmacy_hours_end_index = get_pharmacy_hours_total_count()
    logger.debug("pharmacy_hours_api.update_pharmacy_hours_list() : data 개수 : {0}".format(pharmacy_hours_end_index))

    Pharmacy.objects.all().delete()

    for i in range(PHARMACY_HOURS_START_INDEX, pharmacy_hours_end_index, PHARMACY_HOURS_DATA_UNIT):
        start = i
        end = min(i + PHARMACY_HOURS_DATA_UNIT - 1, pharmacy_hours_end_index)

        pharmacies = get_pharmacy_hours_list(start, end)

        for pharmacy in pharmacies:
            pharmacy_save(pharmacy)


# 부분 약국 운영시간 데이터 가져오기
def get_pharmacy_hours_list(start_index: int, end_index: int) -> dict:
    logger.info("pharmacy_hours_api.get_pharmacy_hours_list()")
    data = requests.get(PHARMACY_HOURS_API_URL % (SECRET_KEY, start_index, end_index)).json()

    check_statuscode(data)

    return data['TbPharmacyOperateInfo']['row']


# 약국 저장
def pharmacy_save(data: dict):
    address = data['DUTYADDR'].split(' ', maxsplit=2)
    si = address[0]
    gu = address[1]
    road_name_address = address[2]

    logger.info("pharmacy_hours_api.pharmacy_save() : (address : {0})".format(data["DUTYADDR"]))

    try:
        pharmacy = Pharmacy(
            name=data['DUTYNAME'],
            si=si,
            gu=gu,
            road_name_address=road_name_address,
            main_number=data['DUTYTEL1'],
            latitude=data['WGS84LAT'],
            longitude=data['WGS84LON'],
            mon_open_time=convert_to_open_time(data['DUTYTIME1S']),
            tue_open_time=convert_to_open_time(data['DUTYTIME2S']),
            wed_open_time=convert_to_open_time(data['DUTYTIME3S']),
            thu_open_time=convert_to_open_time(data['DUTYTIME4S']),
            fri_open_time=convert_to_open_time(data['DUTYTIME5S']),
            sat_open_time=convert_to_open_time(data['DUTYTIME6S']),
            sun_open_time=convert_to_open_time(data['DUTYTIME7S']),
            holiday_open_time=convert_to_open_time(data['DUTYTIME8S']),
            mon_close_time=convert_to_close_time(data['DUTYTIME1C']),
            tue_close_time=convert_to_close_time(data['DUTYTIME2C']),
            wed_close_time=convert_to_close_time(data['DUTYTIME3C']),
            thu_close_time=convert_to_close_time(data['DUTYTIME4C']),
            fri_close_time=convert_to_close_time(data['DUTYTIME5C']),
            sat_close_time=convert_to_close_time(data['DUTYTIME6C']),
            sun_close_time=convert_to_close_time(data['DUTYTIME7C']),
            holiday_close_time=convert_to_close_time(data['DUTYTIME8C']),
            last_modified=datetime.strptime(data['WORK_DTTM'], "%Y-%m-%d %H:%M:%S.%f")
        )
        pharmacy.save()

    except IntegrityError as e:
        logger.error("pharmacy_hours_api.pharmacy_save() : {0}({1}) {2}".format(data['DUTYNAME'], gu, e))
    except Exception as e:
        logger.error("pharmacy_hours_api.pharmacy_save() : {0}({1}) {2}".format(data['DUTYNAME'], gu, e))


def convert_to_open_time(time_data: str):
    try:
        if time_data == "":
            return None

        return int(time_data)

    except Exception as e:
        raise Exception(time_data)


def convert_to_close_time(time_data: str):
    try:
        if time_data == "":
            return None

        time_data = int(time_data)

        # 닫는 시간이 오전 6시 이전이면 + 24시를 해준다.
        if time_data < 600:
            time_data += 2400

        return int(time_data)

    except Exception as e:
        raise Exception(time_data)


def check_statuscode(statuscode: str):
    if statuscode == "INFO-000":
        return
    elif statuscode == "INFO-100":
        raise ApiKeyForbidden
    elif statuscode == "INFO-200":
        raise ApiNotFound
    elif statuscode == "ERROR-300":
        raise ApiBadRequest
    else:
        raise ApiInternalServerError
