"""

"""

import unittest
import random
import re
import string
import unittest
from unittest.mock import patch

import pytest

from coffee import (
    get_price,
    calculate_order_total,
    get_most_expensive_drink,
    generate_wifi_password,
    format_receipt,
    MENU
)   

# Example
# ============================================================
# get_price
# ============================================================
class GetPriceTest(unittest.TestCase):
    # ---------- позитивные ----------
    def test_known_drinks(self):
        self.assertEqual(get_price("espresso"), 150)
        self.assertEqual(get_price("latte"), 280)
        self.assertEqual(get_price("tea"), 120)

    def test_all_menu_items(self):
        for name, price in MENU.items():
            with self.subTest(drink=name):
                self.assertEqual(get_price(name), price)

    def test_returns_int(self):
        result = get_price("latte")
        self.assertIsInstance(result, int)
        self.assertNotIsInstance(result, bool)

    # ---------- негативные ----------
    def test_unknown_drink_raises(self):
        with self.assertRaises(ValueError):
            get_price("mocha")

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            get_price("")

    def test_none_raises(self):
        with self.assertRaises(ValueError):
            get_price(None)

    def test_case_sensitive(self):
        # "Latte" с заглавной — не в MENU
        with self.assertRaises(ValueError):
            get_price("Latte")

    def test_error_message_contains_drink(self):
        with self.assertRaisesRegex(ValueError, "mocha"):
            get_price("mocha")

    # ---------- границы ----------
    def test_whitespace_not_stripped(self):
        with self.assertRaises(ValueError):
            get_price(" latte ")

    def test_number_as_name_raises(self):
        with self.assertRaises(ValueError):
            get_price(123)


# ============================================================
# calculate_order_total
# ============================================================
class CalculateOrderTotalTest(unittest.TestCase):
    # ---------- позитивные ----------
    def test_single_item(self):
        self.assertEqual(calculate_order_total(1, 280), 280)

    def test_typical(self):
        self.assertEqual(calculate_order_total(5, 280), 1400)

    def test_zero_quantity(self):
        self.assertEqual(calculate_order_total(0, 280), 0)

    def test_large_quantity(self):
        self.assertEqual(calculate_order_total(1000, 150), 150000)

    def test_zero_price(self):
        self.assertEqual(calculate_order_total(5, 0), 0)

    def test_result_is_int(self):
        self.assertIsInstance(calculate_order_total(3, 100), int)

    def test_commutative(self):
        self.assertEqual(
            calculate_order_total(3, 100),
            calculate_order_total(100, 3),
        )

    # ---------- негативные ----------
    def test_negative_quantity_raises(self):
        # В текущем коде НЕТ валидации → тест падает (баг)
        with self.assertRaises(ValueError):
            calculate_order_total(-1, 280)

    def test_negative_price_raises(self):
        with self.assertRaises(ValueError):
            calculate_order_total(5, -100)

    def test_string_quantity_raises(self):
        with self.assertRaises(TypeError):
            calculate_order_total("5", 280)

    def test_string_price_raises(self):
        with self.assertRaises(TypeError):
            calculate_order_total(5, "280")

    def test_none_raises(self):
        with self.assertRaises(TypeError):
            calculate_order_total(None, 280)

    def test_float_quantity(self):
        # Фиксируем текущее поведение (дробное допустимо → float)
        result = calculate_order_total(1.5, 280)
        self.assertEqual(result, 420.0)
        self.assertIsInstance(result, float)


# ============================================================
# get_most_expensive_drink
# ============================================================
class GetMostExpensiveDrinkTest(unittest.TestCase):
    # ---------- позитивные ----------
    def test_returns_latte(self):
        # БАГ в исходнике: используется min, поэтому вернётся tea.
        # Тест фиксирует ОЖИДАЕМОЕ поведение, поэтому должен падать.
        name, price = get_most_expensive_drink()
        self.assertEqual(name, "latte")
        self.assertEqual(price, 280)

    def test_returns_tuple(self):
        result = get_most_expensive_drink()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_types_in_result(self):
        name, price = get_most_expensive_drink()
        self.assertIsInstance(name, str)
        self.assertIsInstance(price, int)

    def test_price_is_max(self):
        name, price = get_most_expensive_drink()
        self.assertEqual(price, max(MENU.values()))
        self.assertEqual(MENU[name], price)

    def test_name_in_menu(self):
        name, _ = get_most_expensive_drink()
        self.assertIn(name, MENU)

    # ---------- границы ----------
    def test_single_item_menu(self):
        with patch.dict("coffee.MENU", {"only": 100}, clear=True):
            self.assertEqual(get_most_expensive_drink(), ("only", 100))

    def test_tied_max_prices(self):
        with patch.dict("coffee.MENU", {"a": 100, "b": 100, "c": 50}, clear=True):
            name, price = get_most_expensive_drink()
            self.assertIn(name, ("a", "b"))
            self.assertEqual(price, 100)

    def test_empty_menu_raises(self):
        # min() на пустом словаре бросает ValueError — фиксируем
        with patch.dict("coffee.MENU", {}, clear=True):
            with self.assertRaises(ValueError):
                get_most_expensive_drink()


