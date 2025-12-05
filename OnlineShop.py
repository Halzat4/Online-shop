from typing import List, Dict
import json
import os


class ShopException(Exception):
	pass


class InsufficientQuantityException(ShopException):
	pass


class ItemNotFoundException(ShopException):
	pass


class InvalidDataException(ShopException):
	pass


class EmptyCartException(ShopException):
	pass


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
		return {
			"tovar_id": self.tovar.id,
			"kolichestvo": self.kolichestvo
		}


class Korzina:
	def __init__(self):
		self.elementy: Dict[str, ElementKorziny] = {}

	def dobavit_element(self, tovar: Tovar, kolichestvo: int):
		if kolichestvo <= 0:
			raise InvalidDataException(
				"Нельзя добавить 0 или отрицательное количество"
			)

		tekushee_kolichestvo_v_korzine = 0
		if tovar.id in self.elementy:
			tekushee_kolichestvo_v_korzine = self.elementy[tovar.id].kolichestvo

		if (tekushee_kolichestvo_v_korzine + kolichestvo) > tovar.ostatok:
			raise InsufficientQuantityException(
				f"Недостаточно товара '{tovar.nazvanie}'. "
				f"Доступно: {tovar.ostatok}, в корзине уже: "
				f"{tekushee_kolichestvo_v_korzine}"
			)

		if tovar.id in self.elementy:
			self.elementy[tovar.id].kolichestvo += kolichestvo
		else:
			self.elementy[tovar.id] = ElementKorziny(tovar, kolichestvo)

	def udalit_element(self, tovar_id: str):
		if tovar_id not in self.elementy:
			raise ItemNotFoundException(
				f"Товар с ID {tovar_id} не найден в корзине."
			)
		del self.elementy[tovar_id]

	def poluchit_obshuyu_tsenu(self) -> float:
		return sum(item.poluchit_summu() for item in self.elementy.values())

	def to_list(self) -> List[dict]:
		return [elem.to_dict() for elem in self.elementy.values()]


class Pokupatel:
	def __init__(self, id: str, imya: str, kontakty: str):
		self.id = id
		self.imya = imya
		self._kontakty = kontakty
		self.korzina = Korzina()
		self.proverit_kontakty(kontakty)

	def proverit_kontakty(self, kontakty: str):
		if not kontakty.isdigit():
			raise InvalidDataException(
				"Номер телефона должен состоять только из цифр"
			)
		if len(kontakty) < 10:
			raise InvalidDataException(
				"Номер телефона слишком короткий (минимум 10 цифр)"
			)

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
	def __init__(self, id: str, pokupatel: Pokupatel,
				 elementy: List[ElementZakaza]):
		self.id = id
		self.pokupatel = pokupatel
		self.elementy = elementy
		self.status = "Noviy"
		self.itogovaya_summa = sum(e.poluchit_summu() for e in elementy)

	def poluchit_detali(self) -> dict:
		tovary_str = ", ".join(
			[f"{e.tovar.nazvanie} (x{e.kolichestvo})"
			 for e in self.elementy]
		)
		return {
			"Заказ №": self.id,
			"Покупатель": self.pokupatel.imya,
			"Статус": self.status,
			"Товары": tovary_str,
			"Итого": f"{self.itogovaya_summa} тенге",
		}


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

		spisok_elementov_zakaza: List[ElementZakaza] = []

		for el_korziny in korzina.elementy.values():
			tovar = el_korziny.tovar
			kolichestvo = el_korziny.kolichestvo

			if not self.proverit_ostatok(tovar.id, kolichestvo):
				raise InsufficientQuantityException(
					f"Не хватает товара: {tovar.nazvanie}"
				)

			element_zakaza = ElementZakaza(
				tovar,
				kolichestvo,
				tovar.tsena,
			)
			spisok_elementov_zakaza.append(element_zakaza)

		new_id = str(len(self.zakazy) + 1)
		noviy_zakaz = Zakaz(new_id, pokupatel, spisok_elementov_zakaza)
		self.zakazy[new_id] = noviy_zakaz

		for el in spisok_elementov_zakaza:
			self.tovary[el.tovar.id].ostatok -= el.kolichestvo

		pokupatel.korzina = Korzina()
		return noviy_zakaz


CLIENTS_FILE = "clients.json"


def load_clients() -> Dict[str, dict]:
	if not os.path.exists(CLIENTS_FILE):
		return {}
	with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
		try:
			data = json.load(f)
			if isinstance(data, dict):
				return data
			return {}
		except json.JSONDecodeError:
			return {}


