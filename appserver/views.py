from typing import List, Union

from fastapi import Body, APIRouter, UploadFile, File
from fastapi.responses import FileResponse

from .core.configuration import AgentReportRepositoryConfigurator
from .core.models import SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport

REPOSITORY = AgentReportRepositoryConfigurator().repository()

report_api: APIRouter = APIRouter()


@report_api.put("/", name="Создание отчета.")
async def create_report(
        report_data: Union[SelfImportReport,
                           SelfImportOnAutoReport,
                           PickupFromSupplierReport] = Body(..., title="Модель отчета с заполненной текстовой частью")
) -> FileResponse:
    """Создание черновика отчета."""
    return REPOSITORY.create_report(report_data)


@report_api.get("/{filename}", name="Отчеты в работе")
async def reports_in_progress(filename: str) -> Union[List[dict], FileResponse]:
    """Отчеты в работе."""
    return REPOSITORY.get_report(filename)


@report_api.post("/{filename}", name="Замена отчета")
async def update_report(filename: str, report_file: UploadFile = File(...)) -> str:
    """Заменить файл отчета."""
    return REPOSITORY.update_report(filename, report_file)


@report_api.patch("/", name="")
async def add_photos(
        report_data: Union[SelfImportReport,
                           SelfImportOnAutoReport,
                           PickupFromSupplierReport] = Body(..., title="Модель отчета c фотобазой транспортных единиц")
) -> FileResponse:
    """Добавить фотографии к отчету."""
    return REPOSITORY.add_pictures(report_data)
