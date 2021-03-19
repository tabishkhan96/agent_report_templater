import inspect
from typing import Dict, Type
from dynaconf import settings

from src.repository.exceptions import WrongDocumentType
from src.repository.repository import AgentReportRepository
from src.repository import dao


class AgentReportRepositoryConfigurator:
    def __init__(self):
        self.doc_dao_types: Dict[str, type] = {
            name[:-11].lower(): type_ for name, type_ in inspect.getmembers(dao) if name.endswith('DocumentDAO')
        }

    @property
    def documents_dao(self):
        doc_type: Type[dao.DocumentDAOInterface] = self.doc_dao_types.get(settings.DOC_TYPE)
        if not doc_type:
            raise WrongDocumentType
        return doc_type

    def repository(self):
        return AgentReportRepository(self.documents_dao)
