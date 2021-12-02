from typing import List, Union

from fastapi import Body, APIRouter, UploadFile
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


@report_api.get("/", response_model=List[BaseReport], name="Отчеты в работе")
async def reports_in_progress() -> List[BaseReport]:
    """Отчеты в работе."""
    return REPOSITORY.get_reports()



@report_api.patch("/", name="")
async def add_photos(
        report_data: Union[SelfImportReport,
                           SelfImportOnAutoReport,
                           PickupFromSupplierReport] = Body(..., title="Модель отчета c фотобазой транспортных единиц")
) -> FileResponse:
    """Добавить фотографии к отчету."""
    return REPOSITORY.add_pictures(report_data)