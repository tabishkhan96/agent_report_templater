class AppException(Exception):
    """Базовое исключение приложения"""


class WrongDocumentTypeException(AppException):
    """Неверно указан тип документа в настройках"""


class DraftDocumentNotFound(AppException):
    """Черновик документа не найден"""
