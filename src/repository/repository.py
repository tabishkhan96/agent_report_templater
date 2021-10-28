import logging
import os
from copy import deepcopy
from typing import List, Type, BinaryIO, Optional
from fastapi import UploadFile
from fastapi.responses import FileResponse
from dynaconf import settings
from more_itertools import chunked
from pydantic import BaseModel

from src.repository.dao import DocumentDAOInterface
from src.repository.exceptions import DraftDocumentNotFoundException, DocumentTemplateCorruptedException
from src.repository.models import (
    Table, Row, BaseReport, SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport, TransportUnit,
    Container
)
from src.repository.template_engine import TemplateEngine
from src.repository.report_strategies import ReportCreationStrategyInterface, SelfImportReportCreationStrategy


# TODO

# таблицы цветности - после таблиы результатов
# поворот картинок-  альбомная ориентация и растягивание
# как составлять таблицы с паллетами/коробками. отличия для разных типов СО
# логика тальманского отчета. заполнение
# отличия таблиц температуры для разных СО

# picture cropping


# TODO растягивать фото если оно меньше чем ячейка и переворачивать вертикальные
# если разные грузы в контейнере то в заявке будут разные строки


class AgentReportRepository:
    """Репозиторий бизнес-логики приложения"""

    def __init__(self, document_dao: Type[DocumentDAOInterface]):
        self.logger: logging.Logger = logging.getLogger("repository")
        self.document_dao: Type[DocumentDAOInterface] = document_dao
        self.doc_filling_strategies_mapping: dict[Type[BaseModel], Type[ReportCreationStrategyInterface]] = {
            SelfImportReport: SelfImportReportCreationStrategy,
            SelfImportOnAutoReport: ...,
            PickupFromSupplierReport: ...,
        }

    def create_report(self, report: BaseReport) -> FileResponse:
        """
        Метод создания черновика отчета.

        Метод создает черновик и заполняет его заголовок.
        Заполнение остальных данных происходит в соответствующих стратегиях.

        :param report: данные заявки
        :return str: название файла черновика отчета
        """
        doc = self.document_dao(
            path=f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(report).__name__}/header_template.{settings.DOC_TYPE}"
        )
        header: Table = next(doc.get_tables(), None)
        if not header:
            raise DocumentTemplateCorruptedException('Отсутствует таблица-заголовок')

        self.fill_header_table(report, header)
        self.doc_filling_strategies_mapping[type(report)](self.document_dao, report).execute(doc)

        filename: str = f"{report.number}_{report.order}_" \
                        f"{'_'.join((tu.supplier for tu in report.transport_units))}_" \
                        f"{'_'.join(('_'.join(tu.cargo) for tu in report.transport_units))}_" \
                        f"{'_'.join((tu.number for tu in report.transport_units))}".replace('/', '')

        doc.save(f'{settings.REPOSITORY.REPORTS_DIR}/{filename}.{settings.DOC_TYPE}')
        self.logger.info(f'Doc saved to "{settings.REPOSITORY.REPORTS_DIR}/" with name "{filename}".')
        return FileResponse(
            f"{settings.REPOSITORY.REPORTS_DIR}/{filename}.{settings.DOC_TYPE}",
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def fill_header_table(self, report: BaseReport, header_table: Table):
        for unit in report.transport_units:
            unit.cargo_in_english = [
                settings.VEGETABLES.get(cargo.lower()) or settings.FRUITS.get(cargo.lower(), '') for cargo in unit.cargo
            ]
        TemplateEngine.replace_in_table(
            table=header_table, values=report.header, cell_handler=self.document_dao.set_cell_style
        )

    def get_reports(self) -> List[BaseReport]:
        raise NotImplemented

    def add_pictures(self, doc_filename: str, images: List[UploadFile]) -> FileResponse:
        """
        Добавление фотографий к отчету.

        Фотографии добавляются в таблице 2 на 2, по одной таблице на страницу отчета.

        :param doc_filename: имя файла отчета
        :param images: фотографии
        :return FileResponse: файл отчета
        """
        if doc_filename not in os.listdir(settings.REPOSITORY.REPORTS_DIR):
            raise DraftDocumentNotFoundException

        doc = self.document_dao(f'{settings.REPOSITORY.REPORTS_DIR}/{doc_filename}')
        doc.add_section(horizontal=True)

        images = [image.file for image in images]

        for images_chunk in chunked(images, 4):
            photos_table = deepcopy(
                self.document_dao(
                    f"{settings.REPOSITORY.TEMPLATES_DIR}/photos_template.{settings.DOC_TYPE}"
                ).get_tables()[0]
            )
            doc.append_table(photos_table)
            doc.add_page_break()
            photos_table = doc.get_tables()[-1]

            cells = [cell for n in range(2) for cell in photos_table.row_cells(n)]
            for n, image in enumerate(images_chunk):
                doc.insert_picture_into_cell(cells[n], image)

        doc.save(f"{settings.REPOSITORY.REPORTS_DIR}/{doc_filename}")
        return FileResponse(
            f"{settings.REPOSITORY.REPORTS_DIR}/{doc_filename}",
            filename=doc_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
