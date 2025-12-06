from typing import List, Dict
from Exceptions import InvalidDataException, InsufficientQuantityException, ItemNotFoundException

class Tovar:
    def __init__(self, id: str, nazvanie: str, tsena: float, ostatok: int):
        if tsena < 0:
            raise InvalidDataException("Цена не может быть отрицательной")
        if ostatok < 0:
            raise InvalidDataException("Остаток не может быть отрицательным")
        self.id = id
        self.nazvanie = nazvanie
        self.tsena = tsena
        self.ostatok = ostatok

class ElementKorziny:
    def __init__(self, tovar: Tovar, kolichestvo: int):
        if kolichestvo <= 0:
            raise InvalidDataException("Количество должно быть больше нуля")
        self.tovar = tovar
        self.kolichestvo = kolichestvo

    def poluchit_summu(self) -> float:
        return self.tovar.tsena * self.kolichestvo

    def to_dict(self) -> dict:
        return {"tovar_id": self.tovar.id, "kolichestvo": self.kolichestvo}

class Korzina:
    def __init__(self):
        self.elementy: Dict[str, ElementKorziny] = {}

    def dobavit_element(self, tovar: Tovar, kolichestvo: int):
        if kolichestvo <= 0:
            raise InvalidDataException("Нельзя добавить 0 или отрицательное количество")
        tekushee = self.elementy.get(tovar.id)
        tekushee_kol = tekushee.kolichestvo if tekushee else 0
        if tekushee_kol + kolichestvo > tovar.ostatok:
            raise InsufficientQuantityException(
                f"Недостаточно товара '{tovar.nazvanie}'. "
                f"Доступно: {tovar.ostatok}, в корзине уже: {tekushee_kol}"
            )
        if tekushee:
            tekushee.kolichestvo += kolichestvo
        else:
            self.elementy[tovar.id] = ElementKorziny(tovar, kolichestvo)

    def udalit_element(self, tovar_id: str):
        if tovar_id not in self.elementy:
            raise ItemNotFoundException(f"Товар с ID {tovar_id} не найден в корзине.")
        del self.elementy[tovar_id]

    def poluchit_obshuyu_tsenu(self) -> float:
        return sum(e.poluchit_summu() for e in self.elementy.values())

    def to_list(self) -> List[dict]:
        return [e.to_dict() for e in self.elementy.values()]

class Pokupatel:
    def __init__(self, id: str, imya: str, kontakty: str):
        self.id = id
        self.imya = imya
        self._kontakty = kontakty
        self.korzina = Korzina()
        self.proverit_kontakty(kontakty)

    def proverit_kontakty(self, kontakty: str):
        if not kontakty.isdigit():
            raise InvalidDataException("Номер телефона должен состоять только из цифр")
        if len(kontakty) < 10:
            raise InvalidDataException("Номер телефона слишком короткий (минимум 10 цифр)")

    def poluchit_korzinu(self) -> Korzina:
        return self.korzina

class ElementZakaza:
    def __init__(self, tovar: Tovar, kolichestvo: int, tsena_edinitsy: float):
        self.tovar = tovar
        self.kolichestvo = kolichestvo
        self.tsena_edinitsy = tsena_edinitsy

    def poluchit_summu(self) -> float:
        return self.tsena_edinitsy * self.kolichestvo

class Zakaz:
    def __init__(self, id: str, pokupatel: Pokupatel, elementy: List[ElementZakaza]):
        self.id = id
        self.pokupatel = pokupatel
        self.elementy = elementy
        self.status = "Noviy"
        self.itogovaya_summa = sum(e.poluchit_summu() for e in elementy)

    def poluchit_detali(self) -> dict:
        tovary_str = ", ".join(f"{e.tovar.nazvanie} (x{e.kolichestvo})" for e in self.elementy)
        return {
            "Заказ №": self.id,
            "Покупатель": self.pokupatel.imya,
            "Статус": self.status,
            "Товары": tovary_str,
            "Итого": f"{self.itogovaya_summa} тенге",
        }
