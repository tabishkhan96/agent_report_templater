from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, validator
from fastapi import UploadFile


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


class ThermometerBoundaries(BaseModel):
    min: float = 0.0
    max: float = 0.0


class ThermographData(ThermometerBoundaries):
    graph: UploadFile
    worked: str


class TemperatureData(BaseModel):
    pulp: ThermometerBoundaries
    thermographs: List[ThermographData]
    recommended: float = 0.0


class TransportUnit(BaseModel):
    number: str
    supplier: str
    cargo: List[str]
    cargo_in_english: List[str] = []
    card: List[str]
    cultivar: List[str]
    units: List[str]
    invoice: str
    date: date
    calibre: List[str]
    temperature: TemperatureData
    pallets: int = 0
    damaged_pallets: int = 0
    boxes: int = 0
    damaged_boxes: int = 0
    cargo_damage: float = 0
    empty_boxes: int = 0
    not_full_boxes: int = 0

    @validator("cargo", allow_reuse=True)
    def strip_cargo(cls, value: str):
        return value.strip()


class Container(TransportUnit):
    BL: str


class Truck(TransportUnit):
    CMR: str


class SuppliersTransportUnit(TransportUnit):
    distribution_center_receiver: str
    card: Optional[str] = None
    cultivar: Optional[str] = None
    invoice: Optional[str] = None
    calibre: Optional[str] = None


class BaseReport(BaseModel):
    """Данные для отчета"""
    place_of_inspection: str
    number: str
    order: str
    inspection_date: str
    transport_units: List[TransportUnit]

    def as_header(self) -> dict:
        """Data representation for Report's Header"""

    def transport_units_numbers(self) -> List[str]:
        return [unit.number for unit in self.transport_units]


class SelfImportReport(BaseReport):
    """Данные для отчета по импорту"""
    vessel: str
    transport_units: List[Container]

    def as_header(self) -> dict:
        return {
            'report_number': self.number,
            'place_of_inspection': self.place_of_inspection,
            'inspection_date': self.inspection_date,
            'shipper': [unit.supplier for unit in self.transport_units],
            'cargo': [f'{unit.cargo} / {unit.cargo_in_english}' for unit in self.transport_units],
            'transport_units': [unit.number for unit in self.transport_units],
            'vessel': self.vessel,
            'invoice': [unit.invoice for unit in self.transport_units],
            'order': self.order,
            'BL': [unit.BL for unit in self.transport_units],
        }


class SelfImportOnAutoReport(BaseReport):
    transport_units: List[Truck]

    def as_header(self) -> dict:
        return {
            'report_number': self.number,
            'place_of_inspection': self.place_of_inspection,
            'inspection_date': self.inspection_date,
            'shipper': [unit.supplier for unit in self.transport_units],
            'cargo': [f'{unit.cargo} / {unit.cargo_in_english}' for unit in self.transport_units],
            'transport_units': [unit.number for unit in self.transport_units],
            'invoice': [unit.invoice for unit in self.transport_units],
            'order': self.order,
            'CMR': [unit.CMR for unit in self.transport_units],
        }


class PickupFromSupplierReport(BaseReport):
    transport_units: List[SuppliersTransportUnit]

    def as_header(self) -> dict:
        return {
            'report_number': self.number,
            'cargo': [f'{unit.cargo} / {unit.cargo_in_english}' for unit in self.transport_units],
            'transport_units': [unit.number for unit in self.transport_units],
            'order': self.order,
            'shipper': [unit.supplier for unit in self.transport_units],
            'inspection_date': self.inspection_date,
            'discharge_date': [unit.date for unit in self.transport_units],
            'place_of_inspection': self.place_of_inspection,
            'distribution_center_receiver': [unit.distribution_center_receiver for unit in self.transport_units]
        }

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
