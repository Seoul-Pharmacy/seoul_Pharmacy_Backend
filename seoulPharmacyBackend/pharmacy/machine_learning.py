import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from haversine import haversine


# 사용자의 위도, 경도를 통해 datas에서 사용자와 가장 가까운 약국의 정보를 가진 딕셔너리 5개와 해당 딕셔너리에 거리를 추가하여 return.
def filter_by_location(data, user_latitude, user_longitude):
    filtered_longitude = []
    filtered_latitude = []
    datas_results = []

    for i in range(len(data)):
        filtered_longitude.append(float(data[i]['longitude']))
        filtered_latitude.append(float(data[i]['latitude']))
    filtered_longitude_array = np.array(filtered_longitude)
    filtered_latitude_array = np.array(filtered_latitude)

    kn = KNeighborsRegressor()

    kn.fit(filtered_latitude_array.reshape(-1, 1), filtered_longitude_array.reshape(-1, 1))
    distances, indexes = kn.kneighbors([user_latitude])

    for i in indexes[0]:
        datas_results.append(data[i])

    for i in indexes[0]:
        data[i]["distance"] = (str(haversine((float(user_latitude[0]), float(user_longitude[0])),
                                             (float(data[i]['latitude']), float(data[i]['longitude'])))) + "km")

    return datas_results


