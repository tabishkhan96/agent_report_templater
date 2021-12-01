from importlib import import_module
import inspect
import os
from typing import Dict, Type, Optional

import toml
from dynaconf import settings
import logging
import logging.config

from .exceptions import WrongDocumentTypeException
from .repository import AgentReportRepository
from .document_daos import AbstractDocumentDAO


class AgentReportRepositoryConfigurator:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger("configurator")
        self.__setup_logger(settings.LOGGING)
        package_members: list[tuple[str, type]] = inspect.getmembers(import_module('src.repository.document_daos'))
        self.doc_dao_types: Dict[str, type] = {
            name[:-11].lower(): dao_class for name, dao_class in package_members if name.endswith('DocumentDAO')
        }

    @property
    def documents_dao(self):
        dao_class: Type[AbstractDocumentDAO] = self.doc_dao_types.get(settings.DOC_TYPE)
        if not dao_class:
            raise WrongDocumentTypeException
        return dao_class

    def repository(self):
        return AgentReportRepository(self.documents_dao)

    def __setup_logger(self, file_path: Optional[str]):
        if not file_path:
            self.logger.warning("Logging configuration does not exists. Ensure that variable LOGGING is properly set")
            return

        if not os.path.exists(file_path):
            self.logger.warning(f"{file_path} does not exists. Logging configuration skipped.")

        with open(file_path) as f:
            logging.config.dictConfig(toml.load(f))
