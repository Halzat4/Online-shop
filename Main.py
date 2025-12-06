from typing import List, Dict
from Models import Pokupatel
from Store import Magazin, zapolnit_magazin, pokazat_tovary, restore_cart
from Exceptions import ShopException, InvalidDataException
from Clients import load_clients, save_clients

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
                restore_cart(client, stored.get("cart", []), shop)
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
                clients[name] = {"id": new_id, "kontakty": contact, "cart": []}
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
                        print(f"[ID: {id_tovara}] {el.tovar.nazvanie}: "
                              f"{el.kolichestvo} шт. = {el.poluchit_summu()} тенге")
                    print(f"ИТОГО: {korzina.poluchit_obshuyu_tsenu()} тенге")
            elif vybor == "4":
                t_id = input("Введите ID товара для удаления: ")
                client.poluchit_korzinu().udalit_element(t_id)
                print(f"Товар с ID {t_id} удален из корзины.")
            elif vybor == "5":
                order = shop.oformit_zakaz(client)
                print("\n!!! ЗАКАЗ УСПЕШНО ОФОРМЛЕН !!!")
                for k, v in order.poluchit_detali().items():
                    print(f"{k}: {v}")
                clients[name]["cart"] = []
                save_clients(clients)
            elif vybor == "6":
                clients[name]["cart"] = client.poluchit_korzinu().to_list()
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
