from abc import ABC, abstractmethod
import logging
from copy import deepcopy
from typing import Generator, Optional, Type, Iterator
from dynaconf import settings

from src.repository.dao import DocumentDAOInterface
from src.repository.exceptions import DocumentTemplateCorruptedException
from src.repository.models import (
    Table, Row, BaseReport, SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport, TransportUnit,
    Container
)
from src.repository.template_engine import TemplateEngine


class ReportCreationBaseStrategy(ABC):
    """ Интерфейс стратегий создания отчета. """
    logger: logging.Logger
    document_dao: Type[DocumentDAOInterface]
    report: BaseReport

    def __init__(self, document_dao: Type[DocumentDAOInterface], report: SelfImportReport):
        self.logger: logging.Logger = logging.getLogger("report_strategy")
        self.document_dao: Type[DocumentDAOInterface] = document_dao
        self.report: SelfImportReport = report

    @abstractmethod
    def execute(self, report_doc: DocumentDAOInterface) -> DocumentDAOInterface:
        ...

    def fill_header_table(self, report_doc: DocumentDAOInterface):
        header: Table = next(report_doc.get_tables(), None)
        if not header:
            raise DocumentTemplateCorruptedException('Отсутствует таблица-заголовок')
        for unit in self.report.transport_units:
            unit.cargo_in_english = [
                settings.VEGETABLES.get(cargo.lower()) or settings.FRUITS.get(cargo.lower(), '') for cargo in unit.cargo
            ]
        TemplateEngine.replace_in_table(
            table=header, values=self.report.header, cell_handler=self.document_dao.set_cell_style
        )

    def _get_template_dao(self, template_name: str) -> DocumentDAOInterface:
        return self.document_dao(
            f"{settings.REPOSITORY.TEMPLATES_DIR}/{type(self.report).__name__}/{template_name}.{settings.DOC_TYPE}"
        )

    def _get_tables_from_template(self, template_name: str) -> Iterator[Table]:
        return self._get_template_dao(template_name).get_tables()


class SelfImportReportCreationStrategy(ReportCreationBaseStrategy):
    """ Стратегия создания отчета по собственному импорту. """

    def execute(self, report_doc: DocumentDAOInterface) -> DocumentDAOInterface:
        """
        Создание отчета для собственного импорта.

        Заполняются таблицы данных о температуре в каждой транспортной единице (ТЕ), добавляются графики датчиков,
        определяются нарушения температурного режима (при их наличии создается письмо протеста), создаются шаблоны
        таблиц тальманского счета по каждой ТЕ, таблицы результатов инспекции, замера калибров, заключения, времени
        жизни и данных о исполнителе.
        """
        self.fill_header_table(report_doc)
        temperature_table_template: Optional[Table] = next(self._get_tables_from_template('temperature_template'), None)
        if not temperature_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы температурных данных')
        self.add_temperature_table(report_doc, temperature_table_template)

        tally_account_and_pallets_tables = self._get_tables_from_template('tally_account_template')
        pallets_table_template: Optional[Table] = next(tally_account_and_pallets_tables, None)
        if not pallets_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы паллетов')
        tally_account_table_template: Optional[Table] = next(tally_account_and_pallets_tables, None)
        if not tally_account_table_template:
            raise DocumentTemplateCorruptedException('Отсутствует шаблон таблицы тальманского счета')
        self.add_tally_account_and_pallets_tables(report_doc, pallets_table_template, tally_account_table_template)

        self.add_inspection_result_tables(report_doc, self._get_template_dao('inspection_result_template'))

        conclusion_template = self._get_tables_from_template('conclusion_template')
        calibre_table: Optional[Table] = deepcopy(next(conclusion_template, None))
        conclusion_table: Optional[Table] = deepcopy(next(conclusion_template, None))
        shelf_life_table: Optional[Table] = deepcopy(next(conclusion_template, None))
        executor_table: Optional[Table] = deepcopy(next(conclusion_template, None))
        if not calibre_table or not conclusion_table or not shelf_life_table or not executor_table:
            raise DocumentTemplateCorruptedException('Отсутствует один из шаблонов таблиц заключения')

        self.add_calibre_table(report_doc, calibre_table)
        self.add_conclusion_table(report_doc, conclusion_table)
        self.add_shelf_life_table(report_doc, shelf_life_table)
        self.add_executor_table(report_doc, executor_table)
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
            filter(lambda pr: pr, map(lambda pr: pr.lower().strip(), inspection_result_template.get_paragraphs()))
        )
        cargos_in_report: set[str] = set((cargo for TU in self.report.transport_units for cargo in TU.cargo))
        containers_by_cargo: dict[str, list[Container]] = {
            cargo: [cont for cont in self.report.transport_units if cargo in cont.cargo] for cargo in cargos_in_report
        }
        inspection_result_template_tables: list[Table] = list(inspection_result_template.get_tables())
        for cargo, containers in containers_by_cargo.items():
            try:
                tbl_number: int = cargos_in_inspection_result_template.index(cargo) + 1
            except ValueError:
                tbl_number = 0
            table = deepcopy(inspection_result_template_tables[tbl_number])

            self._fill_table_with_row_for_container(containers, table)
            report_doc.append_table(table)

    def add_calibre_table(self, report_doc: DocumentDAOInterface, calibre_table: Table):
        self._fill_table_with_row_for_container(self.report.transport_units, calibre_table)
        report_doc.append_table(calibre_table)

    def add_conclusion_table(self, report_doc: DocumentDAOInterface, conclusion_table: Table):
        report_doc.append_table(conclusion_table)

    def add_shelf_life_table(self, report_doc: DocumentDAOInterface, shelf_life_table: Table):
        self._fill_table_with_row_for_container(self.report.transport_units, shelf_life_table)
        report_doc.append_table(shelf_life_table)

    def add_executor_table(self, report_doc: DocumentDAOInterface, executor_table: Table):
        TemplateEngine.replace_in_table(
            table=executor_table, values=self.report, cell_handler=self.document_dao.set_cell_style
        )
        report_doc.append_table(executor_table)

    def add_pictures_of_thermographs(self, report_doc: DocumentDAOInterface):
        for TU in self.report.transport_units:
            for thermograph in TU.temperature.thermographs:
                report_doc.append_paragraph(f"Контейнер: {TU.number}\nНомер датчика:{thermograph.number}\n")
                if thermograph.graph:
                    report_doc.append_picture(thermograph.graph.file)
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
