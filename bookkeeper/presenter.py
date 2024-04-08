"""
Основной скрипт проекта
Создает Bookkeeper, прикрепляет базу данных, запускает графический интерфейс
"""
import sys

from typing import Protocol, Callable
from datetime import datetime, timedelta, date
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.view.app_window import MainWindow
from bookkeeper.repository.sqlite_repository import SQliteRepository
from bookkeeper.repository.abstract_repository import AbstractRepository


class AbstractView(Protocol):
    """
    Интерфейс, котороый нужен для окна
    """
    def __init__(self) -> None:
        pass

    def init_ui(self) -> None:
        """
        Нужна для инициализации окна
        """

    def expense_change_handler(
        self, handler: Callable[[int, str, datetime, str, int], None]
    ) -> None:
        """
        Изменяет некоторые параметры записи расходов
        """

    def expense_add_handler(
        self, handler: Callable[[int, str, datetime], None]
    ) -> None:
        """
        Добавляет новую запись расходов
        """

    def delete_category_handler(self, handler: Callable[[str], None]) -> None:
        """
        Удаляет категорию из списка категорий
        """

    def add_category_handler(self, handler: Callable[[Category], None]) -> None:
        """
        Добавляет новую категорию в список категорий
        """

    def budget_change_handler(self, handler: Callable[[Budget], None]) -> None:
        """
        Изменяет установленный бюджет на период
        """

    def set_budget(self, budgets: list[Budget]) -> None:
        """
        Меняет список бюджетов
        """

    def set_categories(self, categories: list[Category]) -> None:
        """
        Меняет список категорий
        """

    def set_expense_list(
        self,
        expenses: list[Expense],
        categories: dict[int, str],
    ) -> None:
        pass

    def set_summ(self, summs: list[float]) -> None:
        pass

    def do_show(self) -> None:
        pass

    def clear_expense_table(self) -> None:
        pass


class Bookkeeper:

    def __init__(
        self,
        view: AbstractView,
        category_repository: AbstractRepository[Category],
        budget_repository: AbstractRepository[Budget],
        expense_repository: AbstractRepository[Expense],
    ) -> None:
        self.day_budg = 1000
        self.week_budg = 7000
        self.month_budg = 30000
        self.budgets: list[Budget]

        self.month_summ = 0
        self.week_summ = 0
        self.day_summ = 0

        self.view = view
        self.category_repository = category_repository
        self.expense_repository = expense_repository
        self.budget_repository = budget_repository

        self.view.expense_change_handler(self.change_expense)
        self.view.expense_add_handler(self.add_expense)
        self.view.delete_category_handler(self.delete_category)
        self.view.add_category_handler(self.add_category)
        self.view.budget_change_handler(self.budget_change)
        self.view.init_ui()

        self.set_budget()
        self.set_categories()
        self.set_expense_list()
        self.set_summ()
        self.view.do_show()

    def set_budget(self) -> None:
        self.budgets = self.budget_repository.get_all()
        if not self.budgets:
            budg_for_day = Budget(self.day_budg, 1)
            budg_for_week = Budget(self.week_budg, 7)
            budg_for_month = Budget(self.month_budg, 30)
            self.budgets = [budg_for_day, budg_for_week, budg_for_month]
            for budgs in self.budgets:
                self.budget_repository.add(budgs)
        self.view.set_budget(self.budgets)

    def set_categories(self) -> None:
        categories = self.category_repository.get_all()
        if not categories:
            categories = [Category("Продукты"), Category("Дом"), Category("Прочее")]
            for cat in categories:
                self.category_repository.add(cat)
        self.view.set_categories(categories)

    def set_expense_list(self) -> None:
        self.view.clear_expense_table()
        expenses = self.expense_repository.get_all()
        cat_list = self.category_repository.get_all()
        categories = {}
        for item in cat_list:
            categories[item.pk] = item.name
        self.view.set_expense_list(expenses, categories)

    def set_summ(self) -> None:
        self.day_summ = 0
        self.week_summ = 0
        self.month_summ = 0
        expenses = self.expense_repository.get_all()
        if expenses:
            today = date.today()
            week = today - timedelta(7)
            month = today - timedelta(31)
            for exp in expenses:
                exp_date = exp.expense_date.date()
                if exp_date >= month:
                    self.month_summ += exp.amount
                if exp_date >= week:
                    self.week_summ += exp.amount
                if exp_date >= today:
                    self.day_summ += exp.amount
        summs = list(map(float, [self.day_summ, self.week_summ, self.month_summ]))
        self.view.set_summ(summs)

    def change_expense(
        self,
        amount: int,
        cat: str,
        datetime_: datetime,
        com: str,
        pk: int,
    ) -> None:
        if cat == "Удаленная категория":
            prim_key = 0
        else:
            cat_list = self.category_repository.get_all({"name": cat})
            assert len(cat_list) == 1
            prim_key = cat_list[0].pk
        exp = Expense(amount, prim_key, datetime_, comment=com, pk=pk)
        self.expense_repository.update(exp)
        self.set_summ()

    def add_expense(self, amount: int, cat: str, datetime_: datetime) -> None:
        cat_list = self.category_repository.get_all({"name": cat})
        assert len(cat_list) == 1
        prim_key = cat_list[0].pk
        exp = Expense(amount, prim_key, datetime_)
        self.expense_repository.add(exp)
        self.set_summ()

    def delete_category(self, name: str) -> None:
        cat_list = self.category_repository.get_all({"name": name})
        assert len(cat_list) == 1
        prim_key = cat_list[0].pk
        self.category_repository.delete(prim_key)
        self.set_expense_list()
        expenses = self.expense_repository.get_all()
        for exp in expenses:
            if exp.category == prim_key:
                upd_exp = Expense(
                    exp.amount, 0, exp.expense_date, comment=exp.comment, pk=exp.pk
                )
                self.expense_repository.update(upd_exp)

    def add_category(self, cat: Category) -> None:
        self.category_repository.add(cat)

    def budget_change(self, budg: Budget) -> None:
        self.budget_repository.update(budg)


def main() -> int:
    main_window = MainWindow()
    cat_repo = SQliteRepository[Category]("bookkeper.db", Category)
    budget_repo = SQliteRepository[Budget]("bookkeper.db", Budget)
    expense_repo = SQliteRepository[Expense]("bookkeper.db", Expense)

    Bookkeeper(main_window, cat_repo, budget_repo, expense_repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
