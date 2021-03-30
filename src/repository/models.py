from abc import ABC, abstractmethod
from datetime import date
from typing import List, Union
from pydantic import BaseModel, validator


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
    report_number: str
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
    date: Union[List[date], date]
    calibre: Union[List[str], str]
    terminal: Union[List[str], str]
    expeditor: Union[List[str], str]
    organization: Union[List[str], str]
    remark: Union[List[str], str]

    @validator("date", pre=True)
    def get_date(cls, value: Union[int, List[int]]):
        """Transform timestamp to datetime object"""
        if isinstance(value, list):
            return [date.fromtimestamp(date_object/1000) for date_object in value]
        return date.fromtimestamp(value/1000)


class BillOfLading(BaseModel):
    """Коносамент"""


class Header(BaseModel):
    """Модель заголовка отчета"""
    report_number: str = "IL-NS-0"
    place: str
    date: Union[List[str], str] = date.today().strftime('%d.%m.%Y')
    shipper: Union[List[str], str]
    cargo: str
    transport_units: List[str]
    vessel: Union[List[str], str]
    invoice: Union[List[str], str]
    order: str
    BL: Union[List[str], str]