# ============================================================
# generate_wifi_password
# ============================================================
class GenerateWifiPasswordTest(unittest.TestCase):
    # ---------- позитивные ----------
    def test_default_length(self):
        pwd = generate_wifi_password()
        self.assertEqual(len(pwd), 8)

    def test_custom_length_8(self):
        self.assertEqual(len(generate_wifi_password(8)), 8)

    def test_custom_length_12(self):
        self.assertEqual(len(generate_wifi_password(12)), 12)

    def test_custom_length_50(self):
        self.assertEqual(len(generate_wifi_password(50)), 50)

    def test_returns_string(self):
        self.assertIsInstance(generate_wifi_password(), str)

    def test_only_allowed_chars(self):
        allowed = set(string.ascii_letters + string.digits)
        pwd = generate_wifi_password(30)
        self.assertTrue(set(pwd).issubset(allowed))

    def test_has_lowercase(self):
        pwd = generate_wifi_password(20)
        self.assertTrue(any(c.islower() for c in pwd))

    def test_has_uppercase(self):
        pwd = generate_wifi_password(20)
        self.assertTrue(any(c.isupper() for c in pwd))

    def test_has_digit(self):
        pwd = generate_wifi_password(20)
        self.assertTrue(any(c.isdigit() for c in pwd))

    def test_passwords_unique(self):
        # недетерминированность — два подряд не совпадают (практически всегда)
        self.assertNotEqual(generate_wifi_password(16), generate_wifi_password(16))

    def test_contains_at_least_one_of_each_type(self):
        for _ in range(20):
            pwd = generate_wifi_password(10)
            self.assertTrue(any(c.islower() for c in pwd))
            self.assertTrue(any(c.isupper() for c in pwd))
            self.assertTrue(any(c.isdigit() for c in pwd))

    def test_with_seeded_random(self):
        random.seed(42)
        pwd1 = generate_wifi_password(8)
        random.seed(42)
        pwd2 = generate_wifi_password(8)
        self.assertEqual(pwd1, pwd2)

    # ---------- негативные ----------
    def test_length_7_raises(self):
        with self.assertRaises(ValueError):
            generate_wifi_password(7)

    def test_length_0_raises(self):
        with self.assertRaises(ValueError):
            generate_wifi_password(0)

    def test_negative_length_raises(self):
        with self.assertRaises(ValueError):
            generate_wifi_password(-5)

    def test_float_length_raises(self):
        # range(8.5 - 3) → TypeError
        with self.assertRaises(TypeError):
            generate_wifi_password(8.5)

    def test_string_length_raises(self):
        # "8" < 8 → TypeError на сравнении
        with self.assertRaises(TypeError):
            generate_wifi_password("8")

    def test_none_length_raises(self):
        with self.assertRaises(TypeError):
            generate_wifi_password(None)

    def test_error_message(self):
        with self.assertRaisesRegex(ValueError, "Длина пароля"):
            generate_wifi_password(3)


