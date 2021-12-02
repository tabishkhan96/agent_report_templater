from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Iterator, BinaryIO, Final, Any


class BaseAdapter(ABC):
    """Basic document elements adapter"""
    def __init__(self, source: Any):
        self._source = source


class Cell(ABC):
    """Интерфейс ячеек таблиц, использующихся в репозитории бизнес-логики"""
    text: str
    paragraphs: Iterator


class Row(ABC):
    """Интерфейс строк таблиц, использующихся в репозитории бизнес-логики"""
    height: int

    @property
    @abstractmethod
    def cells(self) -> List[Cell]:
        ...


class Column(ABC):
    """Интерфейс столбцов таблиц, использующихся в репозитории бизнес-логики"""
    width: int

    @property
    @abstractmethod
    def cells(self) -> List[Cell]:
        ...


class Table(ABC):
    """Интерфейс таблиц, использующихся в репозитории бизнес-логики"""
    columns: list[Column]
    rows: list[Row]

    @abstractmethod
    def add_row(self) -> Row:
        ...

    @abstractmethod
    def column_cells(self, column_number: int) -> Iterator[Cell]:
        ...

    @abstractmethod
    def row_cells(self, row_number: int) -> Iterator[Cell]:
        ...


@dataclass
class Style:
    alignment: str
    italic: bool
    bold: bool
    font: str


DEFAULT_STYLE: Final[Style] = Style(alignment='center', italic=False, bold=True, font="Times New Roman")


class AbstractDocumentDAO(ABC):
    """Интерфейс класса доступа к документам"""
    def __init__(self, path: str):
        self._document = self.load(path)

    @abstractmethod
    def load(self, path: str):
        """Load document form disc"""

    @abstractmethod
    def save(self, doc_name: str):
        """Save document to storage"""

    @abstractmethod
    def get_tables(self) -> Iterator[Table]:
        """Get list of tables of Doc"""

    @abstractmethod
    def append_table(self, table: Table) -> Table:
        """Add Table to the end of Doc"""

    @abstractmethod
    def get_paragraphs(self) -> List[str]:
        """Get list of paragraphs"""

    @abstractmethod
    def append_paragraph(self, text: str, style: Style = DEFAULT_STYLE):
        """Add text paragraph to the end of Doc"""

    @abstractmethod
    def append_picture(self, picture: BinaryIO, height: float, width: float, alignment: str = 'center'):
        """Add a picture to the end of Doc"""

    @abstractmethod
    def add_page_break(self):
        """Add page break of Doc"""

    @abstractmethod
    def add_section(self, horizontal: bool = False):
        """"""

    @abstractmethod
    def get_page_size(self) -> tuple[float, float]:
        """"""

    @classmethod
    @abstractmethod
    def set_cell_style(cls, cell: Cell, style: Style = DEFAULT_STYLE):
        """Set table cell style shortcut"""

    @classmethod
    @abstractmethod
    def insert_picture_into_cell(cls, cell: Cell, pic: BinaryIO, height: float, width: float):
        """Insert picture into cell shortcut"""
