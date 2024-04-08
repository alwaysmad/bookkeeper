"""
Модель бюджета
"""

from dataclasses import dataclass


@dataclass
class Budget:
    """
    Бюджет содержит срок (term), сумму (summa) и категорию расходов (category)
    """
    summa: float = 0
    term: int = 0
    category: str = ""
    pk: int = 0
