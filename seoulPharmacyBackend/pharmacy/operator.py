import logging

from apscheduler.schedulers.background import BackgroundScheduler

from pharmacy.pharmacy_hours_api import update_pharmacy_hours_list
from pharmacy.pharmacy_languages_api import update_pharmacy_languages_about_all_gu

logger = logging.getLogger('django')


def run_apis():
    logger.info("operator.run_apis()")
    update_pharmacy_hours_list()
    update_pharmacy_languages_about_all_gu()


def main():
    sche = BackgroundScheduler(timezone='Asia/Seoul')

    sche.add_job(run_apis, 'cron', day_of_week='mon', hour='6', minute='1', id='run_apis')
    sche.start()


if __name__ == "__main__":
    main()
