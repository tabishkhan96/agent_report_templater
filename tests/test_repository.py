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
        with pytest.raises(DraftDocumentNotFound):
            repository.add_pictures(uuid4().hex, [])

        images_file_objects = [open(f'tests/images/{img}', 'rb') for img in sorted(os.listdir('tests/images'))]
        assert repository.add_pictures(
            TestDoc.guid,
            [UploadFile(filename=f"{i}.jpg", file=img) for i, img in enumerate(images_file_objects)]
        )
        for img in images_file_objects:
            img.close()
