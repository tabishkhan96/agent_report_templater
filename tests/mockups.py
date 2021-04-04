from src.repository.models import Application


class TestDoc:
    guid: str


TEST_APPLICATION = Application(
    report_number="IL-AC-000",
    place_of_inspection="РЦ Альфа Центавра / RC Alpha Centauri",
    order="LV-426",
    supplier="Weyland-Yutani Corp",
    BL="AD2001308100",
    containers=['CRLU1395673', 'ADMU9000367', 'SEGU9195005', 'SEGU9195200'],
    vessel="Rocinante",
    cargo="Фарюк / Faruk",
    card="",
    cultivar="",
    units='megatons',
    invoice=['XYZ2020000001283/', 'XYZ2020000001284/'],
    date=[1700000000000, 1600000000000],
    calibre='18mm',
    terminal='term',
    expeditor='Nastromo',
    organization='UN',
    remark='fuck it'
)
