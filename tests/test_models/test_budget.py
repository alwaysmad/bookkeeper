from datetime import datetime, timedelta
import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    budg = Budget(
        term=timedelta(7),
        summa=5000,
        category="Продукты",
        pk=1,
    )
    assert budg.term == timedelta(7)
    assert budg.summa == 5000
    assert budg.category == "Продукты"
    assert budg.pk == 1


def test_create_brief():
    budg = Budget(100, timedelta(1))
    assert budg.term == timedelta(1)
    assert budg.summa == 100


def test_can_add_to_repo(repo):
    budg = Budget(100, timedelta(1))
    pk = repo.add(budg)
    assert budg.pk == pk
