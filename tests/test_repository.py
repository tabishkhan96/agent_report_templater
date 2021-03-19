import os
from uuid import uuid4

import pytest
from fastapi import UploadFile

from src.repository.configuration import AgentReportRepositoryConfigurator
from src.repository.exceptions import DraftDocumentNotFound
from src.repository.repository import AgentReportRepository

from tests.mockups import TEST_APPLICATION, TestDoc


@pytest.fixture
def repository(request):
    return AgentReportRepositoryConfigurator().repository()


class TestAgentReportRepository:
    """Business logic tests"""

    def test_start(self, repository: AgentReportRepository):
        TestDoc.guid = repository.create_report(TEST_APPLICATION)
        assert TestDoc.guid

    def test_get_reports(self, repository: AgentReportRepository):
        pass

    def test_add_pictures(self, repository: AgentReportRepository):
        images = [f'tests/images/{img}' for img in sorted(os.listdir('tests/images'))]
        with pytest.raises(DraftDocumentNotFound):
            repository.add_pictures(uuid4().hex, [])
        assert repository.add_pictures(TestDoc.guid, images)
