import unittest
import types
import os
import re
from datetime import datetime
from parameterized import parameterized


# ============================================================
# Задание 1.1: flat_generator (любой уровень вложенности)
# Взято из ДЗ "Итераторы, генераторы" (задание 4*)
# print -> return (тут yield, по факту уже return через генератор)
# ============================================================

def flat_generator(list_of_list):
    """Разворачивает список любой вложенности"""
    for elem in list_of_list:
        if isinstance(elem, list):
            yield from flat_generator(elem)
        else:
            yield elem


# ============================================================
# Задание 1.2: logger (декоратор с параметром)
# Взято из ДЗ "Декораторы" (задание 1-2)
# ============================================================

def logger(arg):
    """Декоратор для логирования вызовов функций"""
    if callable(arg):
        old_function = arg

        def new_function(*args, **kwargs):
            now = datetime.now()
            result = old_function(*args, **kwargs)
            with open('main.log', 'a') as f:
                f.write(
                    f'Date: {now.strftime("%Y-%m-%d")}, '
                    f'Time: {now.strftime("%H:%M:%S")}, '
                    f'Function: {old_function.__name__}, '
                    f'Arguments: {args}, '
                    f'Kwargs: {kwargs}, '
                    f'Return: {result}\n'
                )
            return result

        return new_function
    else:
        path = arg

        def __logger(old_function):
            def new_function(*args, **kwargs):
                now = datetime.now()
                result = old_function(*args, **kwargs)
                with open(path, 'a') as f:
                    f.write(
                        f'Date: {now.strftime("%Y-%m-%d")}, '
                        f'Time: {now.strftime("%H:%M:%S")}, '
                        f'Function: {old_function.__name__}, '
                        f'Arguments: {args}, '
                        f'Kwargs: {kwargs}, '
                        f'Return: {result}\n'
                    )
                return result

            return new_function

        return __logger


# ============================================================
# Задание 1.3: clean_phones (форматирование номеров)
# Взято из ДЗ "Регулярные выражения"
# Переделана под работу с одной строкой вместо списка
# ============================================================

def format_phone_number(phone):
    """Приводит номер телефона к формату +7(XXX)XXX-XX-XX"""
    if not phone or not phone.strip():
        return phone

    pattern = (
        r"(\+7|8)?[\s-]*"
        r"\(?(\d{3})\)?[\s-]*"
        r"(\d{3})[\s-]*"
        r"(\d{2})[\s-]*"
        r"(\d{2})"
        r"(?:\s*(?:доб\.?|ext\.?)\s*(\d+))?"
    )

    def _format(m):
        code = m.group(2)
        part1 = m.group(3)
        part2 = m.group(4)
        part3 = m.group(5)
        ext = m.group(6)
        formatted = f"+7({code}){part1}-{part2}-{part3}"
        if ext:
            formatted += f" доб.{ext}"
        return formatted

    result = re.sub(pattern, _format, phone.strip())
    return result


# ============================================================
# ТЕСТЫ
# ============================================================

class TestFlatGenerator(unittest.TestCase):
    """Тесты для flat_generator — разворачивание вложенных списков"""

    def setUp(self):
        self.deep_data = [
            [['a'], ['b', 'c']],
            ['d', 'e', [['f'], 'h'], False],
            [1, 2, None, [[[[['!']]]]], []]
        ]
        self.expected = ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None, '!']

    def test_flat_generator_simple(self):
        """Простой список с одним уровнем вложенности"""
        data = [['a', 'b'], ['c', 'd']]
        result = list(flat_generator(data))
        self.assertEqual(result, ['a', 'b', 'c', 'd'])

    def test_flat_generator_nested(self):
        """Список с глубокой вложенностью"""
        result = list(flat_generator(self.deep_data))
        self.assertEqual(result, self.expected)

    def test_flat_generator_empty_lists(self):
        """Список содержит пустые списки"""
        data = [[], ['a'], [], ['b'], []]
        result = list(flat_generator(data))
        self.assertEqual(result, ['a', 'b'])

    def test_flat_generator_mixed_types(self):
        """Разные типы данных: строки, числа, None, bool"""
        data = [[1, 'two'], [None, False], [3.0]]
        result = list(flat_generator(data))
        self.assertEqual(result, [1, 'two', None, False, 3.0])

    def test_flat_generator_deep_nesting(self):
        """Глубокий уровень вложенности [[[[['!']]]]]"""
        data = [[[[['!']]]]]
        result = list(flat_generator(data))
        self.assertEqual(result, ['!'])

    def test_flat_generator_returns_generator(self):
        """Проверка, что функция возвращает генератор"""
        gen = flat_generator([['a'], ['b']])
        self.assertTrue(isinstance(gen, types.GeneratorType))

    @parameterized.expand([
        ([[1, 2], [3, 4]], [1, 2, 3, 4], "два списка по 2 элемента"),
        ([['x'], ['y', 'z']], ['x', 'y', 'z'], "списки разной длины"),
        ([[], [1]], [1], "первый список пустой"),
        ([[1], []], [1], "второй список пустой"),
        ([['deep', ['deeper', ['deepest']]]], ['deep', 'deeper', 'deepest'], "3 уровня вложенности"),
        ([], [], "пустой входной список"),
    ])
    def test_flat_generator_parametrized(self, input_data, expected, desc):
        """Параметризованный тест для разных случаев"""
        with self.subTest(desc=desc):
            result = list(flat_generator(input_data))
            self.assertEqual(result, expected)


