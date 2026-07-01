from PySide6.QtCore import Qt

from app.ui.playlist_items_model import PlaylistItemsModel


def test_playlist_model_formats_rows_lazily(qtbot):
    model=PlaylistItemsModel()
    model.set_items(({"index":1,"title":"Satu"},{"index":17,"title":"[Video tidak tersedia]"},{"index":18,"title":"<b>literal</b> 🚀"}))
    assert model.rowCount()==3
    assert model.data(model.index(0),Qt.DisplayRole)=="1. Satu"
    assert model.data(model.index(1),Qt.DisplayRole)=="17. [Video tidak tersedia]"
    assert model.data(model.index(2),Qt.ToolTipRole)=="18. <b>literal</b> 🚀"
    assert model.data(model.index(0),Qt.DecorationRole) is None


def test_playlist_model_resets_atomically(qtbot):
    model=PlaylistItemsModel()
    model.set_items(tuple({"index":index+1,"title":f"Video {index}"} for index in range(50000)))
    assert model.rowCount()==50000
    model.set_items(({"index":1,"title":"Baru"},))
    assert model.rowCount()==1
    assert model.data(model.index(0),Qt.DisplayRole)=="1. Baru"


def selectable_items():
    return ({"index":1,"title":"Satu"},{"index":2,"title":"[Video tidak tersedia]"},{"index":3,"title":"Tiga"},{"index":4,"title":"Empat"})


def test_model_exposes_checkboxes_and_blocks_unavailable(qtbot):
    model=PlaylistItemsModel(); model.set_items(selectable_items())
    assert model.data(model.index(0),Qt.CheckStateRole)==Qt.Checked
    assert model.flags(model.index(0)) & Qt.ItemIsUserCheckable
    assert model.data(model.index(1),Qt.CheckStateRole)==Qt.Unchecked
    assert not model.flags(model.index(1)) & Qt.ItemIsEnabled
    assert not model.setData(model.index(1),Qt.Checked,Qt.CheckStateRole)
    assert model.selected_count()==3 and model.selectable_count()==3


def test_toggle_and_bulk_operations_keep_compact_state(qtbot):
    model=PlaylistItemsModel(); model.set_items(selectable_items())
    assert model.setData(model.index(2),Qt.Unchecked,Qt.CheckStateRole)
    assert model.selected_selector()=="1,4"
    model.clear_selection(); assert model.selected_count()==0
    model.select_all(); assert model.selected_selector()=="1,3-4"
    model.invert_selection(); assert model.selected_count()==0
    model.invert_selection(); assert model.selected_selector()=="1,3-4"


def test_selector_sorts_and_deduplicates_source_indices(qtbot):
    model=PlaylistItemsModel(); model.set_items(({"index":5,"title":"A"},{"index":3,"title":"B"},{"index":5,"title":"C"},{"index":4,"title":"D"}))
    assert model.selected_selector()=="3-5"


def test_bulk_reset_scales_without_materializing_selected_rows(qtbot):
    model=PlaylistItemsModel(); model.set_items(tuple({"index":i+1,"title":f"Video {i}"} for i in range(50000)))
    model.clear_selection(); assert model.selected_count()==0; assert model._overrides==set()
    model.select_all(); assert model.selected_count()==50000; assert model._overrides==set()
