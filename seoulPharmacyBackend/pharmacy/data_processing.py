
from venv import logger

from pharmacy.serializers import PharmacySerializer


# local로 약국 저장하기, 입력으로 dictionary를 받는다.
# 필요한 필드는 models.py의 pharmacy에서 id를 제외한 모든 필드
def pharmacy_save_by_local(data):
    serializer = PharmacySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        logger.info("save successfully")
        return
    logger.error("save fail")