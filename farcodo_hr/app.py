import sys
from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon
from .db import initialize
from . import repository as R
STYLE='QMainWindow{background:#f3f6f8} QLabel#title{font-size:23px;font-weight:bold;color:#183b56} QPushButton{background:#176b67;color:white;padding:8px;border:0;border-radius:5px} QLineEdit{padding:6px;background:white} QTableWidget{background:white}'
class RecordDialog(QDialog):
 def __init__(self,kind,row=None):
  super().__init__(); self.kind=kind; self.ws={}; self.setWindowTitle('بيانات الموظف' if kind=='employees' else 'بيانات العقد'); f=QFormLayout(self)
  fields=[('employee_code','كود الموظف'),('full_name','الاسم'),('national_id','رقم الهوية'),('nationality','الجنسية'),('job_title','المسمى الوظيفي'),('department','الإدارة'),('phone','الهاتف'),('email','البريد'),('status','الحالة'),('notes','ملاحظات')] if kind=='employees' else [('contract_number','رقم العقد'),('employee_id','الموظف'),('start_date','بداية العقد'),('end_date','نهاية العقد'),('basic_salary','الراتب الأساسي'),('housing_allowance','بدل السكن'),('transport_allowance','بدل النقل'),('other_allowance','بدلات أخرى'),('status','الحالة'),('notes','ملاحظات')]
  for k,label in fields:
   if k=='employee_id':
    w=QComboBox(); [(w.addItem(f"{e['employee_code']} — {e['full_name']}",e['id'])) for e in R.employee_choices()]
   elif k in ('status',):
    w=QComboBox(); w.addItems(['Active','Inactive'] if kind=='employees' else ['Draft','Pending approval','Approved','Expired','Terminated'])
   elif k in ('start_date','end_date'):
    w=QDateEdit(); w.setCalendarPopup(True); w.setDisplayFormat('yyyy-MM-dd'); w.setDate(__import__('PySide6').QtCore.QDate.currentDate().addYears(1 if k=='end_date' else 0))
   elif 'salary' in k or 'allowance' in k: w=QDoubleSpinBox(); w.setMaximum(1e9); w.setDecimals(2)
   elif k=='notes': w=QTextEdit(); w.setMaximumHeight(60)
   else: w=QLineEdit()
   if row and k in row.keys():
    val=row[k]
    if isinstance(w,QLineEdit): w.setText(str(val or ''))
    elif isinstance(w,QTextEdit): w.setPlainText(str(val or ''))
    elif isinstance(w,QComboBox):
     idx=w.findData(val) if k=='employee_id' else w.findText(str(val)); w.setCurrentIndex(max(0,idx))
    elif isinstance(w,QDoubleSpinBox): w.setValue(float(val or 0))
    elif isinstance(w,QDateEdit): w.setDate(__import__('PySide6').QtCore.QDate.fromString(str(val),'yyyy-MM-dd'))
   self.ws[k]=w; f.addRow(label,w)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); f.addRow(b)
 def data(self):
  d={}
  for k,w in self.ws.items():
   if isinstance(w,QLineEdit): d[k]=w.text().strip()
   elif isinstance(w,QTextEdit): d[k]=w.toPlainText().strip()
   elif isinstance(w,QComboBox): d[k]=w.currentData() if k=='employee_id' else w.currentText()
   elif isinstance(w,QDateEdit): d[k]=w.date().toString('yyyy-MM-dd')
   else: d[k]=w.value()
  return d
class Tab(QWidget):
 def __init__(self,kind):
  super().__init__(); self.kind=kind; self.rid=None; l=QVBoxLayout(self); bar=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText('بحث...'); self.search.textChanged.connect(self.refresh); bar.addWidget(self.search)
  for t,fn in [('إضافة',self.add),('تعديل',self.edit),('حذف',self.delete),('تحديث',self.refresh)]: b=QPushButton(t); b.clicked.connect(fn); bar.addWidget(b)
  l.addLayout(bar); self.table=QTableWidget(); self.table.setSelectionBehavior(QAbstractItemView.SelectRows); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.table.itemSelectionChanged.connect(self.select); l.addWidget(self.table); self.refresh()
 def select(self):
  rows=self.table.selectionModel().selectedRows(); self.rid=int(self.table.item(rows[0].row(),0).text()) if rows else None
 def refresh(self,*a):
  rows=R.list_employees(self.search.text()) if self.kind=='employees' else R.list_contracts(self.search.text()); cols=['id','employee_code','full_name','national_id','nationality','job_title','department','phone','status'] if self.kind=='employees' else ['id','contract_number','full_name','start_date','end_date','basic_salary','housing_allowance','transport_allowance','status']; self.table.setColumnCount(len(cols)); self.table.setHorizontalHeaderLabels(cols); self.table.setRowCount(len(rows))
  for i,r in enumerate(rows):
   for j,k in enumerate(cols): self.table.setItem(i,j,QTableWidgetItem(str(r[k] or '')))
  self.rid=None; self.table.resizeColumnsToContents()
 def add(self):
  if self.kind=='contracts' and not R.employee_choices(): QMessageBox.information(self,'تنبيه','أضف موظفًا أولًا'); return
  d=RecordDialog(self.kind)
  if d.exec():
   try: (R.save_employee if self.kind=='employees' else R.save_contract)(d.data()); self.refresh()
   except Exception as e: QMessageBox.critical(self,'خطأ',str(e))
 def edit(self):
  if self.rid is None: QMessageBox.information(self,'تنبيه','اختر سجلًا أولًا'); return
  rows=R.list_employees(self.search.text()) if self.kind=='employees' else R.list_contracts(self.search.text()); row=next((r for r in rows if r['id']==self.rid),None)
  if row:
   d=RecordDialog(self.kind,row)
   if d.exec():
    try: (R.save_employee if self.kind=='employees' else R.save_contract)(d.data(),self.rid); self.refresh()
    except Exception as e: QMessageBox.critical(self,'خطأ',str(e))
 def delete(self):
  if self.rid is None: QMessageBox.information(self,'تنبيه','اختر سجلًا أولًا'); return
  if QMessageBox.question(self,'تأكيد','هل تريد حذف السجل؟')==QMessageBox.Yes:
   try: (R.delete_employee if self.kind=='employees' else R.delete_contract)(self.rid); self.refresh()
   except Exception as e: QMessageBox.critical(self,'تعذر الحذف',str(e))
def main():
 initialize(); app=QApplication(sys.argv); app.setStyleSheet(STYLE); w=QMainWindow(); w.setWindowTitle('Farcodo HR'); w.resize(1200,720); icon=Path(__file__).resolve().parent.parent/'assets'/'farcodo.ico'
 if icon.exists(): w.setWindowIcon(QIcon(str(icon)))
 root=QWidget(); lay=QVBoxLayout(root); title=QLabel('Farcodo HR | إدارة الموارد البشرية'); title.setObjectName('title'); lay.addWidget(title); tabs=QTabWidget(); tabs.addTab(Tab('employees'),'الموظفون'); tabs.addTab(Tab('contracts'),'العقود'); lay.addWidget(tabs); w.setCentralWidget(root); w.show(); sys.exit(app.exec())
