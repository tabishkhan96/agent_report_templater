from typing import List, Union

from fastapi import Body, APIRouter, Path, UploadFile, File
from fastapi.responses import FileResponse

from src.repository.configuration import AgentReportRepositoryConfigurator
from src.repository.models import BaseReport, SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport

REPOSITORY = AgentReportRepositoryConfigurator().repository()

report_api: APIRouter = APIRouter()


@report_api.put("/", name="Создание отчета.")
async def create_report(
        report_data: Union[SelfImportReport, SelfImportOnAutoReport, PickupFromSupplierReport] = Body(
            ..., title="Данные для отчета")
) -> FileResponse:
    """Создание черновика отчета."""
    return REPOSITORY.create_report(report_data)


@report_api.get("/", response_model=List[BaseReport], name="Отчеты в работе")
async def reports_in_progress() -> List[BaseReport]:
    """Отчеты в работе."""
    return REPOSITORY.get_reports()


@report_api.patch("/", name="Добавить фотографии к отчету")
async def add_photos(
        filename: str = Body(..., description="GUID черновика отчета", min_length=32, max_length=32),
        pictures: List[UploadFile] = File(..., description="Файлы фотографий")
) -> FileResponse:
    """Добавить фотографии к отчету."""
    return REPOSITORY.add_pictures(filename, pictures)
