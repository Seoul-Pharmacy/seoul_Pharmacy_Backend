import logging

import pandas as pd
from numpy import nan

from pharmacy.models import Pharmacy

logger = logging.getLogger('django')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

filename = 'static/excel/외국어 가능 약국 현황.xlsx'


def update_pharmacy_languages():
    df = pd.read_excel(filename, skiprows=3, usecols='C,D,E,F,G,H')
    # 엑셀의 nan값을 ''로 변경
    df = df.fillna('')

    for index, row in df.iterrows():
        speaking_english = make_speaking_language(row['영어'])
        speaking_chinese = make_speaking_language(row['중국어'])
        speaking_japanese = make_speaking_language(row['일본어'])
        main_number = row['Unnamed: 4']

        try:
            pharmacy = Pharmacy.objects.get(main_number=main_number)
            pharmacy.speaking_english = speaking_english
            pharmacy.speaking_chinese = speaking_chinese
            pharmacy.speaking_japanese = speaking_japanese
            pharmacy.save()
        except Pharmacy.DoesNotExist:
            logger.info("{0}({1}, {2})에 대한 데이터가 없습니다.".format(row["Unnamed: 2"], main_number, row["Unnamed: 3"]))
        except Exception as e:
            logger.info("Error : {0}".format(e))


def make_speaking_language(data):
    if data == "":
        return False
    return True
