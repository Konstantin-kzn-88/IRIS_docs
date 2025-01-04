# models/project.py
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Project:
    """Доменная модель проекта"""
    id: Optional[int]
    opo_id: int
    name: str
    description: Optional[str]
    automation_description: Optional[str]
    project_code: Optional[str]
    dpb_code: Optional[str]
    rpz_code: Optional[str]
    ifl_code: Optional[str]
    gochs_code: Optional[str]
    mpb_code: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        return {
            'id': self.id,
            'opo_id': self.opo_id,
            'name': self.name,
            'description': self.description,
            'automation_description': self.automation_description,
            'project_code': self.project_code,
            'dpb_code': self.dpb_code,
            'rpz_code': self.rpz_code,
            'ifl_code': self.ifl_code,
            'gochs_code': self.gochs_code,
            'mpb_code': self.mpb_code
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Создание объекта из словаря"""
        return cls(
            id=data.get('id'),
            opo_id=data['opo_id'],
            name=data['name'],
            description=data.get('description'),
            automation_description=data.get('automation_description'),
            project_code=data.get('project_code'),
            dpb_code=data.get('dpb_code'),
            rpz_code=data.get('rpz_code'),
            ifl_code=data.get('ifl_code'),
            gochs_code=data.get('gochs_code'),
            mpb_code=data.get('mpb_code')
        )

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        return {
            'Наименование': self.name,
            'Описание': self.description or '-',
            'Описание автоматизации': self.automation_description or '-',
            'Шифр проекта': self.project_code or '-',
            'Шифр ДПБ': self.dpb_code or '-',
            'Шифр РПЗ': self.rpz_code or '-',
            'Шифр ИФЛ': self.ifl_code or '-',
            'Шифр ГОЧС': self.gochs_code or '-',
            'Шифр МПБ': self.mpb_code or '-'
        }

    def validate(self) -> None:
        """Валидация объекта"""
        if not self.name:
            raise ValueError("Наименование проекта не может быть пустым")

        # Проверяем только наличие значений в обязательных полях
        if self.opo_id <= 0:
            raise ValueError("Некорректный ID ОПО")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()