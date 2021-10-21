from abc import ABC, abstractmethod
from typing import List, Union, Any, Generator

import docx
from docx.document import Document as DocxDocument, ElementProxy as DocxElementProxy
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.table import Table as DocxTable
from docx.shared import Cm

from src.repository.models import Table, Cell


class DocumentDAOInterface(ABC):
    """Интерфейс класса доступа к документам"""
    def __init__(self, path: str):
        self._document: Union[DocxDocument, Any] = self.load(path)

    @abstractmethod
    def load(self, path: str):
        """Load document form disc"""

    @abstractmethod
    def load_from_storage(self, guid: str):
        """Load document form storage"""

    @abstractmethod
    def save(self, doc_name: str):
        """Save document to storage"""

    @abstractmethod
    def get_tables(self) -> Generator[Table]:
        """Get list of tables of Doc"""

    @abstractmethod
    def append_part(self, obj: Union[Table, Any]):
        """Append part to Doc"""

    @abstractmethod
    def append_table(self, table: Table):
        """Add Table to the end of Doc"""

    @abstractmethod
    def get_paragraphs(self) -> List:
        """Get list of paragraphs"""

    @abstractmethod
    def append_paragraph(self, paragraph: Union[str, Any]):
        """Add text paragraph to the end of Doc"""

    @abstractmethod
    def add_page_break(self):
        """Add page break of Doc"""

    @abstractmethod
    def set_cell_style(
            self,
            cell: Cell,
            alignment: str = 'center',
            italic: bool = False,
            bold: bool = True,
            font: str = "Times New Roman"
    ):
        """Set table cell style shortcut"""

    @abstractmethod
    def insert_picture_into_cell(self, cell: Cell, pic, height: int = 8, width: int = 8):
        """Insert picture into cell shortcut"""


class DocxDocumentDAO(DocumentDAOInterface):
    """
    Класс доступа к документам типа .docx
    """
    def load(self, path: str):
        """Load document form disc"""
        return docx.Document(path)

    def load_from_storage(self, guid: str):
        """Load document form storage"""
        raise NotImplementedError

    def save(self, doc_name: str):
        """Save document to storage"""
        self._document.save(doc_name)

    def get_tables(self) -> Generator[DocxTable]:
        """Get list of tables of Doc"""
        for table in self._document.tables:
            yield table

    def append_part(self, obj: DocxElementProxy):
        """Append part to Doc"""
        self._document.element.body.append(obj)

    def append_table(self, table: DocxTable):
        """Add Table to the end of Doc"""
        tbl = table._tbl
        paragraph = self._document.add_paragraph()
        paragraph._p.addnext(tbl)

    def get_paragraphs(self) -> List:
        """"Get list of paragraphs"""
        return self._document.paragraphs

    def append_paragraph(self, paragraph: Union[str, Any]):
        return self._document.add_paragraph(text=paragraph)

    def add_page_break(self):
        self._document.add_page_break()

    def set_cell_style(
            self,
            cell: Cell,
            alignment: str = 'center',
            italic: bool = False,
            bold: bool = True,
            font: str = "Times New Roman"
    ):
        cell.paragraphs[0].paragraph_format.alignment = getattr(WD_TABLE_ALIGNMENT, alignment.upper())
        cell.paragraphs[0].runs[0].bold = bold
        cell.paragraphs[0].runs[0].italic = italic
        cell.paragraphs[0].runs[0].font.name = font

    def insert_picture_into_cell(self, cell: Cell, pic, height: int = 8, width: int = 8):
        cell.paragraphs[0].add_run().add_picture(pic, width=Cm(width), height=Cm(height))
