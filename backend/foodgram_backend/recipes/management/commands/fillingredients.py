import logging
import sys
from csv import reader

from django.core.management.base import BaseCommand, CommandParser
from recipes.models import Ingredient, MeasurementUnit

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(filename)s/%(funcName)s %(message)s'
)
logger.addHandler(handler)
handler.setFormatter(formatter)


def clear_table(table):
    table.objects.all().delete()
    logger.debug(f'Таблица {table.__name__} очищена.')


class Command(BaseCommand):
    help = 'Используйте эту команду для заполнения таблицы с ингридиентами.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('-c', '--clear', action='store_true')

    def handle(self, *args, **options):
        logger.debug('Начинаем импорт...')
        if options.get('clear'):
            logger.debug('Очищаем таблицы.')
            clear_table(Ingredient)
            clear_table(MeasurementUnit)

        csv_file_path = './data/ingredients.csv'
        with open(csv_file_path, newline='') as csvfile:
            spamreader = reader(csvfile, delimiter=',')
            list_ingredients = []
            i = 0
            for row in spamreader:
                try:
                    i += 1
                    measurement_unit, _ = (
                        MeasurementUnit.objects.get_or_create(
                            unit_name=row[1]))
                    list_ingredients.append(
                        Ingredient(name=row[0],
                                   measurement_unit=measurement_unit))
                except IndexError as error:
                    logger.error(exc_info=error)
                    continue
            logger.debug('Список ингридиентов создан.')
            Ingredient.objects.bulk_create(list_ingredients)
            logger.debug('Ингридиенты успешно добавлены.')
