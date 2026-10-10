from .db import connect
EF=('employee_code','full_name','national_id','nationality','job_title','department','phone','email','status','notes')
CF=('contract_number','employee_id','start_date','end_date','basic_salary','housing_allowance','transport_allowance','other_allowance','status','notes')
def list_employees(s=''):
 with connect() as c:
  q=f'%{s}%'; return c.execute("SELECT * FROM employees WHERE employee_code LIKE ? OR full_name LIKE ? OR COALESCE(national_id,'') LIKE ? ORDER BY full_name",(q,q,q)).fetchall()
def save_employee(d,rid=None):
 if not d.get('employee_code','').strip() or not d.get('full_name','').strip(): raise ValueError('كود الموظف والاسم الكامل مطلوبان')
 vals=[d.get(k,'') for k in EF]
 with connect() as c:
  if rid: c.execute('UPDATE employees SET '+','.join(k+'=?' for k in EF)+' WHERE id=?',(*vals,rid))
  else: c.execute('INSERT INTO employees ('+','.join(EF)+') VALUES ('+','.join('?' for _ in EF)+')',vals)
def delete_employee(i):
 with connect() as c: c.execute('DELETE FROM employees WHERE id=?',(i,))
def employee_choices():
 with connect() as c: return c.execute('SELECT id,employee_code,full_name FROM employees ORDER BY full_name').fetchall()
def list_contracts(s=''):
 with connect() as c:
  q=f'%{s}%'; return c.execute('SELECT c.*,e.full_name FROM contracts c JOIN employees e ON e.id=c.employee_id WHERE c.contract_number LIKE ? OR e.full_name LIKE ? ORDER BY c.end_date',(q,q)).fetchall()
def save_contract(d,rid=None):
 if not d.get('contract_number','').strip() or not d.get('employee_id') or not d.get('start_date') or not d.get('end_date'): raise ValueError('رقم العقد والموظف والتواريخ مطلوبة')
 if d['end_date']<d['start_date']: raise ValueError('نهاية العقد لا يمكن أن تسبق بدايته')
 vals=[d.get(k,0 if 'salary' in k or 'allowance' in k else '') for k in CF]
 with connect() as c:
  if rid: c.execute('UPDATE contracts SET '+','.join(k+'=?' for k in CF)+' WHERE id=?',(*vals,rid))
  else: c.execute('INSERT INTO contracts ('+','.join(CF)+') VALUES ('+','.join('?' for _ in CF)+')',vals)
def delete_contract(i):
 with connect() as c: c.execute('DELETE FROM contracts WHERE id=?',(i,))
