import logging

import numpy as np
from haversine import haversine
from sklearn.neighbors import KNeighborsClassifier

logger = logging.getLogger('django')


# datas, 유저의 위도&경도-> datas 내에서 사용자와 가까운 약국이 있는 5개의 딕셔너리와 해당 딕셔너리에 약국과의 거리를 추가하여 return.
def filter_by_location(datas, user_latitude, user_longitude):
    logger.info("machine_learning.filter_by_location()")

    filtered_longitude = []
    filtered_latitude = []
    datas_results = []

    for i in range(len(datas)):
        filtered_longitude.append(float(datas[i]['longitude']))
        filtered_latitude.append(float(datas[i]['latitude']))

    lat_lon_zip = [[lat, lon] for lat, lon in zip(filtered_latitude, filtered_longitude)]
    fake = np.zeros(len(datas))

    if (len(datas)) > 4:

        kn = KNeighborsClassifier()

        mean = np.mean(lat_lon_zip, axis=0)
        std = np.std(lat_lon_zip, axis=0)

        lat_lon_zip = (lat_lon_zip - mean) / std
        new = ([user_latitude, user_longitude] - mean) / std

        kn.fit(lat_lon_zip, fake)
        distances, indexes = kn.kneighbors([new])

    elif (len(datas)) < 5:
        kn = KNeighborsClassifier(n_neighbors=len(datas))

        kn.fit(lat_lon_zip, fake)
        distances, indexes = kn.kneighbors([[user_latitude, user_longitude]])

    for i in indexes[0]:
        datas[i]["distance"] = convertKmToMeter(haversine((float(user_latitude), float(user_longitude)), (
            float(datas[i]['latitude']), float(datas[i]['longitude']))))

    for i in indexes[0]:
        datas_results.append(datas[i])

    return datas_results


def is_less_than_1km(distance: float) -> bool:
    if distance < 1:
        return True
    return False


def convertKmToMeter(distance):
    if is_less_than_1km(distance):
        return "{}{}".format(str(round(distance * 1000, 2)), "m")
    return "{}{}".format(str(round(distance, 2)), "km")
