class AppException(Exception):
    """Базовое исключение приложения"""


class WrongDocumentTypeException(AppException):
    """Неверно указан тип документа в настройках"""


class DraftDocumentNotFoundException(AppException):
    """Черновик документа не найден"""


class DocumentTemplateNotFoundException(AppException):
    """Шаблон документа не найден"""


class DocumentTemplateCorruptedException(AppException):
    """Шаблон документа поврежден"""
