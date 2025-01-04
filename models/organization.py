# models/organization.py
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Dict, Any


@dataclass
class Organization:
    """Доменная модель организации"""
    id: Optional[int]
    name: str
    full_name: str
    org_form: str
    head_position: Optional[str]
    head_name: Optional[str]
    legal_address: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    license_number: Optional[str]
    license_date: Optional[date]
    ind_safety_system: Optional[str]
    prod_control: Optional[str]
    accident_investigation: Optional[str]
    rescue_contract: Optional[str]
    rescue_certificate: Optional[str]
    fire_contract: Optional[str]
    emergency_certificate: Optional[str]
    material_reserves: Optional[str]
    financial_reserves: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'org_form': self.org_form,
            'head_position': self.head_position,
            'head_name': self.head_name,
            'legal_address': self.legal_address,
            'phone': self.phone,
            'fax': self.fax,
            'email': self.email,
            'license_number': self.license_number,
            'license_date': self.license_date.isoformat() if self.license_date else None,
            'ind_safety_system': self.ind_safety_system,
            'prod_control': self.prod_control,
            'accident_investigation': self.accident_investigation,
            'rescue_contract': self.rescue_contract,
            'rescue_certificate': self.rescue_certificate,
            'fire_contract': self.fire_contract,
            'emergency_certificate': self.emergency_certificate,
            'material_reserves': self.material_reserves,
            'financial_reserves': self.financial_reserves
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Organization':
        """Создание объекта из словаря"""
        # Преобразование строки даты в объект date
        license_date = (datetime.fromisoformat(data['license_date']).date()
                        if data.get('license_date') else None)

        return cls(
            id=data.get('id'),
            name=data['name'],
            full_name=data['full_name'],
            org_form=data['org_form'],
            head_position=data.get('head_position'),
            head_name=data.get('head_name'),
            legal_address=data.get('legal_address'),
            phone=data.get('phone'),
            fax=data.get('fax'),
            email=data.get('email'),
            license_number=data.get('license_number'),
            license_date=license_date,
            ind_safety_system=data.get('ind_safety_system'),
            prod_control=data.get('prod_control'),
            accident_investigation=data.get('accident_investigation'),
            rescue_contract=data.get('rescue_contract'),
            rescue_certificate=data.get('rescue_certificate'),
            fire_contract=data.get('fire_contract'),
            emergency_certificate=data.get('emergency_certificate'),
            material_reserves=data.get('material_reserves'),
            financial_reserves=data.get('financial_reserves')
        )

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        return {
            'Наименование': self.name,
            'Полное наименование': self.full_name,
            'Форма собственности': self.org_form,
            'Должность руководителя': self.head_position or '-',
            'ФИО руководителя': self.head_name or '-',
            'Юридический адрес': self.legal_address or '-',
            'Телефон': self.phone or '-',
            'Факс': self.fax or '-',
            'Email': self.email or '-',
            'Номер лицензии': self.license_number or '-',
            'Дата лицензии': self.license_date.strftime('%d.%m.%Y') if self.license_date else '-',
            'Система ПБ': self.ind_safety_system or '-',
            'Производственный контроль': self.prod_control or '-',
            'Расследование аварий': self.accident_investigation or '-',
            'Договор со спасателями': self.rescue_contract or '-',
            'Свидетельство спасателей': self.rescue_certificate or '-',
            'Договор с пожарными': self.fire_contract or '-',
            'Свидетельство НАСФ': self.emergency_certificate or '-',
            'Материальные резервы': self.material_reserves or '-',
            'Финансовые резервы': self.financial_reserves or '-'
        }