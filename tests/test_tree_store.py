import pytest
from pathlib import Path

from core.tree_store import (
    TreeStore,
    TreeStoreException,
    Index,
    base_256,
    base_10,
    get_store_tuple,
)


def test_base_256():
    assert base_256(0) == (0, 0, 0)
    assert base_256(1) == (0, 0, 1)
    assert base_256(255) == (0, 0, 255)
    assert base_256(256) == (0, 1, 0)
    assert base_256(16777215) == (255, 255, 255)

    with pytest.raises(TreeStoreException):
        base_256(-1)

    with pytest.raises(TreeStoreException):
        base_256(16777216)


def test_base_10():
    assert base_10(0, 0, 0) == 0
    assert base_10(0, 0, 1) == 1
    assert base_10(0, 0, 255) == 255
    assert base_10(0, 1, 0) == 256
    assert base_10(255, 255, 255) == 16777215


def test_get_store_tuple():
    assert get_store_tuple(0) == ("000", "000", "000")
    assert get_store_tuple(256) == ("000", "001", "000")
    assert get_store_tuple(16777215) == ("255", "255", "255")


def test_index_operations(tmp_path: Path):
    idx_file = tmp_path / "index.json"
    idx = Index(idx_file)
    assert idx.value == 0

    idx.value = 5
    assert idx.value == 5

    # Test reading existing file
    idx2 = Index(idx_file)
    assert idx2.value == 5

    with pytest.raises(TreeStoreException):
        idx.value = 4  # Can't decrease


def test_tree_store_create_and_get(tmp_path: Path):
    store_home = tmp_path / "ts"
    ts = TreeStore(store_home)

    store0 = ts.create_store()
    assert store0.index == 0
    assert store0.key == "000000000"
    assert store0.home.exists()

    store1 = ts.create_store()
    assert store1.index == 1
    assert store1.key == "000000001"
    assert store1.home.exists()

    s = ts.get_store(0)
    assert s.index == 0
    assert s.key == "000000000"

    with pytest.raises(TreeStoreException):
        ts.get_store(2)  # Doesn't exist


def test_tree_store_iterate(tmp_path: Path):
    ts = TreeStore(tmp_path)
    ts.create_store()
    ts.create_store()
    ts.create_store()

    stores = list(ts.iterate())
    assert len(stores) == 3
    assert stores[0].index == 0
    assert stores[2].index == 2

    stores_subset = list(ts.iterate(first=1, top=2))
    assert len(stores_subset) == 1
    assert stores_subset[0].index == 1
