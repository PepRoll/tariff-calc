
import ui
import clipboard
from console import hud_alert
from console import alert

''' Приложение для расчета платы за жкх. и формирования отчета для арендодателя.
'''

class Tarif:
	def __init__(self, sender):
		try:
			self.cold_water = float(sender.superview['tarif_cold_water'].text)
			self.warm_water = float(sender.superview['tarif_warm_water'].text)
			self.water = float(sender.superview['tarif_water'].text)
			self.electric = float(sender.superview['tarif_electric'].text)
		except ValueError:
			alert('Все поля тарифов должны быть заполнены числами.')
		except:
			alert('Неизвестная ошибка, при чтении тарифов.')

class Bill:
	def __init__(self, delta, tarif):
		self.cold_water = delta.cold_water * tarif.cold_water
		self.warm_water = delta.warm_water * tarif.warm_water
		self.water = delta.water * tarif.water
		self.electric = delta.electric * tarif.electric
		self.amount = self.cold_water +  self.warm_water + self.water + self.electric

class Counter:
	def __init__(self, cw, ww, e):
		self.cold_water = cw
		self.warm_water = ww
		self.electric = e

class Delta:
	def __init__(self, newCounter):
		oldCounter = counter_from_file()
		self.cold_water = newCounter.cold_water - oldCounter.cold_water
		self.warm_water = newCounter.warm_water - oldCounter.warm_water
		self.water = self.cold_water + self.warm_water
		self.electric = newCounter.electric - oldCounter.electric

class EmptyFieldException(Exception):
	def __init__(self, label, type):
		self.message = "Поле '{0}' ({1}) должно быть заполнено".format(label, type)
			
def counter_from_file():
	try:
		with open('counter.txt', 'r') as f:
				lst = f.readlines()
				cold_water = int(lst[0])
				warm_water = int(lst[1])
				electric = int(lst[2])
				return Counter(cold_water, warm_water, electric)
	except FileNotFoundError:
		alert('Отсуствуют предыдущие показатели счетчиков, расчет невозможен. Сохраните текущие показатели.')
	except:
		alert('Неизвестная ошибка, при чтении предыдущих показателей.')
		
		
class Printer:
	def __init__(self, counter, delta, bill):
		self.cold_water = "Холодная вода: т.п. {0}, {1} куб., {2} руб".format(counter.cold_water,delta.cold_water, bill.cold_water)
		self.warm_water = "Горячая вода: т.п. {0}, {1} куб., {2} руб".format(counter.warm_water,delta.warm_water, bill.warm_water)
		self.water = "Водоотводение: {0} куб., {1} руб".format(delta.water, bill.water)
		self.electric = "Элекричество:  т.п. {0}, {1}, {2} руб".format(counter.electric,delta.electric, bill.electric)
		self.amount = "Итого: {0} руб".format(bill.amount)
	
	def print(self, sender):
		sender.superview['view'].text = "{0}\n{1}\n{2}\n{3}\n{4}".format(self.cold_water, self.warm_water, self.water, self.electric, self.amount)

def read_from_field(sender, label, type):	
	field = sender.superview[label].text
	if not field:
		raise EmptyFieldException(sender.superview[label].placeholder, type)
	
	return field
		
def tarif_field(sender, label):
	return read_from_field(sender, label, 'Тариф')

def counter_field(sender, label):
	return read_from_field(sender, label, 'Показания')

def save_tarif(sender):
	try:
		cold = tarif_field(sender, 'tarif_cold_water')
		warm = tarif_field(sender, 'tarif_warm_water')
		water = tarif_field(sender,  'tarif_water')
		electric = tarif_field(sender, 'tarif_electric')
		
		with open('tarif.txt', 'w') as f:
			f.write(cold + '\n')
			f.write(warm + '\n')
			f.write(water + '\n')
			f.write(electric + '\n')
			
	except EmptyFieldException as e:
		alert(e.message)
	except: alert('Неизвестная ошибка при сохранении тарифов')
		
def counter_from_fields(sender):
	try:
		cold_water = int(sender.superview['counter_cold_water'].text)
		warm_water = int(sender.superview['counter_warm_water'].text)
		electric = int(sender.superview['counter_electric'].text)
		return Counter(cold_water, warm_water, electric)
	except ValueError:
			alert('Все поля показаний должны быть заполнены целыми числами.')
	except:
		alert('Неизвестная ошибка, при чтении показателей.')
		

def save_counter(sender):
	try:
		
		cold = counter_field(sender, 'counter_cold_water')
		warm = counter_field(sender, 'counter_warm_water')
		electric = counter_field(sender, 'counter_electric')
		
		with open('counter.txt', 'w') as f:
			f.write(cold + '\n')
			f.write(warm + '\n')
			f.write(electric + '\n')
	except EmptyFieldException as e:
		alert(e.message)
	except: alert('Неизвестная ошибка, при сохранении показателей')

def tarif_from_file(v):
	try:
		with open('tarif.txt', 'r') as f:
			lst = f.readlines()
			if lst:
				v['tarif_cold_water'].text = lst[0]
				v['tarif_warm_water'].text = lst[1]
				v['tarif_water'].text = lst[2]
				v['tarif_electric'].text = lst[3]
	except FileNotFoundError:
		pass

def calculate(sender):
	'@type sender: ui.Button'
	counter = counter_from_fields(sender)
	delta = Delta(counter)
	bill = Bill(delta, Tarif(sender))
	Printer(counter, delta, bill).print(sender)

def save(sender):
	'@type sender: ui.Button'
	tarif_saved = save_tarif(sender)
	counter_saved = save_counter(sender)
	hud_alert('Сохранено')
	
def copy(sender):
	'@type sender: ui.Button'	
	view_value = sender.superview['view'].text
	if not view_value:
		alert('Коппировать нечего, сначала проведите расчет.')
	else:
		clipboard.set(view_value)
		hud_alert('Скопировано')
	
v = ui.load_view('tarif')
tarif_from_file(v)
v.present(orientations=['portrait'])
