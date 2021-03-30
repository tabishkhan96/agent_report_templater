from typing import List

from fastapi import Body, APIRouter, Path, UploadFile, File
from fastapi.responses import FileResponse

from src.repository.configuration import AgentReportRepositoryConfigurator
from src.repository.models import Application, Header

REPOSITORY = AgentReportRepositoryConfigurator().repository()

report_api: APIRouter = APIRouter()


@report_api.put("/", name="Создание отчета.")
async def create_report(application: Application = Body(..., title="Заявка по выбранному заказу")) -> str:
    """Создание черновика отчета."""
    return REPOSITORY.create_report(application)


@report_api.get("/", response_model=List[Header], name="Отчеты в работе")
async def reports_in_progress() -> List[Header]:
    """Отчеты в работе."""
    return REPOSITORY.get_reports()


@report_api.patch("/{doc_guid}", name="Добавить фотографии к отчету")
async def add_photos(
        doc_guid: str = Path(..., description="GUID черновика отчета", min_length=32, max_length=32),
        pictures: List[UploadFile] = File(..., description="Файлы фотографий")
) -> FileResponse:
    """Добавить фотографии к отчету."""
    return REPOSITORY.add_pictures(doc_guid, pictures)
