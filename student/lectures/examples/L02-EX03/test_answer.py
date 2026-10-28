"""Поведенческая проверка учебной функции."""

import unittest

from bad import answer


class AnswerTests(unittest.TestCase):
    def test_answer_is_42(self) -> None:
        self.assertEqual(answer(), 42)


if __name__ == "__main__":
    unittest.main()
