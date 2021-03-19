from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel


class Cell(ABC):
    """Интерфейс ячеек таблиц, использующихся в репозитории бизнес-логики"""
    text: str
    paragraphs: List


class Row(ABC):
    """Интерфейс строк таблиц, использующихся в репозитории бизнес-логики"""

    @property
    @abstractmethod
    def cells(self) -> List[Cell]:
        ...


class Table(ABC):
    """Интерфейс таблиц, использующихся в репозитории бизнес-логики"""

    @abstractmethod
    def add_row(self) -> Row:
        ...

    @abstractmethod
    def column_cells(self, column_number: int) -> List[Cell]:
        ...

    @abstractmethod
    def row_cells(self, row_number: int) -> List[Cell]:
        ...


class Application(BaseModel):
    """Заявка"""
    place_of_inspection: str
    order: str
    supplier: Union[List[str], str]
    BL: Union[List[str], str]
    containers: Union[List[str], str]
    vessel: Union[List[str], str]
    cargo: str
    card: Union[List[str], str]
    cultivar: Union[List[str], str]
    units: Union[List[str], str]
    invoice: Union[List[str], str]
    date: Union[List[str], str]
    calibre: Union[List[str], str]
    terminal: Union[List[str], str]
    expeditor: Union[List[str], str]
    organization: Union[List[str], str]
    remark: Union[List[str], str]


class BillOfLading(BaseModel):
    """Коносамент"""


class Header(BaseModel):
    """Модель заголовка отчета"""
    number: str = "IL-NS-0"
    place: Optional[str] = None
    date: Optional[Union[List[str], str]] = datetime.today().strftime('%d.%m.%Y')
    shipper: Optional[Union[List[str], str]] = None
    cargo: Optional[str] = None
    transport_units: Optional[List[str]] = None
    vessel: Optional[Union[List[str], str]] = None
    invoice: Optional[Union[List[str], str]] = None
    order: Optional[str] = None
    BL: Optional[Union[List[str], str]] = None
