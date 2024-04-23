import logging

import xmltodict
from SPARQLWrapper import SPARQLWrapper, XML
from django.core.exceptions import MultipleObjectsReturned

from pharmacy.models import Pharmacy

logger = logging.getLogger('django')

PHARMACY_LANGUAGE_API_URL = "http://lod.seoul.go.kr/sparql"

COUNT_STATE = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <http://schema.org/>
PREFIX juso: <http://rdfs.co/juso/>
PREFIX jusokr: <http://rdfs.co/juso/kr/>
PREFIX seoul: <http://lod.seoul.go.kr/ontology/>

SELECT (COUNT(*) AS ?count)
WHERE {
  ?pharmacy rdf:type schema:Pharmacy .
  ?pharmacy rdfs:label ?name .
  FILTER (lang(?name) = "ko")
  ?pharmacy juso:address ?juso .
  ?pharmacy seoul:language ?language_uri .
  ?language_uri rdfs:label ?language .
  ?juso jusokr:si_gun_gu <http://lod.seoul.go.kr/resource/AdministrativeDivision/%s> .
  <http://lod.seoul.go.kr/resource/AdministrativeDivision/%s> rdfs:label ?gu .
  FILTER (lang(?gu) = "ko")
}
"""

STATE = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <http://schema.org/>
PREFIX juso: <http://rdfs.co/juso/>
PREFIX jusokr: <http://rdfs.co/juso/kr/>
PREFIX seoul: <http://lod.seoul.go.kr/ontology/>

SELECT ?name ?language ?gu
WHERE {
  ?pharmacy rdf:type schema:Pharmacy .
  ?pharmacy rdfs:label ?name .
  FILTER (lang(?name) = "ko")
  ?pharmacy juso:address ?juso .
  ?pharmacy seoul:language ?language_uri .
  ?language_uri rdfs:label ?language .
  ?juso jusokr:si_gun_gu <http://lod.seoul.go.kr/resource/AdministrativeDivision/%s> .
  <http://lod.seoul.go.kr/resource/AdministrativeDivision/%s> rdfs:label ?gu .
  FILTER (lang(?gu) = "ko")
} OFFSET %d LIMIT %d 
"""

GU_LIST = ["Gangdonggu", "Songpagu", "Gangnamgu", "Seochogu", "Gwanakgu", "Dongjakgu", "Yeongdeungpogu", "Geumcheongu", "Gurogu", "Gangseogu", "Yangcheongu", "Mapogu", "Seodaemungu", "Eunpyeonggu", "Nowongu", "Dobonggu", "Gangbukgu", "Seongbukgu", "Jungranggu", "Dongdaemungu", "Gwangjingu", "Seongdonggu", "Yongsangu", "Junggu", "Jongrogu"]

PHARMACY_LANGUAGE_START_INDEX = 0
PHARMACY_LANGUAGE_DATA_UNIT = 100


# API에 요청하여 데이터 개수를 가져오는 함수
def get_sparql_data(url, state) -> dict:
    sparql = SPARQLWrapper(url)
    sparql.setQuery(state)
    sparql.setReturnFormat(XML)
    results = sparql.query().convert()

    return xmltodict.parse(results.toxml())


# 응답에서 count정보만 가져오는 함수
def extract_total_count(data: dict) -> int:
    return int(data['sparql']['results']['result']['binding']['literal']['#text'])


# 전체 Gu에 대해 API에 요청 및 저장
def update_pharmacy_languages_about_all_gu():
    for gu in GU_LIST:
        update_pharmacy_languages(gu)


# API에 요청하여 응답을 기존 데이터에 저장하는 함수
def update_pharmacy_languages(gu):
    pharmacy_hours_end_index = extract_total_count(get_sparql_data(PHARMACY_LANGUAGE_API_URL, COUNT_STATE % (gu,gu)))

    logger.info("pharmacy_languages api {0}의 총 데이터 개수 : {1}".format(gu, pharmacy_hours_end_index))

    for i in range(PHARMACY_LANGUAGE_START_INDEX, pharmacy_hours_end_index, PHARMACY_LANGUAGE_DATA_UNIT):
        offset = i
        limit = min(PHARMACY_LANGUAGE_DATA_UNIT, pharmacy_hours_end_index - i)

        pharmacy_languages_list = extract_pharmacy_languages(
            get_sparql_data(PHARMACY_LANGUAGE_API_URL, STATE % (gu, gu, offset, limit)))

        for pharmacy_languages in pharmacy_languages_list:
            update_pharmacy_language(pharmacy_languages)


# API 응답에서 URI와 전화번호를 추출하는 함수
def extract_pharmacy_languages(data: dict) -> list:

    # logger.info("api로 부터 온 데이터 : {}".format(data))

    result = []

    for entry in data['sparql']['results']['result']:
        entry_dict = {}
        for item in entry['binding']:
            if item['@name'] == 'name':
                entry_dict[item['@name']] = item['literal']['#text']
            elif item['@name'] == 'language':
                entry_dict['language'] = item['literal']['#text']
            elif item['@name'] == 'gu':
                entry_dict['gu'] = item['literal']['#text']

        result.append(entry_dict)
    return result


# API 응답에서 uri 정보중 언어정보만 가져오는 함수
def extract_language_name(uri):
    # "Language/" 다음의 문자열을 추출
    index = uri.rfind('/')
    if index != -1:
        return uri[index + 1:]


# 언어 정보를 db에 저장
def update_pharmacy_language(pharmacy_languages):
    name = pharmacy_languages["name"]
    language = pharmacy_languages["language"]
    address = pharmacy_languages["gu"]

    # logger.info("update date : ({}, {}, {})".format(road_name_address, name, language))

    try:
        pharmacy = Pharmacy.objects.get(gu__contains=address, name=name)

        if language == "영어":
            pharmacy.speaking_english = True
        elif language == "일어":
            pharmacy.speaking_japanese = True
        elif language == "중국어":
            pharmacy.speaking_chinese = True

        pharmacy.save()
    except Pharmacy.DoesNotExist:
        logger.error("{0}({1})에 대한 데이터가 없습니다.".format(name, address))
    except MultipleObjectsReturned as e:
        logger.error("{0}({1})에 대한 데이터가 여러개 있습니다. : {2}".format(name, address, e))
    except Exception as e:
        logger.error("{0}({1})'s Error : {2}".format(name, address, e))
