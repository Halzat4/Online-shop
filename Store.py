from typing import Dict, List
from Models import Tovar, Zakaz, Pokupatel, ElementZakaza, Korzina
from Exceptions import EmptyCartException, InsufficientQuantityException

class Magazin:
    def __init__(self):
        self.tovary: Dict[str, Tovar] = {}
        self.zakazy: Dict[str, Zakaz] = {}

    def dobavit_tovar_na_sklad(self, tovar: Tovar):
        self.tovary[tovar.id] = tovar

    def proverit_ostatok(self, tovar_id: str, kolichestvo: int) -> bool:
        if tovar_id in self.tovary:
            return self.tovary[tovar_id].ostatok >= kolichestvo
        return False

    def oformit_zakaz(self, pokupatel: Pokupatel) -> Zakaz:
        korzina = pokupatel.poluchit_korzinu()
        if not korzina.elementy:
            raise EmptyCartException("Корзина пуста!")

        elementy_zakaza: List[ElementZakaza] = []
        for el_korziny in korzina.elementy.values():
            tovar = el_korziny.tovar
            kol = el_korziny.kolichestvo
            if not self.proverit_ostatok(tovar.id, kol):
                raise InsufficientQuantityException(f"Не хватает товара: {tovar.nazvanie}")
            elementy_zakaza.append(ElementZakaza(tovar, kol, tovar.tsena))

        new_id = str(len(self.zakazy) + 1)
        zakaz = Zakaz(new_id, pokupatel, elementy_zakaza)
        self.zakazy[new_id] = zakaz

        for el in elementy_zakaza:
            self.tovary[el.tovar.id].ostatok -= el.kolichestvo

        pokupatel.korzina = Korzina()
        return zakaz

def zapolnit_magazin(magazin: Magazin):
    magazin.dobavit_tovar_na_sklad(Tovar("1", "Ноутбук", 250000.0, 5))
    magazin.dobavit_tovar_na_sklad(Tovar("2", "Мышка", 5000.0, 20))
    magazin.dobavit_tovar_na_sklad(Tovar("3", "Клавиатура", 15000.0, 10))
    magazin.dobavit_tovar_na_sklad(Tovar("4", "Монитор", 60000.0, 3))

def pokazat_tovary(magazin: Magazin):
    print("\n--- Ассортимент Магазина ---")
    print(f"{'ID':<5} {'Название':<20} {'Цена (тг)':<12} {'Остаток':<10}")
    print("-" * 50)
    for t in magazin.tovary.values():
        print(f"{t.id:<5} {t.nazvanie:<20} {t.tsena:<12} {t.ostatok:<10}")
    print("-" * 50)

def restore_cart(client: Pokupatel, cart_data: List[dict], shop: Magazin):
    if not cart_data:
        return
    print("Восстановление корзины...")
    for item in cart_data:
        t_id = item["tovar_id"]
        qty = item["kolichestvo"]
        if t_id in shop.tovary:
            tovar = shop.tovary[t_id]
            try:
                client.poluchit_korzinu().dobavit_element(tovar, qty)
            except InsufficientQuantityException:
                print(f"Внимание: товар {tovar.nazvanie} недоступен в количестве {qty} шт.")
        else:
            print(f"Внимание: товар с ID {t_id} больше не существует в магазине.")
