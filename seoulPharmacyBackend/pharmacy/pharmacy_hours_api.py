import logging
from datetime import time, datetime

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
    data = requests.get(SIMPLE_PHARMACY_HOURS_API_URL % SECRET_KEY).json()

    check_err(data)

    total_count = data['TbPharmacyOperateInfo']['list_total_count']

    logger.info("number of api request data: {}".format(total_count))

    return total_count


# 모든 약국 운영시간 데이터 가져와서 저장
def update_pharmacy_hours_list():
    pharmacy_hours_end_index = get_pharmacy_hours_total_count()

    Pharmacy.objects.all().delete()

    for i in range(PHARMACY_HOURS_START_INDEX, pharmacy_hours_end_index, PHARMACY_HOURS_DATA_UNIT):
        start = i
        end = min(i + PHARMACY_HOURS_DATA_UNIT - 1, pharmacy_hours_end_index)

        pharmacies = get_pharmacy_hours_list(start, end)

        for pharmacy in pharmacies:
            pharmacy_save(pharmacy)


# 부분 약국 운영시간 데이터 가져오기
def get_pharmacy_hours_list(start_index: int, end_index: int) -> dict:
    data = requests.get(PHARMACY_HOURS_API_URL % (SECRET_KEY, start_index, end_index)).json()

    check_err(data)

    return data['TbPharmacyOperateInfo']['row']


# 약국 저장
def pharmacy_save(data: dict):
    address = data['DUTYADDR'].split(' ', maxsplit=2)
    si = address[0]
    gu = address[1]
    road_name_address = address[2]

    try:
        pharmacy = Pharmacy(
            name=data['DUTYNAME'],
            si=si,
            gu=gu,
            road_name_address=road_name_address,
            main_number=data['DUTYTEL1'],
            latitude=data['WGS84LAT'],
            longitude=data['WGS84LON'],
            mon_open_time=convert_to_time(data['DUTYTIME1S']),
            tue_open_time=convert_to_time(data['DUTYTIME2S']),
            wed_open_time=convert_to_time(data['DUTYTIME3S']),
            thu_open_time=convert_to_time(data['DUTYTIME4S']),
            fri_open_time=convert_to_time(data['DUTYTIME5S']),
            sat_open_time=convert_to_time(data['DUTYTIME6S']),
            sun_open_time=convert_to_time(data['DUTYTIME7S']),
            holiday_open_time=convert_to_time(data['DUTYTIME8S']),
            mon_close_time=convert_to_time(data['DUTYTIME1C']),
            tue_close_time=convert_to_time(data['DUTYTIME2C']),
            wed_close_time=convert_to_time(data['DUTYTIME3C']),
            thu_close_time=convert_to_time(data['DUTYTIME4C']),
            fri_close_time=convert_to_time(data['DUTYTIME5C']),
            sat_close_time=convert_to_time(data['DUTYTIME6C']),
            sun_close_time=convert_to_time(data['DUTYTIME7C']),
            holiday_close_time=convert_to_time(data['DUTYTIME8C']),
            last_modified=datetime.strptime(data['WORK_DTTM'], "%Y-%m-%d %H:%M:%S.%f")
        )
        pharmacy.save()

    except ValueError as e:
        logger.error("{0}({1})'s error: {2}".format(data['DUTYNAME'], gu, e))
    except TypeError as e:
        logger.error("{0}({1})'s error : {2}".format(data['DUTYNAME'], gu, e))
    except IntegrityError as e:
        logger.error("{0}({1})'s error : {2}".format(data['DUTYNAME'], gu, e))
    except Exception as e:
        logger.error("{0}({1})'s error : {2}".format(data['DUTYNAME'], gu, e))


def convert_to_time(time_str: str):
    try:
        if time_str == "":
            return None

        if len(time_str) < 4:
            time_str = time_str.zfill(4)

        hour = int(time_str[0:2])
        minute = int(time_str[2:4])

        if hour >= 24:
            hour = hour - 24

        return time(hour=hour, minute=minute)
    except ValueError as e:
        raise ValueError(time_str)
    except TypeError as e:
        raise TypeError(time_str)
    except Exception as e:
        raise Exception(time_str)


def check_err(data: dict):
    code = data['TbPharmacyOperateInfo']['RESULT']['CODE']

    logger.info("api status code : {0}".format(code))
    if code == "INFO-000":
        return
    elif code == "INFO-100":
        raise ApiKeyForbidden
    elif code == "INFO-200":
        raise ApiNotFound
    elif code == "ERROR-300":
        raise ApiBadRequest
    else:
        raise ApiInternalServerError