def save_clients(clients: Dict[str, dict]) -> None:
	with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
		json.dump(clients, f, ensure_ascii=False, indent=4)


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
				print(f"Внимание: Товар {tovar.nazvanie} больше недоступен в количестве {qty} шт.")
		else:
			print(f"Внимание: Товар с ID {t_id} больше не существует в магазине.")


def main():
	shop = Magazin()
	zapolnit_magazin(shop)

	clients = load_clients()

	print("Добро пожаловать в консольный магазин!")

	while True:
		name = input("Введите ваше имя: ").strip()
		if not name:
			print("Имя не может быть пустым.")
			continue
		break

	if name in clients:
		stored = clients[name]
		contact = stored.get("kontakty", "")
		print(f"Найден существующий клиент: {name}, телефон: {contact}")
		while True:
			use = input("Использовать эти данные? (да/нет): ").strip().lower()
			if use in ("да", "нет"):
				break
			print("Пожалуйста, введите 'да' или 'нет'.")

		if use == "да":
			try:
				client = Pokupatel(stored["id"], name, contact)
				cart_data = stored.get("cart", [])
				restore_cart(client, cart_data, shop)

			except InvalidDataException:
				print("Сохранённый номер некорректен, введите новый.")
				while True:
					contact = input("Введите номер телефона: ")
					try:
						client = Pokupatel(stored["id"], name, contact)
						break
					except InvalidDataException as e:
						print(f"[ОШИБКА]: {e}")
		else:
			while True:
				contact = input("Введите номер телефона: ")
				try:
					client = Pokupatel(stored["id"], name, contact)
					break
				except InvalidDataException as e:
					print(f"[ОШИБКА]: {e}")
			clients[name]["kontakty"] = contact
			clients[name]["cart"] = []
			save_clients(clients)
	else:
		while True:
			contact = input("Введите номер телефона: ")
			try:
				new_id = str(len(clients) + 1)
				client = Pokupatel(new_id, name, contact)
				clients[name] = {
					"id": new_id,
					"kontakty": contact,
					"cart": []
				}
				save_clients(clients)
				break
			except InvalidDataException as e:
				print(f"[ОШИБКА]: {e}")

	while True:
		print("\nВыберите действие:")
		print("1. Показать товары")
		print("2. Добавить товар в корзину")
		print("3. Посмотреть корзину")
		print("4. Удалить товар из корзины")
		print("5. Оформить заказ")
		print("6. Сохранить корзину и выйти")
		print("7. Выход без сохранения")

		vybor = input("Ваш выбор: ")

		try:
			if vybor == "1":
				pokazat_tovary(shop)

			elif vybor == "2":
				t_id = input("Введите ID товара: ")
				if t_id in shop.tovary:
					qty_str = input("Введите количество: ")
					if not qty_str.isdigit():
						print("Ошибка: введите число!")
						continue
					qty = int(qty_str)
					tovar = shop.tovary[t_id]
					client.poluchit_korzinu().dobavit_element(tovar, qty)
					print(f"Добавлено: {tovar.nazvanie} x{qty}")
				else:
					print("Товар с таким ID не найден.")

			elif vybor == "3":
				korzina = client.poluchit_korzinu()
				if not korzina.elementy:
					print("Корзина пуста.")
				else:
					print("\n--- Ваша корзина ---")
					for id_tovara, el in korzina.elementy.items():
						print(
							f"[ID: {id_tovara}] {el.tovar.nazvanie}: "
							f"{el.kolichestvo} шт. = {el.poluchit_summu()} тенге"
						)
					print(
						f"ИТОГО: {korzina.poluchit_obshuyu_tsenu()} тенге"
					)

			elif vybor == "4":
				t_id = input("Введите ID товара для удаления: ")
				client.poluchit_korzinu().udalit_element(t_id)
				print(f"Товар с ID {t_id} удален из корзины.")

			elif vybor == "5":
				order = shop.oformit_zakaz(client)
				print("\n!!! ЗАКАЗ УСПЕШНО ОФОРМЛЕН !!!")
				details = order.poluchit_detali()
				for k, v in details.items():
					print(f"{k}: {v}")

				clients[name]["cart"] = []
				save_clients(clients)

			elif vybor == "6":
				current_cart = client.poluchit_korzinu().to_list()
				clients[name]["cart"] = current_cart
				save_clients(clients)
				print("Корзина сохранена. До свидания.")
				break

			elif vybor == "7":
				print("До свидания.")
				break

			else:
				print("Неверный выбор, попробуйте снова.")

		except ShopException as e:
			print(f"\n[ОШИБКА МАГАЗИНА]: {e}")
		except ValueError:
			print("\n[ОШИБКА]: Введены некорректные данные.")
		except Exception as e:
			print(f"\n[НЕИЗВЕСТНАЯ ОШИБКА]: {e}")


if __name__ == "__main__":
	main()
