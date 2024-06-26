import json
import logging

import requests

from common import my_settings

HOLIDAY_API_URL = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'
SECRET_KEY = my_settings.DATA_SECRET_KEY

logger = logging.getLogger('django')


def is_holiday(year, month, day) -> bool:
    logger.info("holiday_api.is_holiday()")

    date = int("{0}{1:02d}{2:02d}".format(year, month, day))

    params = {'serviceKey': SECRET_KEY, 'numOfRows': '100', '_type': 'json', 'solYear': year}

    response = requests.get(HOLIDAY_API_URL, params=params)
    result = json.loads(response.text)

    for i in range(len(result['response']['body']['items']['item'])):
        holiday = result['response']['body']['items']['item'][i]['locdate']
        if holiday == date:
            return True

    return False
