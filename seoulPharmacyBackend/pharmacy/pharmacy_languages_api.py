import logging

import xmltodict
from SPARQLWrapper import SPARQLWrapper, XML

from pharmacy.models import Pharmacy

logger = logging.getLogger('django')

PHARMACY_LANGUAGE_API_URL = "http://lod.seoul.go.kr/sparql"

COUNT_STATE = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX seoul: <http://lod.seoul.go.kr/ontology/>
PREFIX schema: <http://schema.org/>

SELECT (COUNT(*) AS ?count)
WHERE {
    ?pharmacy rdf:type schema:Pharmacy .
    ?pharmacy rdfs:label ?name .
    FILTER ( lang(?name) = "ko" )
    ?pharmacy seoul:language ?language .
    ?pharmacy schema:telephone ?tel .
}
"""

STATE = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX seoul: <http://lod.seoul.go.kr/ontology/>
PREFIX schema: <http://schema.org/>

SELECT *
WHERE { 
    ?pharmacy rdf:type schema:Pharmacy . 
    ?pharmacy rdfs:label ?name . 
    FILTER ( lang(?name) = "ko" )
    ?pharmacy seoul:language ?language .
    ?pharmacy schema:telephone ?tel .
} OFFSET %d LIMIT %d
"""

PHARMACY_LANGUAGE_START_INDEX = 0
PHARMACY_LANGUAGE_DATA_UNIT = 100


# API에 요청하여 데이터 개수를 가져오는 함수
def get_pharmacy_languages_total_count() -> dict:
    sparql = SPARQLWrapper(PHARMACY_LANGUAGE_API_URL)

    sparql.setQuery(COUNT_STATE)
    sparql.setReturnFormat(XML)
    results = sparql.query().convert()
    return xmltodict.parse(results.toxml())


def extract_total_count(data: dict) -> int:
    return int(data['sparql']['results']['result']['binding']['literal']['#text'])


# API에 요청하여 응답을 기존 데이터에 저장하는 함수
def update_pharmacy_languages():
    pharmacy_hours_end_index = extract_total_count(get_pharmacy_languages_total_count())

    logger.info("pharmacy_languages api의 총 데이터 개수 : {}".format(pharmacy_hours_end_index))

    for i in range(PHARMACY_LANGUAGE_START_INDEX, pharmacy_hours_end_index, PHARMACY_LANGUAGE_DATA_UNIT):
        offset = i
        limit = min(PHARMACY_LANGUAGE_DATA_UNIT, pharmacy_hours_end_index - i)

        language_and_tel_list = extract_language_and_tel(get_pharmacy_languages_list(offset, limit))

        for language_and_tel in language_and_tel_list:
            update_pharmacy_language(language_and_tel['name'], language_and_tel['language'], language_and_tel['tel'])


# API에 요청하여 데이터를 offset부터 limit 개수 만큼 가져오는 함수
def get_pharmacy_languages_list(offset: int, limit: int) -> dict:
    sparql = SPARQLWrapper(PHARMACY_LANGUAGE_API_URL)

    sparql.setQuery(STATE%(offset, limit))
    sparql.setReturnFormat(XML)
    results = sparql.query().convert()
    return xmltodict.parse(results.toxml())


# API 응답에서 URI와 전화번호를 추출하는 함수
def extract_language_and_tel(data: dict) -> list:
    result = []

    for entry in data['sparql']['results']['result']:
        entry_dict = {}
        for item in entry['binding']:
            if item['@name'] == 'name':
                entry_dict[item['@name']] = item['literal']['#text']
            elif item['@name'] == 'language':
                entry_dict[item['@name']] = extract_language_name(item['uri'])
            elif item['@name'] == 'tel':
                entry_dict[item['@name']] = item['literal']
        result.append(entry_dict)
    return result


# API 응답에서 uri 정보중 언어정보만 가져오는 함수
def extract_language_name(uri):
    # "Language/" 다음의 문자열을 추출
    index = uri.rfind('/')
    if index != -1:
        return uri[index + 1:]


# 언어 정보를 db에 저장
def update_pharmacy_language(name, language, main_number):
    try:
        pharmacy = Pharmacy.objects.get(main_number__contains=main_number)

        if language == "영어":
            pharmacy.speaking_english = True
        elif language == "일어":
            pharmacy.speaking_chinese = True
        elif language == "중국어":
            pharmacy.speaking_japanese = True

        pharmacy.save()
    except Pharmacy.DoesNotExist:
        logger.error("{0}({1})에 대한 데이터가 없습니다.".format(name, main_number))
    except Exception as e:
        logger.error("Error : {0}".format(e))
