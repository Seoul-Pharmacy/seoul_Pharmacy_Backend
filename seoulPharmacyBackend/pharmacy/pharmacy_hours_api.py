import logging
from venv import logger
import requests
from config import my_settings

SECRET_KEY = my_settings.SEOUL_API_SECRET_KEY
PHARMACY_HOURS_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/%d/%d/"
SIMPLE_PHARMACY_HOURS_URL = "http://openapi.seoul.go.kr:8088/%s/json/TbPharmacyOperateInfo/1/1/"
PHARMACY_HOURS_START_INDEX = 1
PHARMACY_HOURS_DATA_UNIT = 1000


# 약국 운영시간 데이터 개수 가져오기
def get_pharmacy_hours_total_count():
    data = requests.get(SIMPLE_PHARMACY_HOURS_URL % SECRET_KEY).json()

    logging.warning(data['TbPharmacyOperateInfo']['list_total_count'])
    return data['TbPharmacyOperateInfo']['list_total_count']


# 모든 약국 운영시간 데이터 가져와서 저장
def get_all_pharmacy_hours_list():
    pharmacy_hours_end_index = get_pharmacy_hours_total_count()

    for i in range(PHARMACY_HOURS_START_INDEX, pharmacy_hours_end_index, PHARMACY_HOURS_DATA_UNIT):
        start = i
        end = min(i + PHARMACY_HOURS_DATA_UNIT - 1, pharmacy_hours_end_index)
        get_pharmacy_hours_list(start, end)


# 부분 약국 운영시간 데이터 가져오기
def get_pharmacy_hours_list(start_index, end_index):
    data = requests.get(PHARMACY_HOURS_URL % (SECRET_KEY, start_index, end_index)).json()

    logging.warning(data)
    return data['TbPharmacyOperateInfo']['row']


# get_all_pharmacy_hours_list()


def check_err(code, message):
    if code == "INFO-200":
        logger.error("해당 요청에 대한 결과가 없습니다.")
    if code == "ERROR-500":
        logger.error("서버 오류 입니다.")
    if code == "ERROR-310":
        logger.error("해당하는 서비스가 없습니다.")
    if code == "INFO-100":
        logger.error("인증키가 유효하지 않습니다.")
