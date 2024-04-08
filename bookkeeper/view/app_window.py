# pylint: disable-all
"""
Окно приложения
"""

import sys
import datetime
from PySide6 import QtWidgets, QtCore
from typing import Callable
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget


def check_float(text: str) -> float | None:
    """
    Проверка строчки на то, является ли она числом
    """
    try:
        return float(text)
    except ValueError:
        return None


class CategoryChangeWindow(QtWidgets.QWidget):
    """
    Окно, меняющее категорию записи в расходах
    """

    def __init__(self, parent: "MainWindow", categoryes: list[str], ro: int, col: int):
        super().__init__()
        self.par = parent
        self.categoryes = categoryes
        self.ro = ro
        self.col = col
        self._correct_category_inlist()
        self.layer: QtWidgets.QGridLayout
        self.combo_cor: QtWidgets.QComboBox

    def _correct_category_inlist(self) -> None:
        ok_button = QtWidgets.QPushButton("Ок")
        invite_label = QtWidgets.QLabel("Выберите категорию")
        self.layer = QtWidgets.QGridLayout()
        self.layer.addWidget(invite_label, 0, 0)
        self.layer.addWidget(self._category_combo(), 1, 0)
        self.layer.addWidget(ok_button, 2, 0)
        self.setLayout(self.layer)

        ok_button.clicked.connect(self._on_ok_button_click)

    def _category_combo(self) -> QtWidgets.QWidget:
        self.combo_cor = QtWidgets.QComboBox()
        for i in self.categoryes:
            self.combo_cor.addItem(f"{i}")
        return self.combo_cor

    def _on_ok_button_click(self) -> None:
        text = self.combo_cor.currentText()
        self.par.expenses_table.setItem(
            self.ro,
            self.col,
            QtWidgets.QTableWidgetItem(text),
        )
        summ = int(self.par.expenses_table.item(self.ro, 1).text())
        cat = text
        date = datetime.datetime.strptime(
            self.par.expenses_table.item(self.ro, 0).text(), "%Y-%m-%d %H:%M:%S"
        )
        comm = self.par.expenses_table.item(self.ro, 3)
        if comm is None:
            comment = ""
        else:
            comment = comm.text()
        self.par.handler_expense_changer(
            summ,
            cat,
            date,
            comment,
            self.ro + 1,
        )


class CategoryWindow(QtWidgets.QWidget):
    """
    Окно изменения списка категорий: добавления в список и удаления из списка
    """

    def __init__(self, parent: "MainWindow", categoryes: list[str]):
        super().__init__()
        self.par = parent
        self.categoryes = categoryes
        self._correct_category()
        self.layer: QtWidgets.QGridLayout
        self.success_add_label: QtWidgets.QLabel
        self.success_del_label: QtWidgets.QLabel

    def _correct_category(self) -> None:
        delete_button = QtWidgets.QPushButton("Удалить категорию")
        plus_button = QtWidgets.QPushButton("Добавить категорию")
        self.success_del_label = QtWidgets.QLabel(" ")
        self.success_add_label = QtWidgets.QLabel(" ")
        self.layer = QtWidgets.QGridLayout()
        self.layer.addWidget(delete_button, 0, 1)
        self.layer.addWidget(self._category_combo_edit(), 0, 0)
        self.layer.addWidget(self.success_del_label, 1, 0)
        self.layer.addWidget(plus_button, 2, 1)
        self.layer.addWidget(self._category_input(), 2, 0)
        self.layer.addWidget(self.success_add_label, 3, 0)
        self.setLayout(self.layer)

        delete_button.clicked.connect(self._on_delete_button_click)
        plus_button.clicked.connect(self._on_plus_button_click)

        # self.setWindowTitle("Редактирование категорий")
        self.setGeometry(300, 100, 600, 200)

    def _on_delete_button_click(self) -> None:
        text = self.combo_edit.currentText()
        self.combo_edit.removeItem(self.combo_edit.currentIndex())
        count = self.combo_edit.count()
        categoryes = [self.combo_edit.itemText(i) for i in range(count)]
        self.par.delete_category(categoryes=categoryes)
        self.success_del_label.setText(f'категория "{text}" удалена')
        self.layer.addWidget(self.success_del_label, 1, 0, 1, -1)
        self.par.handler_del(text)

    def _on_plus_button_click(self) -> None:
        text = self.category_input_field.text()
        count = self.combo_edit.count()
        categoryes = [self.combo_edit.itemText(i) for i in range(count)]
        if text not in categoryes:
            self.combo_edit.addItem(text)
            self.par.add_category(str(text))
            self.success_add_label.setText(f'категория "{text}" добавлена')
            self.layer.addWidget(self.success_add_label, 3, 0, 1, -1)
            self.par.handler_add(Category(text))
        else:
            self.success_add_label.setText(f'категория "{text}" уже существует')
            self.layer.addWidget(self.success_add_label, 3, 0, 1, -1)

    def _category_combo_edit(self) -> QtWidgets.QWidget:
        self.combo_edit = QtWidgets.QComboBox()
        for i in self.categoryes:
            self.combo_edit.addItem(f"{i}")
        return self.combo_edit

    def _category_input(self) -> QtWidgets.QLineEdit:
        self.category_input_field = QtWidgets.QLineEdit("Введите новую категорию")
        return self.category_input_field


