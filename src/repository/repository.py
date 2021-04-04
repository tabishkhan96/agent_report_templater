import logging
import os
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Type, List
from fastapi import UploadFile
from fastapi.responses import FileResponse
from dynaconf import settings
from more_itertools import chunked

from src.repository.dao import DocumentDAOInterface
from src.repository.exceptions import DraftDocumentNotFound
from src.repository.models import Application, Header, Table, Row


class AgentReportRepository:
    """Репозиторий бизнес-логики приложения"""

    def __init__(self, document_dao: Type[DocumentDAOInterface]):
        self.logger: logging.Logger = logging.getLogger("repository")
        self.document_dao: Type[DocumentDAOInterface] = document_dao

    def create_report(self, application: Application) -> str:
        """
        Метод создания черновика отчета.

        Черновик состоит из текстовой части-заголовка, который заполняется из заявки, таблицы данных о температуре в
        каждом контейнере, тальманского отчета по каждому контейнеру, таблиц результатов, замера калибров, заключения,
        времени жизни и данных о исполнителе. Также добавляется место под график температурных датчиков (два для каждого
        контейнера)

        :param application: данные заявки
        :return str: хеш созданного черновика
        """
        header_data: Header = Header(
            report_number=application.report_number,
            place=application.place_of_inspection,
            shipper=application.supplier,
            cargo=application.cargo,
            transport_units=application.containers,
            vessel=application.vessel,
            invoice=application.invoice,
            order=application.order,
            BL=application.BL
        )
        doc = self.document_dao(f"{settings.REPOSITORY.TEMPLATES_DIR}/report_template.{settings.DOC_TYPE}")

        cargo_in_english: str = (
                settings.VEGETABLES.get(header_data.cargo.lower(), '') or
                settings.FRUITS.get(header_data.cargo.lower(), '')
        )
        header_data.cargo = f"{header_data.cargo} / {cargo_in_english}"

        header: Table = doc.get_tables()[0]
        # распихиваем данные в заголовок отчета
        for cell, text in zip(header.column_cells(1), header_data.dict().values()):
            if isinstance(text, list):
                text = '\n'.join(text)
            cell.text = text
            doc.set_cell_style(cell)

        temperature_data: Table = doc.get_tables()[1]
        for container in header_data.transport_units:
            row: Row = temperature_data.add_row()
            row.cells[0].text = container
            doc.set_cell_style(row.cells[0])

        doc.add_page_break()

        tally_account_template = self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/tally_account_template.{settings.DOC_TYPE}"
        )
        for container in header_data.transport_units:
            pallet_and_boxes_table = deepcopy(tally_account_template.get_tables()[0])
            pallet_and_boxes_table.column_cells(0)[1].text = container
            doc.set_cell_style(pallet_and_boxes_table.column_cells(0)[1])
            tally_account_table = deepcopy(tally_account_template.get_tables()[1])
            doc.append_table(pallet_and_boxes_table)
            doc.append_table(tally_account_table)
            doc.add_page_break()

        inspection_result_template = self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/inspection_result_template.{settings.DOC_TYPE}"
        )

        results_table = deepcopy(inspection_result_template.get_tables()[0])
        calibre_table = deepcopy(inspection_result_template.get_tables()[1])
        conclusion_table = deepcopy(inspection_result_template.get_tables()[2])
        shelf_life_table = deepcopy(inspection_result_template.get_tables()[3])
        executor_table = deepcopy(inspection_result_template.get_tables()[4])

        results_table.column_cells(0)[3].text = header_data.transport_units[0]
        doc.set_cell_style(results_table.column_cells(0)[3])
        calibre_table.column_cells(0)[1].text = header_data.transport_units[0]
        doc.set_cell_style(calibre_table.column_cells(0)[1])
        shelf_life_table.column_cells(0)[1].text = header_data.transport_units[0]
        doc.set_cell_style(shelf_life_table.column_cells(0)[1])
        executor_table.column_cells(0)[3].text = datetime.today().strftime("%d.%m.%Y")
        doc.set_cell_style(executor_table.column_cells(0)[3])

        for i, container in enumerate(header_data.transport_units[1:]):
            row: Row = results_table.add_row()
            row.cells[0].text = container
            doc.set_cell_style(row.cells[0])

            row: Row = calibre_table.add_row()
            row.cells[0].text = container
            doc.set_cell_style(row.cells[0])

            row: Row = shelf_life_table.add_row()
            row.cells[0].text = container
            doc.set_cell_style(row.cells[0])

        doc.append_table(results_table)
        doc.append_table(calibre_table)
        doc.append_table(conclusion_table)
        doc.append_table(shelf_life_table)
        doc.append_table(executor_table)

        doc.add_page_break()

        for container in header_data.transport_units:
            for _ in range(2):
                paragraph = doc.append_paragraph(f"Контейнер: {container}\nНомер датчика:\n")
                paragraph.runs[0].bold = True
                paragraph.runs[0].font.name = "Times New Roman"
            doc.add_page_break()

        doc_guid: str = uuid.uuid4().hex
        filename: str = f"{doc_guid}_{header_data.report_number}_{header_data.order}_" \
                        f"{header_data.shipper}_{cargo_in_english}".replace("/", '')

        doc.save(f"{settings.REPOSITORY.REPORTS_DIR}/{filename}.{settings.DOC_TYPE}")
        self.logger.info(f"Doc saved to '{settings.REPOSITORY.REPORTS_DIR}/' with GUID {doc_guid}.")
        return doc_guid

    def get_reports(self) -> List[Header]:
        raise NotImplemented

    def add_pictures(self, doc_guid: str, images: List[UploadFile]) -> FileResponse:
        """
        Добавление фотографий к отчету.

        Фотографии добавляются в таблице 2 на 2, по одной таблице на страницу отчета.

        :param doc_guid: GUID файла-отчета
        :param images: фотографии
        :return FileResponse: файл отчета
        """
        filename: str = ''
        for file in os.listdir(settings.REPOSITORY.REPORTS_DIR):
            if file.startswith(doc_guid):
                filename = file
                break
        if not filename:
            raise DraftDocumentNotFound

        doc = self.document_dao(f'{settings.REPOSITORY.REPORTS_DIR}/{filename}')

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

        filename_without_guid: str = filename[33:]

        doc.save(f"{settings.REPOSITORY.REPORTS_DIR}/{filename_without_guid}")
        os.remove(f"{settings.REPOSITORY.REPORTS_DIR}/{filename}")
        return FileResponse(
            f"{settings.REPOSITORY.REPORTS_DIR}/{filename_without_guid}",
            filename=filename_without_guid,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
