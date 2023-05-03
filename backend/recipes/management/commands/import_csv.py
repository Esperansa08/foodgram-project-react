import logging
from csv import DictReader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

MESSAGE = 'Данные успешно загружены в таблицу'
SUCCESS_MESSAGE = 'Все данные успешно загружены'


logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='a')


class Command(BaseCommand):
    help = 'Команда для создания БД на основе имеющихся csv файлов'

    def ingredient_create(row):
        Ingredient.objects.create(
            name=row['name'],
            measurement_unit=row['measurement_unit'])

    ACTIONS = [
        (ingredient_create, Ingredient, 'ingredients.csv'),
    ]

    def handle(self, *args, **options):
        logging.info('Загрузка данных из csv в базу:')
        for func, model, file in self.ACTIONS:
            if model.objects.exists():
                logging.info('Таблица уже содержит данные.')
            for row in DictReader(
                open(
                    f'{file}',
                    encoding='utf8'),
                fieldnames=[
                    'name',
                    'measurement_unit']):
                try:
                    func(row)
                except BaseException:
                    print(f'Не залилось! {row}')
                    logging.exception("message")
            logging.info(MESSAGE)
        logging.info(SUCCESS_MESSAGE)
