from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, validator
from fastapi import UploadFile
import functools


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
    columns: list

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
    date: str
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
    def strip_cargo(cls, value: List[str]):
        return [v.strip() for v in value]


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

    @property
    def header(self) -> dict:
        """Data representation for Report's Header"""
        suppliers, cargos, cargos_in_english, invoices = [], [], [], []
        for unit in self.transport_units:
            suppliers.append(unit.supplier) if unit.supplier not in suppliers else ...
            cargos.append(unit.cargo) if unit.cargo not in cargos else ...
            cargos_in_english.append(unit.cargo_in_english) if unit.cargo_in_english not in cargos_in_english else ...
            invoices.append(unit.invoice) if unit.invoice not in invoices else ...
        cargos = functools.reduce(lambda x, y: x + y, cargos)
        cargos_in_english = functools.reduce(lambda x, y: x + y, cargos_in_english)
        return {
            'report_number': self.number,
            'place_of_inspection': self.place_of_inspection,
            'inspection_date': self.inspection_date,
            'shipper': suppliers,
            'cargo': [
                f'{cargo} / {cargo_in_english}' for cargo, cargo_in_english in zip(cargos, cargos_in_english)
            ],
            'transport_units': self.transport_units_numbers(),
            'invoice': invoices,
            'order': self.order,
        }

    def transport_units_numbers(self) -> List[str]:
        return [unit.number for unit in self.transport_units]


class SelfImportReport(BaseReport):
    """Данные для отчета по импорту"""
    vessel: str
    transport_units: List[Container]

    @property
    def header(self) -> dict:
        header: dict = super().header
        header.update({
            'vessel': self.vessel,
            'BL': [unit.BL for unit in self.transport_units],
        })
        return header


class SelfImportOnAutoReport(BaseReport):
    transport_units: List[Truck]

    @property
    def header(self) -> dict:
        header: dict = super().header
        header.update({
            'CMR': [unit.CMR for unit in self.transport_units],
        })
        return header


class PickupFromSupplierReport(BaseReport):
    transport_units: List[SuppliersTransportUnit]

    @property
    def header(self) -> dict:
        header: dict = super().header
        header.update({
            'discharge_date': [unit.date for unit in self.transport_units],
            'distribution_center_receiver': [unit.distribution_center_receiver for unit in self.transport_units]
        })
        return header
