import unittest

from Exceptions import (
    InvalidDataException,
    InsufficientQuantityException,
    ItemNotFoundException,
    EmptyCartException,
)
from Models import (
    Tovar,
    ElementKorziny,
    Korzina,
    Pokupatel,
    ElementZakaza,
    Zakaz,
)
from Store import Magazin


class TestShop(unittest.TestCase):
    def setUp(self):
        self.shop = Magazin()
        self.t1 = Tovar("1", "Тестовый товар", 1000.0, 10)
        self.shop.dobavit_tovar_na_sklad(self.t1)
        self.client = Pokupatel("1", "Иван", "77001112233")

    def test_tovar_invalid_price_and_stock(self):
        with self.assertRaises(InvalidDataException):
            Tovar("2", "Плохой", -10.0, 5)
        with self.assertRaises(InvalidDataException):
            Tovar("3", "Плохой2", 10.0, -1)

    def test_element_korziny_invalid_quantity(self):
        with self.assertRaises(InvalidDataException):
            ElementKorziny(self.t1, 0)
        with self.assertRaises(InvalidDataException):
            ElementKorziny(self.t1, -5)

    def test_element_korziny_sum(self):
        el = ElementKorziny(self.t1, 3)
        self.assertEqual(el.poluchit_summu(), 3000.0)

    def test_korzina_add_and_total(self):
        self.client.poluchit_korzinu().dobavit_element(self.t1, 2)
        self.assertEqual(
            self.client.korzina.poluchit_obshuyu_tsenu(),
            2000.0
        )

    def test_korzina_insufficient(self):
        with self.assertRaises(InsufficientQuantityException):
            self.client.poluchit_korzinu().dobavit_element(self.t1, 20)

    def test_korzina_invalid_add_zero_or_negative(self):
        with self.assertRaises(InvalidDataException):
            self.client.poluchit_korzinu().dobavit_element(self.t1, 0)
        with self.assertRaises(InvalidDataException):
            self.client.poluchit_korzinu().dobavit_element(self.t1, -3)

    def test_korzina_delete_not_found(self):
        with self.assertRaises(ItemNotFoundException):
            self.client.poluchit_korzinu().udalit_element("999")

    def test_pokupatel_phone_validation(self):
        with self.assertRaises(InvalidDataException):
            Pokupatel("2", "Петя", "12345")
        with self.assertRaises(InvalidDataException):
            Pokupatel("3", "Вася", "abcde12345")

    def test_zakaz_details(self):
        el = ElementZakaza(self.t1, 2, 1000.0)
        zakaz = Zakaz("z1", self.client, [el])
        details = zakaz.poluchit_detali()
        self.assertIn("Заказ №", details)
        self.assertEqual(details["Итого"], "2000.0 тенге")

    def test_oformit_zakaz_success(self):
        self.client.poluchit_korzinu().dobavit_element(self.t1, 4)
        order = self.shop.oformit_zakaz(self.client)
        self.assertEqual(order.itogovaya_summa, 4000.0)
        self.assertEqual(self.shop.tovary["1"].ostatok, 6)

    def test_oformit_zakaz_empty_cart(self):
        with self.assertRaises(EmptyCartException):
            self.shop.oformit_zakaz(self.client)

    def test_oformit_zakaz_insufficient_after_add(self):
        self.client.poluchit_korzinu().dobavit_element(self.t1, 5)
        self.t1.ostatok = 3
        with self.assertRaises(InsufficientQuantityException):
            self.shop.oformit_zakaz(self.client)


if __name__ == "__main__":
    unittest.main()
