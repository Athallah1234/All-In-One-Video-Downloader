from PySide6.QtCore import QAbstractListModel,QModelIndex,Qt,Signal


class PlaylistItemsModel(QAbstractListModel):
    selectionChanged=Signal(int,int)
    def __init__(self,parent=None):
        super().__init__(parent); self._items=(); self._default_checked=True; self._overrides=set(); self._unavailable=set()

    def set_items(self,items):
        self.beginResetModel(); self._items=items if isinstance(items,tuple) else tuple(items or ()); self._default_checked=True; self._overrides=set(); self._unavailable={row for row,item in enumerate(self._items) if item.get("title")=="[Video tidak tersedia]"}; self.endResetModel(); self.selectionChanged.emit(self.selected_count(),self.selectable_count())

    def rowCount(self,parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)

    def data(self,index,role=Qt.DisplayRole):
        if not index.isValid() or not 0<=index.row()<len(self._items):return None
        if role==Qt.CheckStateRole:return Qt.Checked if self._checked(index.row()) else Qt.Unchecked
        if role not in (Qt.DisplayRole,Qt.ToolTipRole):return None
        item=self._items[index.row()]
        return f"{item['index']}. {item['title']}"

    def _checked(self,row):
        return row not in self._unavailable and (self._default_checked != (row in self._overrides))

    def flags(self,index):
        if not index.isValid() or index.row() in self._unavailable:return Qt.NoItemFlags
        return Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsUserCheckable

    def setData(self,index,value,role=Qt.EditRole):
        if role!=Qt.CheckStateRole or not index.isValid() or index.row() in self._unavailable:return False
        desired=value==Qt.Checked
        if desired==self._default_checked:self._overrides.discard(index.row())
        else:self._overrides.add(index.row())
        self.dataChanged.emit(index,index,[Qt.CheckStateRole]); self.selectionChanged.emit(self.selected_count(),self.selectable_count()); return True

    def selectable_count(self):return len(self._items)-len(self._unavailable)
    def selected_count(self):return self.selectable_count()-len(self._overrides) if self._default_checked else len(self._overrides)
    def _bulk(self,checked):
        self._default_checked=checked; self._overrides.clear()
        if self._items:self.dataChanged.emit(self.index(0),self.index(len(self._items)-1),[Qt.CheckStateRole])
        self.selectionChanged.emit(self.selected_count(),self.selectable_count())
    def select_all(self):self._bulk(True)
    def clear_selection(self):self._bulk(False)
    def invert_selection(self):
        self._default_checked=not self._default_checked
        if self._items:self.dataChanged.emit(self.index(0),self.index(len(self._items)-1),[Qt.CheckStateRole])
        self.selectionChanged.emit(self.selected_count(),self.selectable_count())

    def selected_selector(self):
        indices=sorted({item.get("index") for row,item in enumerate(self._items) if self._checked(row) and isinstance(item.get("index"),int) and not isinstance(item.get("index"),bool) and item["index"]>0}); ranges=[]
        for value in indices:
            if not ranges or value>ranges[-1][1]+1:ranges.append([value,value])
            else:ranges[-1][1]=value
        return ",".join(str(start) if start==end else f"{start}-{end}" for start,end in ranges)
