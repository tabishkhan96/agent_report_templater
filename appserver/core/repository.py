import logging
import os
from copy import deepcopy
from io import BytesIO
from typing import List, Type, Optional, Union
from fastapi import UploadFile
from fastapi.responses import FileResponse
from dynaconf import settings
from more_itertools import chunked
from pydantic import BaseModel
from PIL import Image
from urllib.parse import unquote

from .document_daos import AbstractDocumentDAO, Table
from .exceptions import DraftDocumentNotFoundException, DocumentTemplateCorruptedException
from .models import BaseReport, SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport, Photo
from .report_strategies import ReportCreationBaseStrategy, SelfImportReportCreationStrategy


# TODO

# таблицы цветности - после таблиы результатов
# поворот картинок-  альбомная ориентация и растягивание
# как составлять таблицы с паллетами/коробками. отличия для разных типов СО
# логика тальманского отчета. заполнение
# отличия таблиц температуры для разных СО

# picture cropping


# TODO растягивать фото если оно меньше чем ячейка и переворачивать вертикальные


class AgentReportRepository:
    """Репозиторий бизнес-логики приложения"""

    def __init__(self, document_dao: Type[AbstractDocumentDAO]):
        self.logger: logging.Logger = logging.getLogger("repository")
        self.document_dao: Type[AbstractDocumentDAO] = document_dao
        self.doc_filling_strategies_mapping: dict[Type[BaseModel], Type[ReportCreationBaseStrategy]] = {
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
        self.doc_filling_strategies_mapping[type(report)](self.document_dao, report).execute(doc)

        filename: str = self._build_report_name(report)

        doc.save(f'{settings.REPOSITORY.REPORTS_DIR}/{filename}')
        self.logger.info(f'Doc saved to "{settings.REPOSITORY.REPORTS_DIR}/" with name "{filename}".')
        return FileResponse(
            f"{settings.REPOSITORY.REPORTS_DIR}/{filename}",
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def get_report(self, filename: str) -> Union[List[dict], FileResponse]:
        report_files = os.scandir(settings.REPOSITORY.REPORTS_DIR)
        if not filename:
            return [{'name': file.name,
                     'size': file.stat().st_size,
                     'modified': file.stat().st_mtime} for file in report_files]
        filename = unquote(filename)
        if filename not in (file.name for file in report_files):
            raise DraftDocumentNotFoundException
        return FileResponse(
            f"{settings.REPOSITORY.REPORTS_DIR}/{filename}",
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def update_report(self, filename: str, report_file: UploadFile) -> str:
        filename = unquote(filename)
        if filename not in os.listdir(settings.REPOSITORY.REPORTS_DIR):
            raise DraftDocumentNotFoundException
        with open(f"{settings.REPOSITORY.REPORTS_DIR}/{filename}", "wb") as doc:
            doc.write(report_file.file.read())
        return filename

    def add_pictures(self, report: BaseReport) -> FileResponse:
        """
        Добавление фотографий к отчету.

        Фотографии добавляются в таблице 2 на 2, по одной таблице на страницу отчета.

        :param report:
        :return FileResponse: файл отчета
        """
        doc_filename: str = self._build_report_name(report)
        if doc_filename not in os.listdir(settings.REPOSITORY.REPORTS_DIR):
            raise DraftDocumentNotFoundException(f"Искомое имя: {doc_filename}")

        doc = self.document_dao(f'{settings.REPOSITORY.REPORTS_DIR}/{doc_filename}')
        doc.add_section(horizontal=True)

        photos_table_template: Optional[Table] = next(self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(report).__name__}/photos_template.{settings.DOC_TYPE}"
        ).get_tables(), None)

        if not photos_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы фотографий')

        for transport_unit in report.transport_units:
            doc.append_paragraph(transport_unit.number)
            for images_chunk in chunked(transport_unit.photos, 4):
                photos_table = doc.append_table(deepcopy(photos_table_template))
                self._fill_pictures_table(photos_table, images_chunk)
                doc.add_page_break()

        doc.save(f"{settings.REPOSITORY.REPORTS_DIR}/{doc_filename}")
        return FileResponse(
            f"{settings.REPOSITORY.REPORTS_DIR}/{doc_filename}",
            filename=doc_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def _build_report_name(self, report: BaseReport):
        suppliers: set[str] = {unit.supplier for unit in report.transport_units}
        cargos: set[str] = {cargo for unit in report.transport_units for cargo in unit.cargo}

        filename: str = f"{report.number}_{report.order}_{'_'.join(suppliers)}_{'_'.join(cargos)}_" \
                        f"{'_'.join((tu.number for tu in report.transport_units))}" \
                        f".{settings.DOC_TYPE}"
        return filename.replace('/', '')

    def _fill_pictures_table(self, photos_table: Table, photos: list[Photo]) -> Table:
        images: list[Image] = [Image.open(photo.file).rotate(360 - photo.rotation) for photo in photos if photo.file]
        photo_frame_ratio: float = photos_table.columns[0].width / photos_table.rows[0].height
        map(lambda img: img.resize((image.size[1] * photo_frame_ratio, image.size[1])), images)
        cells = [cell for n in range(2) for cell in photos_table.row_cells(n)]
        for n, image in enumerate(images):
            img_byte_array = BytesIO()
            image.save(img_byte_array, format='PNG')
            self.document_dao.insert_picture_into_cell(cells[n], img_byte_array)
        return photos_table