class DayChangeWindow(QtWidgets.QWidget):
    """
    Окно изменения даты расхода в списке
    """

    def __init__(self, parent: "MainWindow", ro: int, col: int):
        super().__init__()
        self.par = parent
        self.ro = ro
        self.col = col
        self._correct_day()

    def _correct_day(self) -> None:
        invite_label = QtWidgets.QLabel("Выберите дату")
        day_label = QtWidgets.QLabel("Введите день")
        month_label = QtWidgets.QLabel("Выберите месяц")
        year_label = QtWidgets.QLabel("Введите год")
        ok_button = QtWidgets.QPushButton("ok")

        self.layer = QtWidgets.QGridLayout()
        self.layer.addWidget(invite_label, 0, 0)
        self.layer.addWidget(day_label, 2, 0)
        self.layer.addWidget(month_label, 1, 0)
        self.layer.addWidget(year_label, 3, 0)
        self.layer.addWidget(self._month_combo(), 1, 1)
        self.layer.addWidget(self._day_input(), 2, 1)
        self.layer.addWidget(self._year_input(), 3, 1)
        self.layer.addWidget(ok_button, 4, 1)

        self.setLayout(self.layer)

        ok_button.clicked.connect(self._on_ok_button_click)

    def _on_ok_button_click(self) -> None:
        day = self.text_day.text()
        month = self.combo_month.currentText()
        year = self.text_year.text()
        if check_float(day) is None or check_float(year) is None:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("День и год должны быть в числовом формате.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()

        elif len(year) != 4:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage(
                'Год должен быть в формате четырех цифр, например, "2024".\n'
            )
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
        try:
            datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("В выбранном месяце нет введенного дня.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
        else:
            date = datetime.datetime(int(year), int(month), int(day))
            self.par.expenses_table.setItem(
                self.ro,
                self.col,
                QtWidgets.QTableWidgetItem(date.strftime("%Y-%m-%d %H:%M:%S")),
            )

            summ = int(self.par.expenses_table.item(self.ro, 1).text())
            cat = self.par.expenses_table.item(self.ro, 2).text()
            comm = self.par.expenses_table.item(self.ro, 3)
            if comm is None:
                comment = ""
            else:
                comment = comm.text()
            self.par.handler_expense_changer(
                summ,
                cat,
                date,
                comment,
                self.ro + 1,
            )

    def _month_combo(self) -> QtWidgets.QWidget:
        self.combo_month = QtWidgets.QComboBox()
        for i in range(1, 13):
            self.combo_month.addItem(f"{i:02}")
        return self.combo_month

    def _day_input(self) -> QtWidgets.QLineEdit:
        self.text_day = QtWidgets.QLineEdit("")
        return self.text_day

    def _year_input(self) -> QtWidgets.QLineEdit:
        self.text_year = QtWidgets.QLineEdit("")
        return self.text_year


class BudgetWindow(QtWidgets.QWidget):
    """
    Окно изменения бюджета
    """

    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.par = parent
        self._correct_budget()

    def _correct_budget(self) -> None:
        renew_day_button = QtWidgets.QPushButton("Обновить бюджет на день")
        renew_week_button = QtWidgets.QPushButton("Обновить бюджет на неделю")
        renew_month_button = QtWidgets.QPushButton("Обновить бюджет на месяц")
        self.success_day_label = QtWidgets.QLabel(" ")
        self.success_week_label = QtWidgets.QLabel(" ")
        self.success_month_label = QtWidgets.QLabel(" ")

        self.day_label = QtWidgets.QLabel("Бюджет на день")
        self.week_label = QtWidgets.QLabel("Бюджет на неделю")
        self.month_label = QtWidgets.QLabel("Бюджет на месяц")

        self.layer = QtWidgets.QGridLayout()
        self.layer.addWidget(renew_day_button, 0, 2)
        self.layer.addWidget(renew_week_button, 2, 2)
        self.layer.addWidget(renew_month_button, 4, 2)
        self.layer.addWidget(self.day_label, 0, 0)
        self.layer.addWidget(self.success_day_label, 1, 0)
        self.layer.addWidget(self.week_label, 2, 0)
        self.layer.addWidget(self.success_week_label, 3, 0)
        self.layer.addWidget(self.month_label, 4, 0)
        self.layer.addWidget(self.success_month_label, 5, 0)
        self.layer.addWidget(self._budget_day_input(), 0, 1)
        self.layer.addWidget(self._budget_week_input(), 2, 1)
        self.layer.addWidget(self._budget_month_input(), 4, 1)

        self.setLayout(self.layer)

        renew_day_button.clicked.connect(self._on_renew_day_button_click)
        renew_week_button.clicked.connect(self._on_renew_week_button_click)
        renew_month_button.clicked.connect(self._on_renew_month_button_click)

        # self.setWindowTitle("Редактирование категорий")
        self.setGeometry(300, 100, 500, 200)

    def _on_renew_day_button_click(self) -> None:
        text_day = self.budget_day_input_field
        if (
            text_day.text() is not None
            and check_float(str(text_day.text())) is not None
        ):
            self.par.control_table.setItem(
                0, 1, QtWidgets.QTableWidgetItem(str(text_day.text()))
            )
            self.success_day_label.setText("Бюджет на день обновлен")
            self.layer.addWidget(self.success_day_label, 1, 0, 1, -1)
            self.par.handler_budget(Budget(float(text_day.text()), 1, pk=1))
        else:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Бюджет на день должен быть в числовом формате.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
            self.success_day_label.setText("")
            self.layer.addWidget(self.success_day_label, 1, 0, 1, -1)

    def _on_renew_week_button_click(self) -> None:
        text_week = self.budget_week_input_field

        if (
            text_week.text() is not None
            and check_float(str(text_week.text())) is not None
        ):
            self.par.control_table.setItem(
                1, 1, QtWidgets.QTableWidgetItem(str(text_week.text()))
            )
            self.success_week_label.setText("Бюджет на неделю обновлен")
            self.par.handler_budget(Budget(float(str(text_week.text())), 7, pk=2))

            self.layer.addWidget(self.success_week_label, 3, 0, 1, -1)
        else:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Бюджет на неделю должен быть в числовом формате.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
            self.success_week_label.setText("")
            self.layer.addWidget(self.success_week_label, 3, 0, 1, -1)

    def _on_renew_month_button_click(self) -> None:
        text_month = self.budget_month_input_field

        if (
            text_month.text() is not None
            and check_float(str(text_month.text())) is not None
        ):
            self.par.control_table.setItem(
                2, 1, QtWidgets.QTableWidgetItem(str(text_month.text()))
            )
            self.par.handler_budget(Budget(float(str(text_month.text())), 31, pk=3))
            self.success_month_label.setText("Бюджет на месяц обновлен")
            self.layer.addWidget(self.success_month_label, 5, 0, 1, -1)
        else:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Бюджет на месяц должен быть в числовом формате.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
            self.success_month_label.setText("")
            self.layer.addWidget(self.success_month_label, 5, 0, 1, -1)

    def _budget_day_input(self) -> QtWidgets.QLineEdit:
        self.budget_day_input_field = QtWidgets.QLineEdit("")
        return self.budget_day_input_field

    def _budget_week_input(self) -> QtWidgets.QLineEdit:
        self.budget_week_input_field = QtWidgets.QLineEdit("")
        return self.budget_week_input_field

    def _budget_month_input(self) -> QtWidgets.QLineEdit:
        self.budget_month_input_field = QtWidgets.QLineEdit("")
        return self.budget_month_input_field


class MainWindow(QtWidgets.QWidget):

    def __init__(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)
        super().__init__()
        self.combo: QtWidgets.QComboBox
        self.expenses_input_field: QtWidgets.QLineEdit
        self.control_table: QtWidgets.QTableWidget
        self.expenses_table: QtWidgets.QTableWidget
        self.day_change_win: DayChangeWindow
        self.cat_win: CategoryWindow

    def init_ui(self) -> None:
        expenses_label = QtWidgets.QLabel("Расходы")
        help_label = QtWidgets.QLabel(
            "Help: Чтобы редактировать расходы "
            + "дважды кликните на ячейку в таблице расходов"
        )

        self.status_label = QtWidgets.QLabel(" ")
        control_label = QtWidgets.QLabel("Бюджет")
        add_button = QtWidgets.QPushButton("Добавить расход")
        invite_label = QtWidgets.QLabel("Сумма")
        category_label = QtWidgets.QLabel("Категория")
        correct_budget_button = QtWidgets.QPushButton("Редактировать бюджет")
        correct_category_button = QtWidgets.QPushButton("Редактировать категории")

        self.layer = QtWidgets.QGridLayout()
        self.layer.addWidget(expenses_label, 0, 0)
        self.layer.addWidget(
            self.status_label, 0, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.layer.addWidget(self._expenses_table_func(), 1, 0, 1, -1)
        self.layer.addWidget(control_label, 2, 0)
        self.layer.addWidget(self._control_table_func(), 3, 0, 1, -1)
        self.layer.addWidget(
            invite_label, 4, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.layer.addWidget(
            self._expenses_input(""), 4, 1, 1, -1
        )
        self.layer.addWidget(
            category_label, 5, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self._category_combobox()
        self.layer.addWidget(self.combo, 5, 1, 1, -1)
        self.layer.addWidget(add_button, 6, 0, 1, -1)

        self.layer.addWidget(correct_budget_button, 7, 0, 1, -1)
        self.layer.addWidget(correct_category_button, 8, 0, 1, -1)
        self.layer.addWidget(help_label, 9, 0, 1, -1)

        self.setLayout(self.layer)

        add_button.clicked.connect(self._on_add_button_click)
        correct_budget_button.clicked.connect(self._on_budget_button_click)
        correct_category_button.clicked.connect(self._on_category_button_click)
        self.expenses_table.cellDoubleClicked.connect(self._expenses_cell_change)
        self.setWindowTitle("Bookkeeper App")
        self.setGeometry(900, 100, 700, 500)

    def do_show(self) -> None:
        self.show()
        self.app.exec_()

    def expense_change_handler(
        self, handler: Callable[[int, str, datetime.datetime, str, int], None]
    ) -> None:
        """
        Изменяет некоторые параметры записи расходов
        """
        self.handler_expense_changer = handler

    def expense_add_handler(
        self, handler: Callable[[int, str, datetime.datetime], None]
    ) -> None:
        """
        Добавляет новую запись расходов
        """
        self.handler_expense_adder = handler

    def delete_category_handler(self, handler: Callable[[str], None]) -> None:
        """
        Удаляет категорию из списка каатегорий
        """
        self.handler_del = handler

    def add_category_handler(self, handler: Callable[[Category], None]) -> None:
        """
        Добавляет новую каатегорию в список каатегорий
        """
        self.handler_add = handler

    def budget_change_handler(self, handler: Callable[[Budget], None]) -> None:
        """
        Изменяет установленный бюджет на период
        """
        self.handler_budget = handler

    def clear_expense_table(self) -> None:
        self.expenses_table.clearContents()

    def set_budget(self, budgets: list[Budget]) -> None:
        self.control_table.setItem(
            0, 1, QtWidgets.QTableWidgetItem(str(budgets[0].summa))
        )
        self.control_table.setItem(
            1, 1, QtWidgets.QTableWidgetItem(str(budgets[1].summa))
        )
        self.control_table.setItem(
            2, 1, QtWidgets.QTableWidgetItem(str(budgets[2].summa))
        )

    def set_categories(self, categories: list[Category]) -> None:
        for cat in categories:
            self.combo.addItem(f"{cat.name}")

    def set_expense_list(
        self,
        expenses: list[Expense],
        categories: dict[int, str],
    ) -> None:
        row = 0
        while self.expenses_table.item(row, 0) is not None:
            row += 1
        for exp in expenses:
            if exp.category in categories:
                cat_name = categories[exp.category]
            else:
                cat_name = "Удаленная категория"
            date = exp.expense_date.strftime("%Y-%m-%d %H:%M:%S")
            self.expenses_table.setItem(row, 0, QtWidgets.QTableWidgetItem(date))
            self.expenses_table.setItem(
                row, 1, QtWidgets.QTableWidgetItem(str(exp.amount))
            )
            self.expenses_table.setItem(row, 2, QtWidgets.QTableWidgetItem(cat_name))
            self.expenses_table.setItem(row, 3, QtWidgets.QTableWidgetItem(exp.comment))
            row += 1

    def set_summ(self, summs: list[float]) -> None:
        for i, summ in enumerate(summs):
            self.control_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(summ)))

    def _expenses_cell_change(self, row: int, column: int) -> None:
        if self.expenses_table.item(row, 0) is None:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Этой записи пока не существует.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
        else:
            if column == 0:
                self._day_changing(row, column)
            if column == 1:
                self._summa_changing(row, column)
            if column == 2:
                self._category_changing(row, column)
            if column == 3:
                self._comment_changing(row, column)

    def _day_changing(self, row: int, column: int) -> None:
        self.day_change_win = DayChangeWindow(self, row, column)
        self.day_change_win.show()

    def _summa_changing(self, row: int, column: int) -> None:
        text, ok_button = QtWidgets.QInputDialog.getMultiLineText(
            self,
            "Изменить сумму расхода",
            "" "Введите новую сумму расхода:",
            "",
        )
        if check_float(text) is None:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Сумма должна быть введена в числовом формате.\n")
            dlg.setWindowTitle("Ошибка")
            dlg.resize(200, 50)
            dlg.exec()
        elif ok_button and text:
            self.expenses_table.setItem(
                row,
                column,
                QtWidgets.QTableWidgetItem(text),
            )
            date = datetime.datetime.strptime(
                self.expenses_table.item(row, 0).text(), "%Y-%m-%d %H:%M:%S"
            )

            comm = self.expenses_table.item(row, 3)
            if comm is None:
                comment = ""
            else:
                comment = comm.text()
            self.handler_expense_changer(
                int(text),
                self.expenses_table.item(row, 2).text(),
                date,
                comment,
                row + 1,
            )

    def _category_changing(self, row: int, column: int) -> None:
        count = self.combo.count()
        categoryes = [self.combo.itemText(i) for i in range(count)]
        self.category_change_win = CategoryChangeWindow(
            self, categoryes=categoryes, ro=row, col=column
        )
        self.category_change_win.show()

    def _comment_changing(self, row: int, column: int) -> None:
        text, ok_button = QtWidgets.QInputDialog.getMultiLineText(
            self,
            "Дабавить комментарий к записи",
            "Введите комментарий к записи:",
            "",
        )
        if ok_button and text:
            self.expenses_table.setItem(
                row,
                column,
                QtWidgets.QTableWidgetItem(text),
            )
            val = self.expenses_table.item(row, 0).text()
            date = datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")

            self.handler_expense_changer(
                int(self.expenses_table.item(row, 1).text()),
                self.expenses_table.item(row, 2).text(),
                date,
                text,
                row + 1,
            )

    def _on_add_button_click(self) -> None:
        category_text = str(self.reading_combobox())
        sum_text = str(self.reading_sum())
        if check_float(sum_text) is None:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Сумма должна быть в числовом формате.\n")
            dlg.setWindowTitle("Ошибкаа")
            dlg.resize(200, 50)
            dlg.exec()
        else:
            row_count = 0
            while self.expenses_table.item(row_count, 0) is not None:
                row_count += 1
            # row_count = self.expenses_table.rowCount()
            self.expenses_table.setItem(
                row_count, 1, QtWidgets.QTableWidgetItem(sum_text)
            )
            self.expenses_table.setItem(
                row_count, 2, QtWidgets.QTableWidgetItem(category_text)
            )
            date = datetime.datetime.now()
            self.expenses_table.setItem(
                row_count,
                0,
                QtWidgets.QTableWidgetItem(date.strftime("%Y-%m-%d %H:%M:%S")),
            )

            self.status_label.setText("Расходы добавлены")
            self.handler_expense_adder(
                int(sum_text),
                category_text,
                date,
            )

    def _on_category_button_click(self) -> None:
        count = self.combo.count()
        categoryes = [self.combo.itemText(i) for i in range(count)]
        self.cat_win = CategoryWindow(self, categoryes=categoryes)
        self.cat_win.show()

    def _on_budget_button_click(self) -> None:
        self.budg_win = BudgetWindow(self)
        self.budg_win.show()

    def _expenses_table_func(self) -> QtWidgets.QTableWidget:
        self.expenses_table = QtWidgets.QTableWidget(4, 1000)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(1000)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.expenses_table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.expenses_table.verticalHeader().hide()

        return self.expenses_table

    def _control_table_func(self) -> QtWidgets.QTableWidget:
        self.control_table = QtWidgets.QTableWidget(2, 3)

        self.control_table.setColumnCount(2)
        self.control_table.setRowCount(3)
        self.control_table.setHorizontalHeaderLabels("Сумма Бюджет".split())
        self.control_table.setVerticalHeaderLabels("День Неделя Месяц".split())
        hor_header = self.control_table.horizontalHeader()
        hor_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        hor_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.control_table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        ver_header = self.control_table.verticalHeader()
        ver_header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        ver_header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        ver_header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        self.control_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.control_table.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )

        return self.control_table

    def _expenses_input(self, text: str) -> QtWidgets.QLineEdit:
        self.expenses_input_field = QtWidgets.QLineEdit(f"{text}")
        return self.expenses_input_field

    def _category_combobox(self) -> QtWidgets.QComboBox:
        self.combo = QtWidgets.QComboBox()
        return self.combo

    def reading_combobox(self) -> str:
        return self.combo.currentText()

    def reading_sum(self) -> str:
        """
        Чтение введенной суммы расхода пользователем
        """
        return self.expenses_input_field.text()

    def add_category(self, text: str) -> None:
        """
        Добавление категории в главном окне
        после добавления пользователем
        """
        self.combo.addItem(f"{text}")

    def delete_category(self, categoryes: list[str]) -> None:
        """
        Переписывание содержания категорий в главном окне
        после удаления выбранного пользователем
        """
        self.combo.clear()
        for i in categoryes:
            self.combo.addItem(f"{i}")