class TestLoggerDecorator(unittest.TestCase):
    """Тесты для декоратора logger"""

    def setUp(self):
        # удаляем старые лог-файлы перед каждым тестом
        for f in ['main.log', 'test_custom.log', 'test_sum.log', 'test_div.log']:
            if os.path.exists(f):
                os.remove(f)

    def tearDown(self):
        # чистим за собой
        for f in ['main.log', 'test_custom.log', 'test_sum.log', 'test_div.log']:
            if os.path.exists(f):
                os.remove(f)

    def test_logger_default_path(self):
        """Декоратор без аргумента пишет в main.log"""
        @logger
        def hello():
            return 'Hello World'

        hello()
        self.assertTrue(os.path.exists('main.log'))

    def test_logger_custom_path(self):
        """Декоратор с аргументом пишет в указанный файл"""
        @logger('test_custom.log')
        def hello():
            return 'Hello World'

        hello()
        self.assertTrue(os.path.exists('test_custom.log'))

    def test_log_content(self):
        """В логе есть дата, время, имя функции, аргументы, результат"""
        @logger
        def summator(a, b=0):
            return a + b

        summator(2, 3)
        with open('main.log') as f:
            content = f.read()

        self.assertIn('Date:', content)
        self.assertIn('Function: summator', content)
        self.assertIn('Arguments: (2, 3)', content)
        self.assertIn('Return: 5', content)

    def test_sum_int(self):
        """Декорированная summator с целыми числами"""
        @logger
        def summator(a, b=0):
            return a + b

        result = summator(2, 2)
        self.assertEqual(result, 4)

    def test_sum_float(self):
        """Декорированная summator с дробными числами"""
        @logger
        def summator(a, b=0):
            return a + b

        result = summator(4.3, b=2.2)
        self.assertAlmostEqual(result, 6.5)

    def test_div(self):
        """Декорированная div работает верно"""
        @logger
        def div(a, b):
            return a / b

        result = div(6, 2)
        self.assertEqual(result, 3)

    def test_div_by_zero(self):
        """Декорированная div с делением на 0 — должно быть исключение"""
        @logger
        def div(a, b):
            return a / b

        with self.assertRaises(ZeroDivisionError):
            div(1, 0)

    @parameterized.expand([
        (2, 3, 5, "целые положительные"),
        (-1, 1, 0, "отрицательное + положительное"),
        (0, 0, 0, "два нуля"),
        (1.5, 2.5, 4.0, "дробные числа"),
        (10, -5, 5, "положительное + отрицательное"),
    ])
    def test_sum_parametrized(self, a, b, expected, desc):
        """Параметризованный тест summator с разными аргументами"""
        @logger
        def summator(x, y=0):
            return x + y

        result = summator(a, b)
        self.assertEqual(result, expected)


class TestCleanPhones(unittest.TestCase):
    """Тесты для format_phone_number — форматирование номеров телефонов"""

    def test_standard_phone(self):
        """Стандартный номер +7(123)456-78-90"""
        result = format_phone_number('+7(123)456-78-90')
        self.assertEqual(result, '+7(123)456-78-90')

    def test_phone_with_eight(self):
        """Номер начинается с 8 вместо +7"""
        result = format_phone_number('8(123)456-78-90')
        self.assertEqual(result, '+7(123)456-78-90')

    def test_phone_without_parentheses(self):
        """Номер без скобок"""
        result = format_phone_number('+7 123 456 78 90')
        self.assertEqual(result, '+7(123)456-78-90')

    def test_phone_with_dashes(self):
        """Номер с тире в разных местах"""
        result = format_phone_number('+7-123-456-78-90')
        self.assertEqual(result, '+7(123)456-78-90')

    def test_phone_with_extension_dob(self):
        """Номер с добавочным через доб."""
        result = format_phone_number('+7(123)456-78-90 доб.1234')
        self.assertEqual(result, '+7(123)456-78-90 доб.1234')

    def test_phone_with_ext_variation(self):
        """Номер с добавочным через ext."""
        result = format_phone_number('+7(123)456-78-90 ext.567')
        self.assertEqual(result, '+7(123)456-78-90 доб.567')

    def test_empty_phone(self):
        """Пустая строка — возвращается как есть"""
        result = format_phone_number('')
        self.assertEqual(result, '')

    def test_none_phone(self):
        """None — возвращается как есть"""
        result = format_phone_number(None)
        self.assertIsNone(result)

    def test_invalid_phone(self):
        """Невалидный номер (слишком короткий) — не меняется"""
        result = format_phone_number('12345')
        self.assertEqual(result, '12345')

    @parameterized.expand([
        ('8 999 111 22 33', '+7(999)111-22-33', "восьмёрка с пробелами"),
        ('8(999)111-22-33', '+7(999)111-22-33', "восьмёрка со скобками и тире"),
        ('+7 999 111 22 33', '+7(999)111-22-33', "+7 с пробелами"),
        ('+7-999-111-22-33', '+7(999)111-22-33', "+7 с тире"),
        ('+7(999)1112233', '+7(999)111-22-33', "номер слитно"),
        ('8(999)111-22-33 доб.456', '+7(999)111-22-33 доб.456', "с добавочным"),
        ('+7(999)111-22-33 доб 789', '+7(999)111-22-33 доб.789', "доб без точки"),
    ])
    def test_phone_parametrized(self, input_phone, expected, desc):
        """Параметризованный тест разных форматов номеров"""
        result = format_phone_number(input_phone)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()