# ============================================================
# format_receipt
# ============================================================
class FormatReceiptTest(unittest.TestCase):
    # ---------- позитивные ----------
    def test_latte_one(self):
        receipt = format_receipt("latte", 1)
        self.assertIn("Напиток: latte", receipt)
        self.assertIn("Количество: 1", receipt)
        self.assertIn("Итого: 280 руб.", receipt)

    def test_espresso_three(self):
        receipt = format_receipt("espresso", 3)
        self.assertIn("Итого: 450 руб.", receipt)

    def test_zero_quantity(self):
        receipt = format_receipt("tea", 0)
        self.assertIn("Итого: 0 руб.", receipt)

    def test_returns_string(self):
        self.assertIsInstance(format_receipt("latte", 1), str)

    def test_header_present(self):
        receipt = format_receipt("latte", 1)
        self.assertIn("Чек", receipt)

    def test_regex_format(self):
        receipt = format_receipt("latte", 2)
        pattern = re.compile(
            r"Напиток:\s+(?P<drink>\w+).*?"
            r"Количество:\s+(?P<qty>\d+).*?"
            r"Итого:\s+(?P<total>\d+)\s+руб\.",
            re.DOTALL,
        )
        m = pattern.search(receipt)
        self.assertIsNotNone(m)
        self.assertEqual(m.group("drink"), "latte")
        self.assertEqual(int(m.group("qty")), 2)
        self.assertEqual(int(m.group("total")), 560)

    def test_total_matches_formula(self):
        for drink, qty in [("latte", 3), ("tea", 5), ("espresso", 1)]:
            with self.subTest(drink=drink, qty=qty):
                receipt = format_receipt(drink, qty)
                m = re.search(r"Итого:\s+(\d+)\s+руб\.", receipt)
                self.assertIsNotNone(m)
                self.assertEqual(int(m.group(1)), get_price(drink) * qty)

    # ---------- негативные ----------
    def test_unknown_drink_raises(self):
        with self.assertRaises(ValueError):
            format_receipt("mocha", 1)

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            format_receipt("", 1)

    def test_none_name_raises(self):
        with self.assertRaises(ValueError):
            format_receipt(None, 1)

    def test_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            format_receipt("latte", -1)

    def test_string_quantity_raises(self):
        with self.assertRaises(TypeError):
            format_receipt("latte", "2")

    def test_float_quantity_current_behavior(self):
        # В текущем коде дробное количество проходит, итог дробный → фиксируем
        receipt = format_receipt("latte", 1.5)
        self.assertIn("Итого: 420.0 руб.", receipt)

    def test_error_message_contains_drink(self):
        with self.assertRaisesRegex(ValueError, "mocha"):
            format_receipt("mocha", 1)


# ============================================================
# Интеграционные / сквозные сценарии
# ============================================================
class IntegrationTest(unittest.TestCase):
    def test_price_total_receipt_consistency(self):
        price = get_price("latte")
        total = calculate_order_total(3, price)
        self.assertEqual(total, 840)
        receipt = format_receipt("latte", 3)
        self.assertIn(f"Итого: {total} руб.", receipt)

    def test_generate_then_validate(self):
        pwd = generate_wifi_password(12)
        self.assertEqual(len(pwd), 12)
        self.assertRegex(pwd, r"^[A-Za-z0-9]+$")
        self.assertTrue(any(c.islower() for c in pwd))
        self.assertTrue(any(c.isupper() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))


# ============================================================
# Параметризованные тесты (pytest)
# ============================================================
@pytest.mark.parametrize("bad_length", [7, 0, -1, -100, 3])
def test_wifi_password_invalid_lengths_param(bad_length):
    with pytest.raises(ValueError):
        generate_wifi_password(bad_length)


@pytest.mark.parametrize("bad_value", [8.5, "8", None, [8], {"a": 1}])
def test_wifi_password_bad_types_param(bad_value):
    with pytest.raises((TypeError, ValueError)):
        generate_wifi_password(bad_value)


@pytest.mark.parametrize("drink", ["mocha", "", "Latte", "LATTE", None, 123])
def test_get_price_unknown_param(drink):
    with pytest.raises(ValueError):
        get_price(drink)


@pytest.mark.parametrize("qty,price", [(-1, 280), (5, -100), (-5, -100)])
def test_calculate_total_negative_param(qty, price):
    with pytest.raises(ValueError):
        calculate_order_total(qty, price)


@pytest.mark.parametrize("drink,qty,expected", [
    ("latte", 1, 280),
    ("espresso", 3, 450),
    ("tea", 5, 600),
    ("americano", 0, 0),
])
def test_receipt_total_param(drink, qty, expected):
    receipt = format_receipt(drink, qty)
    m = re.search(r"Итого:\s+(\d+)\s+руб\.", receipt)
    assert m is not None
    assert int(m.group(1)) == expected


if __name__ == "__main__":
    unittest.main()