datas = [
    {
        "id": 133780,
        "name": "행복한미래약국",
        "si": "서울특별시",
        "gu": "강남구",
        "road_name_address": "언주로 707, 2층 일부호 (논현동)",
        "main_number": "02-515-3800",
        "latitude": "37.51622313914720000000",
        "longitude": "127.03501084882800000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "07:30:00",
        "tue_open_time": "07:30:00",
        "wed_open_time": "07:30:00",
        "thu_open_time": "07:30:00",
        "fri_open_time": "07:30:00",
        "sat_open_time": "07:30:00",
        "sun_open_time": "07:30:00",
        "holiday_open_time": "13:00:00",
        "mon_close_time": "19:00:00",
        "tue_close_time": "19:00:00",
        "wed_close_time": "19:00:00",
        "thu_close_time": "19:00:00",
        "fri_close_time": "19:00:00",
        "sat_close_time": "17:00:00",
        "sun_close_time": "12:00:00",
        "holiday_close_time": "18:00:00",
        "last_modified": "2024-04-16"
    },
    {
        "id": 133781,
        "name": "행복한수약국",
        "si": "서울특별시",
        "gu": "강남구",
        "road_name_address": "강남대로 446",
        "main_number": "02-558-7430",
        "latitude": "37.50238919965600000000",
        "longitude": "127.02594709144100000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "09:30:00",
        "tue_open_time": "09:30:00",
        "wed_open_time": "09:30:00",
        "thu_open_time": "09:30:00",
        "fri_open_time": "09:30:00",
        "sat_open_time": "09:30:00",
        "sun_open_time": "07:30:00",
        "holiday_open_time": "13:00:00",
        "mon_close_time": "21:30:00",
        "tue_close_time": "21:30:00",
        "wed_close_time": "21:30:00",
        "thu_close_time": "21:30:00",
        "fri_close_time": "21:30:00",
        "sat_close_time": "18:30:00",
        "sun_close_time": "12:00:00",
        "holiday_close_time": "18:00:00",
        "last_modified": "2024-04-16"
    },
    {
        "id": 133782,
        "name": "행복한수약국",
        "si": "서울특별시",
        "gu": "영등포구",
        "road_name_address": "영중로2길 1 1층 (영등포동3가)",
        "main_number": "02-2672-2340",
        "latitude": "37.51688470845980000000",
        "longitude": "126.90681126953900000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "09:00:00",
        "tue_open_time": "09:00:00",
        "wed_open_time": "09:00:00",
        "thu_open_time": "09:00:00",
        "fri_open_time": "09:00:00",
        "sat_open_time": "09:00:00",
        "sun_open_time": "07:30:00",
        "holiday_open_time": "13:00:00",
        "mon_close_time": "21:00:00",
        "tue_close_time": "21:00:00",
        "wed_close_time": "21:00:00",
        "thu_close_time": "21:00:00",
        "fri_close_time": "19:30:00",
        "sat_close_time": "16:00:00",
        "sun_close_time": "12:00:00",
        "holiday_close_time": "18:00:00",
        "last_modified": "2024-04-16"
    },
    {
        "id": 133784,
        "name": "뉴우리약국",
        "si": "서울특별시",
        "gu": "광진구",
        "road_name_address": "아차산로 237, 삼진빌딩 5층 (화양동)",
        "main_number": "02-2205-3366",
        "latitude": "37.54049819865800000000",
        "longitude": "127.06974612386215000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "09:00:00",
        "tue_open_time": "09:00:00",
        "wed_open_time": "09:00:00",
        "thu_open_time": "09:00:00",
        "fri_open_time": "09:00:00",
        "sat_open_time": "09:00:00",
        "sun_open_time": "09:00:00",
        "holiday_open_time": "09:30:00",
        "mon_close_time": "19:00:00",
        "tue_close_time": "19:00:00",
        "wed_close_time": "19:00:00",
        "thu_close_time": "19:00:00",
        "fri_close_time": "19:00:00",
        "sat_close_time": "15:00:00",
        "sun_close_time": "21:30:00",
        "holiday_close_time": "20:30:00",
        "last_modified": "2024-04-16"
    },
    {
        "id": 133785,
        "name": "행복한약국",
        "si": "서울특별시",
        "gu": "영등포구",
        "road_name_address": "경인로 775",
        "main_number": "02-554-7455",
        "latitude": "37.51474642450430000000",
        "longitude": "126.89753683572700000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "08:30:00",
        "tue_open_time": "08:30:00",
        "wed_open_time": "08:30:00",
        "thu_open_time": "08:30:00",
        "fri_open_time": "08:30:00",
        "sat_open_time": "08:30:00",
        "sun_open_time": "09:00:00",
        "holiday_open_time": "13:00:00",
        "mon_close_time": "19:30:00",
        "tue_close_time": "19:30:00",
        "wed_close_time": "19:30:00",
        "thu_close_time": "19:30:00",
        "fri_close_time": "19:30:00",
        "sat_close_time": "13:30:00",
        "sun_close_time": "18:00:00",
        "holiday_close_time": "18:00:00",
        "last_modified": "2024-04-16"
    },
    {
        "id": 133786,
        "name": "행복한약국",
        "si": "서울특별시",
        "gu": "강남구",
        "road_name_address": "테헤란로 222, 도원빌딩 지하1층 일부 (역삼동)",
        "main_number": "02-3453-6795",
        "latitude": "37.50165808386610000000",
        "longitude": "127.04076575090200000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "09:40:00",
        "tue_open_time": "09:40:00",
        "wed_open_time": "09:40:00",
        "thu_open_time": "09:40:00",
        "fri_open_time": "09:40:00",
        "sat_open_time": "09:40:00",
        "sun_open_time": "09:00:00",
        "holiday_open_time": "13:00:00",
        "mon_close_time": "20:00:00",
        "tue_close_time": "18:30:00",
        "wed_close_time": "18:30:00",
        "thu_close_time": "20:00:00",
        "fri_close_time": "18:30:00",
        "sat_close_time": "15:00:00",
        "sun_close_time": "18:00:00",
        "holiday_close_time": "18:00:00",
        "last_modified": "2024-04-16"
    },
    {
        "id": 133787,
        "name": "행복한약국",
        "si": "서울특별시",
        "gu": "마포구",
        "road_name_address": "신촌로 270, 308호 (아현동, 수창빌딩)",
        "main_number": "02-393-1137",
        "latitude": "37.55712130016080000000",
        "longitude": "126.95571065354100000000",
        "speaking_english": False,
        "speaking_japanese": False,
        "speaking_chinese": False,
        "mon_open_time": "09:00:00",
        "tue_open_time": "09:00:00",
        "wed_open_time": "09:00:00",
        "thu_open_time": "09:00:00",
        "fri_open_time": "09:00:00",
        "sat_open_time": "09:00:00",
        "sun_open_time": "09:00:00",
        "holiday_open_time": "13:00:00",
        "mon_close_time": "20:30:00",
        "tue_close_time": "19:30:00",
        "wed_close_time": "19:30:00",
        "thu_close_time": "20:00:00",
        "fri_close_time": "20:30:00",
        "sat_close_time": "15:00:00",
        "sun_close_time": "18:00:00",
        "holiday_close_time": "18:00:00",
        "last_modified": "2024-04-16"
    }
]

print(filter_by_location(datas, "37.4", "127.846"))