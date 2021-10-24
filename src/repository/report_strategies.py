from abc import ABC, abstractmethod
import logging
from copy import deepcopy
from typing import Generator, Optional, Type
from dynaconf import settings

from src.repository.dao import DocumentDAOInterface
from src.repository.exceptions import DocumentTemplateCorruptedException
from src.repository.models import (
    Table, Row, BaseReport, SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport, TransportUnit,
    Container
)
from src.repository.template_engine import TemplateEngine


class ReportCreationStrategyInterface(ABC):
    """ Интерфейс стратегий создания отчета. """
    logger: logging.Logger
    document_dao: Type[DocumentDAOInterface]
    report: BaseReport

    @abstractmethod
    def __init__(self, document_dao: Type[DocumentDAOInterface], report: SelfImportReport):
        ...

    @abstractmethod
    def execute(self, report_doc: DocumentDAOInterface) -> DocumentDAOInterface:
        ...


class SelfImportReportCreationStrategy(ReportCreationStrategyInterface):
    """ Стратегия создания отчета по собственному импорту. """
    def __init__(self, document_dao: Type[DocumentDAOInterface], report: SelfImportReport):
        self.logger: logging.Logger = logging.getLogger("report_strategy")
        self.document_dao: Type[DocumentDAOInterface] = document_dao
        self.report: SelfImportReport = report

    def execute(self, report_doc: DocumentDAOInterface) -> DocumentDAOInterface:
        """
        Создание отчета для собственного импорта.

        Заполняются таблицы данных о температуре в каждой транспортной единице (ТЕ), добавляются графики датчиков,
        определяются нарушения температурного режима (при их наличии создается письмо протеста), создаются шаблоны
        таблиц тальманского счета по каждой ТЕ, таблицы результатов инспекции, замера калибров, заключения, времени
        жизни и данных о исполнителе.
        """
        temperature_table_template: Optional[Table] = next(
            self.document_dao(
                f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(self.report).__name__}/temperature_template.{settings.DOC_TYPE}"
            ).get_tables(),
            None
        )
        if not temperature_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы температурных данных')

        self.add_temperature_table(report_doc, temperature_table_template)

        tally_account_and_pallets_tables = self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(self.report).__name__}/tally_account_template.{settings.DOC_TYPE}"
        ).get_tables()

        pallets_table_template: Optional[Table] = next(tally_account_and_pallets_tables, None)
        if not pallets_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы паллетов')

        tally_account_table_template: Optional[Table] = next(tally_account_and_pallets_tables, None)
        if not tally_account_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы тальманского счета')

        self.add_tally_account_and_pallets_tables(report_doc, pallets_table_template, tally_account_table_template)

        inspection_result_template = self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(self.report).__name__}/inspection_result_template.{settings.DOC_TYPE}"
        )

        self.add_inspection_result_tables(report_doc, inspection_result_template)

        conclusion_template = self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(self.report).__name__}/conclusion_template.{settings.DOC_TYPE}"
        ).get_tables()

        calibre_table = deepcopy(next(conclusion_template, None))
        conclusion_table = deepcopy(next(conclusion_template, None))
        shelf_life_table = deepcopy(next(conclusion_template, None))
        executor_table = deepcopy(next(conclusion_template, None))

        if not calibre_table or not conclusion_table or not shelf_life_table or not executor_table:
            raise DocumentTemplateCorruptedException('Отсутствует один из шаблонов таблиц заключения')

        self.add_calibre_table(report_doc, calibre_table)
        self.add_conclusion_table(report_doc, conclusion_table)
        self.add_shelf_life_table(report_doc, shelf_life_table)
        TemplateEngine.replace_in_table(
            table=executor_table, values=self.report, cell_handler=self.document_dao.set_cell_style
        )
        report_doc.append_table(executor_table)

        report_doc.add_page_break()
        self.add_pictures_of_thermographs(report_doc)
        return report_doc

    def add_temperature_table(self, report_doc: DocumentDAOInterface, temperature_table: Table):
        self._fill_table_with_row_for_container(self.report.transport_units, temperature_table)
        report_doc.append_table(temperature_table)

    def add_tally_account_and_pallets_tables(
            self, report_doc: DocumentDAOInterface, pallets_table_template: Table, tally_account_table_template: Table
    ):
        for container in self.report.transport_units:
            pallets_table = deepcopy(pallets_table_template)
            TemplateEngine.replace_in_table(table=pallets_table, values=container,
                                            cell_handler=self.document_dao.set_cell_style)
            report_doc.append_table(pallets_table)

            tally_account_table = deepcopy(tally_account_table_template)
            TemplateEngine.replace_in_table(
                table=tally_account_table, values=container, cell_handler=self.document_dao.set_cell_style
            )
            report_doc.append_table(tally_account_table)

    def add_inspection_result_tables(
            self,
            report_doc: DocumentDAOInterface,
            inspection_result_template: DocumentDAOInterface
    ):
        cargos_in_inspection_result_template = list(
            filter(lambda pr: pr, map(lambda pr: pr.text.lower().strip(), inspection_result_template.get_paragraphs()))
        )
        cargos_in_report: set[str] = set((cargo for TU in self.report.transport_units for cargo in TU.cargo))
        containers_by_cargo: dict[str, list[Container]] = {
            cargo: [cont for cont in self.report.transport_units if cargo in cont.cargo] for cargo in cargos_in_report
        }
        for cargo, containers in containers_by_cargo.values():
            try:
                tbl_number: int = cargos_in_inspection_result_template.index(cargo) + 1
            except ValueError:
                tbl_number = 0
            table = list(inspection_result_template.get_tables())[tbl_number]

            self._fill_table_with_row_for_container(containers, table)
            report_doc.append_table(table)

    def add_calibre_table(self, report_doc: DocumentDAOInterface, calibre_table: Table):
        self._fill_table_with_row_for_container(self.report.transport_units, calibre_table)
        report_doc.append_table(calibre_table)

    def add_conclusion_table(self, report_doc, conclusion_table):
        report_doc.append_table(conclusion_table)

    def add_shelf_life_table(self, report_doc, shelf_life_table):
        self._fill_table_with_row_for_container(self.report.transport_units, shelf_life_table)
        report_doc.append_table(shelf_life_table)

    def add_pictures_of_thermographs(self, report_doc):
        for TU in self.report.transport_units:
            for thermograph in TU.temperature.thermographs:
                paragraph = report_doc.append_paragraph(f"Контейнер: {TU.number}\nНомер датчика:{thermograph.number}\n")
                paragraph.runs[0].bold = True
                paragraph.runs[0].font.name = "Times New Roman"
                if thermograph.graph:
                    report_doc.append_paragraph().add_run().add_picture(thermograph.graph)
            report_doc.add_page_break()

    def _fill_table_with_row_for_container(self, containers: list[Container], table: Table):
        cells_content: list[str] = []
        containers: Generator[Container] = (container for container in containers)
        first_container: Container = next(containers, {})

        for cell in table.rows[-1].cells:
            cells_content.append(cell.text)
            cell.text = TemplateEngine.replace_text(cell.text, first_container)

        for container in containers:
            row: Row = table.add_row()
            for number, cell in enumerate(row.cells):
                cell.text = TemplateEngine.replace_text(cells_content[number], container)
                self.document_dao.set_cell_style(cell)

        TemplateEngine.replace_in_table(table=table, values=self.report, cell_handler=self.document_dao.set_cell_style)
