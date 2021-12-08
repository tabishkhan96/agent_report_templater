import re
from typing import Dict, Any, Union, Callable, Optional, Final
from pydantic import BaseModel

from .document_daos import Table, Cell


class TemplateEngine:
    """Simple template engine for replacing '{{ ... }}' keys in document tables with desired values."""
    key_pattern: Final[re.Pattern] = re.compile('{{ *[A-z0-9_.]+ *}}')

    @classmethod
    def replace_text(cls, value: str, values: Union[Dict[str, Any], BaseModel]) -> str:
        """
        Replaces a '{{key1.key2}}' key in given string with a value from values which is located at `values[key1][key2]`

        :param value: string contains '{{ ... }}'
        :param values: dict or model with values for replacement
        :return: a new string with keys replaced
        """
        if isinstance(values, BaseModel):
            values: dict = values.dict()
        for match in re.finditer(cls.key_pattern, value):
            key: str = match.group()
            key_substitution = cls._get_nested_attr(values, key[2:-2].strip(), key)
            if isinstance(key_substitution, (list, tuple, set)):
                key_substitution = '\n'.join(key_substitution)
            value = value.replace(key, str(key_substitution))
        return str(value)

    @classmethod
    def replace_in_table(
            cls, table: Table,
            values: Union[Dict[str, Any], BaseModel],
            cell_handler: Optional[Callable[[Cell], None]] = None
    ) -> Table:
        """
        Replaces '{{ key1.key2 }}' keys in all cells of given table with values containing `values[key1][key2]`

        :param table: document table
        :param values: object containing data
        :param cell_handler: callable object that will receive a Cell object after text replacement
        :return: processed table
        """
        for row in table.rows:
            for cell in row.cells:
                cell.text = cls.replace_text(cell.text, values)
                if cell_handler:
                    cell_handler(cell)
        return table

    @classmethod
    def get_key(cls, text: str) -> Optional[str]:
        """
        Returns a key contained in '{{ ... }}' brackets if exists in given string.

        :return: str
        """
        match = re.search(cls.key_pattern, text)
        return match.group()[2:-2] if match else None

    @classmethod
    def _get_nested_attr(cls, obj: dict, attribute_path: str, default: Any) -> Any:
        for part in attribute_path.split('.'):
            if not part:
                continue
            if isinstance(obj, (list, tuple, set)):
                return tuple(map(lambda o: cls._get_nested_attr(o, part, default=obj), obj))
            if not hasattr(obj, 'get'):
                return obj
            obj = obj.get(part)
            if obj is None:
                return default
        return obj
