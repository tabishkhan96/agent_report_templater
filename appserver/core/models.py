import datetime
import re
from io import BytesIO
from base64 import b64decode
from typing import List, Optional
from pydantic import BaseModel, validator


class Photo(BaseModel):
    id: int
    file: BytesIO
    rotation: int = 0

    class Config:
        arbitrary_types_allowed = True

    @validator('file', pre=True)
    def decode_base64_string_to_bytes(cls, value):
        value = re.findall("data:image/\w+;base64,(.*)", value)
        return BytesIO(b64decode(value[0]) if value else b'')


class FloatWithCustomStringification(float):
    def __str__(self) -> str:
        """Always show '+' symbol and 1 digit after period when stringified"""
        if self == 0:
            return str(0.0)
        return "{0:+.1f}".format(self)


class ThermometerBoundaries(BaseModel):
    min: FloatWithCustomStringification
    max: FloatWithCustomStringification

    @validator('min', 'max', allow_reuse=True)
    def validate_temperature(cls, value):
        return FloatWithCustomStringification(value)


class ThermographData(ThermometerBoundaries):
    number: str
    graph: Optional[Photo]
    worked: str

    @validator("worked")
    def set_worked_status(cls, value):
        statuses_mapping = {
            "0": "Нет/No",
            "1": "Да/Yes",
            "2": "Не работал/Did not work",
            "3": "Работал некорректно/Did not work correctly"
        }
        return statuses_mapping.get(value, "")


class TemperatureData(BaseModel):
    pulp: ThermometerBoundaries
    thermographs: List[ThermographData]
    recommended: FloatWithCustomStringification
    violations_affect: str

    @validator("violations_affect")
    def set_violations(cls, value):
        statuses_mapping = {
            "1": "Нет/Нет\nNo/No",
            "2": "Да/Нет\nYes/No",
            "3": "Да/Да\nYes/Yes"
        }
        return statuses_mapping.get(value, "")

    @validator('recommended', allow_reuse=True)
    def validate_temperature(cls, value):
        return FloatWithCustomStringification(value)


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
    pallets: int
    damaged_pallets: int = 0
    boxes: int
    damaged_boxes: int = 0
    cargo_damage: float = 0.0
    empty_boxes: int = 0
    not_full_boxes: int = 0
    photos: list[Photo] = []

    @validator("cargo", allow_reuse=True)
    def strip_cargo(cls, value: List[str]):
        return [v.strip().lower() for v in value]


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
    surveyor: str
    issue_date: str = datetime.date.today().strftime('%d.%m.%Y')
    transport_units: List[TransportUnit]

    @property
    def header(self) -> dict:
        """Data representation for Report's Header"""
        cargos: set[str] = self.all_cargos
        cargos_in_english: set[str] = self.all_cargos_in_english
        return {
            'report_number': self.number,
            'place_of_inspection': self.place_of_inspection,
            'inspection_date': self.inspection_date,
            'shipper': {unit.supplier for unit in self.transport_units},
            'cargo': [
                f'{cargo.capitalize()}/{cargo_in_english}' for cargo, cargo_in_english in zip(cargos, cargos_in_english)
            ],
            'transport_units': [unit.number for unit in self.transport_units],
            'invoice': {unit.invoice for unit in self.transport_units},
            'order': self.order,
        }

    @property
    def all_cargos_in_english(self) -> set[str]:
        return {cargo for unit in self.transport_units for cargo in unit.cargo_in_english}

    @property
    def all_cargos(self) -> set[str]:
        return {cargo for unit in self.transport_units for cargo in unit.cargo}


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
