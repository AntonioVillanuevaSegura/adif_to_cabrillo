#https://cqww.com/cabrillo.htm
"""
                              --------info sent------- -------info rcvd--------
QSO: freq  mo date       time call          rst exch   call          rst exch   t
QSO: ***** ** yyyy-mm-dd nnnn ************* nnn ****** ************* nnn ****** n
QSO:  3799 PH 2000-11-26 0711 N6TW          59  03     JT1Z          59  23     0
000000000111111111122222222223333333333444444444455555555556666666666777777777788
123456789012345678901234567890123456789012345678901234567890123456789012345678901
CW (morse)
PH (phone, voz)
RY (radioteletipo, RTTY)
FM, AM, SSB, etc.
"""

import tkinter as tk #Gui
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser

import re

VERSION_SOFT= "1"
	
import tkinter as tk
from tkinter import ttk, filedialog, END
import re

VERSION_SOFT = "1.0"

HEADER="""START-OF-LOG: 3.0
CONTEST: 
CALLSIGN: 
LOCATION: 
CATEGORY-OPERATOR: 
CATEGORY-ASSISTED: 
CATEGORY-BAND: 
CATEGORY-POWER: 
CATEGORY-MODE: 
CATEGORY-TRANSMITTER: 
CATEGORY-OVERLAY: 
GRID-LOCATOR: 
CLAIMED-SCORE: 
CLUB: 
CREATED-BY: 
NAME: 
ADDRESS: 
ADDRESS-CITY: 
ADDRESS-STATE-PROVINCE: 
ADDRESS-POSTALCODE: 
ADDRESS-COUNTRY:
OPERATORS: 
SOAPBOX:
"""
class HojaExcelApp:
	def __init__(self, parent, adif_records, mode=0):
		self.parent = parent
		self.adif_records = adif_records
		self.crear_hoja_excel(mode)

	def crear_hoja_excel(self,mode=0):
		columns = ("FREQ_RX", "MODE", "QSO_DATE", "TIME_ON",
				   "STATION_CALLSIGN", "DATA1", "CALL", "DATA2")
		if mode == 1:
			
			# Creamos la lista solo con las claves antes de ":"
			#columns = [linea.split(":", 1)[0].strip() for linea in HEADER.strip().splitlines() if ":" in linea]
			columns =("CONTEST","C.OPERATOR","C.BAND","C.POWER","C.MODE","LOCATOR","SCORE","NAME")
			self.tree = ttk.Treeview(self.parent, columns=columns, show='headings',height=1)
		elif mode==0:	
			self.tree = ttk.Treeview(self.parent, columns=columns, show='headings')
			
		for col in columns:
			self.tree.heading(col, text=col)
			self.tree.column(col, width=100)  # ajuste de ancho

		
		#Mode 0 utiliza adif_records
		if mode ==0:
			# Aseguramos que cada fila tenga todas las columnas
			for row in self.adif_records:
				while len(row) < len(columns):
					row.append("")

			# Insertamos los datos
			for row in self.adif_records:
				self.tree.insert("", "end", values=row)
		

		
		self.tree.pack(fill="both", expand=True)

		# Doble clic para editar celda
		self.tree.bind("<Double-1>", self.editar_celda)
		
		if mode == 1:
			# Lista con una fila vacía (tantos "" como columnas)
			fila_vacia = ["" for _ in columns]
			self.cargar_datos([fila_vacia])

	def editar_celda(self, event):
		"""Permite editar una celda al hacer doble clic sobre ella."""
		region = self.tree.identify("region", event.x, event.y)
		if region != "cell":
			return

		row_id = self.tree.identify_row(event.y)
		column_id = self.tree.identify_column(event.x)

		# Coordenadas y tamaño de la celda
		x, y, width, height = self.tree.bbox(row_id, column_id)
		valor_actual = self.tree.set(row_id, column_id)

		# Entry para edición
		entry_edit = tk.Entry(self.tree)
		entry_edit.place(x=x, y=y, width=width, height=height)
		entry_edit.insert(0, valor_actual)
		entry_edit.focus()

		def guardar(event=None):
			nuevo_valor = entry_edit.get()
			self.tree.set(row_id, column_id, nuevo_valor)
			entry_edit.destroy()

		# Guardar al pulsar Enter o perder foco
		entry_edit.bind("<Return>", guardar)
		entry_edit.bind("<FocusOut>", guardar)

	def cargar_datos(self, nuevos_datos):
		"""Borra la tabla y carga nuevos datos"""
		for item in self.tree.get_children():
			self.tree.delete(item)
		for row in nuevos_datos:
			self.tree.insert("", "end", values=row)
			
	def leer_tabla (self):
		"""Recorre todas las filas de la tabla y devuelve una lista con sus valores"""
		datos = []
		for item_id in self.tree.get_children():  # IDs de cada fila
			fila = self.tree.item(item_id, "values")  # tupla con los valores de las columnas
			#print(fila)  # mostrar en consola debug
			datos.append(fila)
		return datos

class Header:
	def __init__(self):
		self.crea_diccionario()
		
	def crea_diccionario(self):
		""" Inicializa el direccionario con keys HEADER cabrillo"""
		self.header_dict = {}

		for linea in HEADER.strip().splitlines():
			if ":" in linea:  # aseguramos que la línea tiene separador
				clave, valor = linea.split(":", 1)  # split solo en el primer ':'
				self.header_dict[clave.strip()] = valor.strip()	
					
	def lee_diccionario(self):
		""" Lee el diccionario key , value"""
		res=""
		for key,value in self.header_dict.items():
			res += key +': '+value+'\n'
		return res
			
	def set_value(self,key,value):
		""" set key with value in dict"""
		self.header_dict[key]=value
			
class InterfaceGraphique(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Adif to Cabrillo by F4LEC')
		self.resizable(False, False)
		# self.geometry("1000x500")

		self.creeGui()
		
		#Crea Header
		self.cabecera= Header() #instancia Header
		
		#def __init__(self, parent, adif_records, mode=0):
		# Crear la hoja excel en FrameSup HEADER cabrillo
		self.hoja_header = HojaExcelApp(self.FrameSup, "",1)		

		# Crear la hoja excel en FrameMed QSOs
		self.hoja_qso = HojaExcelApp(self.FrameMed,"",0)
		
	def creeGui(self):
		# Frames para colocar diferentes partes
		self.FrameSup = tk.Frame(self, borderwidth=2)
		self.FrameSup.pack()

		self.FrameMed = tk.Frame(self, borderwidth=2)
		self.FrameMed.pack()

		self.FrameButtons = tk.Frame(self, borderwidth=2)
		self.FrameButtons.pack()

		# Botón para abrir archivo ADIF
		self.ReadFileButton = tk.Button(self.FrameButtons, text="Open ADIF", bg="red",
										command=self.OpenFile)
		self.ReadFileButton.grid(row=0, column=2)
		
		# Botón para exportar cabrillo
		self.WriteButton = tk.Button(self.FrameButtons, text="Write Cabrillo", bg="green",
										command=self.WriteFile)
		self.WriteButton.grid(row=0, column=3)	
			
	def WriteFile(self):
		# Abre la ventana para seleccionar ubicación y nombre del archivo a guardar
		ruta_guardado = filedialog.asksaveasfilename(
			title="Guardar archivo como",
			defaultextension=".log",  # extensión por defecto
			filetypes=[("Archivos logs", "*.log"), ("Todos los archivos", "*.*")]
		)
		
		if ruta_guardado:
			# contendio a escribir
			contenido= self.tabla_to_cabrillo () #
			#contenido = "Este es el contenido que quiero guardar en el archivo."
			
			# Abrir el archivo en modo escritura y guardar el contenido
			with open(ruta_guardado, "w", encoding="utf-8") as archivo:
				archivo.write(contenido)
			print(f"Archivo guardado en: {ruta_guardado}")
		else:
			print("Guardado cancelado")		

	def OpenFile(self):
		""" Carga un fichero Adif creado con KLOG  """
		ruta_fichero = filedialog.askopenfilename(
			title="Selecciona el archivo ADIF",
			filetypes=[("Archivos ADIF", "*.adi *.adif"), ("Todos los archivos", "*.*")]
		)

		if not ruta_fichero:
			print("No se ha seleccionado ningún archivo.")
			return

		with open(ruta_fichero, encoding='utf8') as f:
			adif_data = f.read()

		adif_records_raw = adif_data.split("<EOR>")
		datos_tabla = []

		for record in adif_records_raw:
			if "<CALL:" in record:
				adif = self.parse_adif_record(record)
				self.station_callsign=adif ["STATION_CALLSIGN"] #Lo utilizo en el HEADER
				# Añadimos columnas a la hoja excel
				datos_tabla.append([adif["FREQ"], adif["MODE"],adif["QSO_DATE"], adif["TIME_ON"],adif ["STATION_CALLSIGN"],adif ["RST_SENT"],adif["CALL"],adif["RST_RCVD"]])
				#line = self.adif_to_cabrillo_line(adif)
				#print(line)
		
		# Cargamos nuevos datos en la tabla
		self.hoja_qso.cargar_datos(datos_tabla)


	def get_field(name,record):
		match = re.search(fr"<{name}:(\d+)>(.*?)($|<)", record)
		return match.group(2).strip() if match else ""
		
	def parse_adif_record(self, record):
		"""Recupera datos del ADIF klog crea  KEYs  para cabrillo
		<CALL:6>IU7QCK <QSO_DATE:8>20250809 <TIME_ON:6>080500 <FREQ:6>14.227 <BAND:3>20M <FREQ_RX:6>14.227 <BAND_RX:3>20M <MODE:3>SSB <MY_GRIDSQUARE:8>JN33JU07 <STATION_CALLSIGN:5>F4LEC <CQZ:2>15 <ITUZ:2>28 <DXCC:3>248 <CONT:2>EU <CONTACTED_OP:0> <EQ_CALL:0> <EQSL_QSLSDATE:8>20250809 <EQSL_QSL_SENT:1>Q <LOTW_QSLSDATE:8>20250809 <LOTW_QSL_SENT:1>Q <CLUBLOG_QSO_UPLOAD_DATE:8>20250809 <CLUBLOG_QSO_UPLOAD_STATUS:1>M <OPERATOR:0> <OWNER_CALLSIGN:0> <RST_SENT:2>59 <RST_RCVD:2>59 <TX_PWR:2>50 <EOR>"""

		def get_field(name):
			match = re.search(fr"<{name}:(\d+)>(.*?)($|<)", record)
			return match.group(2).strip() if match else ""
		return {# <RST_SENT:2>59 <RST_RCVD:2>59
			"CALL": get_field("CALL"),
			#"QSO_DATE": get_field("QSO_DATE"),
			"QSO_DATE": f"{get_field('QSO_DATE')[:4]}-{get_field('QSO_DATE')[4:6]}-{get_field('QSO_DATE')[6:8]}",
			"TIME_ON": get_field("TIME_ON")[:4],
			"FREQ": (get_field("FREQ") or "").replace('.', ''),
			"MODE": get_field("MODE"),
			"STATION_CALLSIGN": get_field("STATION_CALLSIGN"),
			"RST_SENT": get_field("RST_SENT"),
			"RST_RCVD": get_field("RST_RCVD"),            
		}

	def adif_to_cabrillo_line(self, adif):
		""" Crea linea cabrillo
		QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
		QSO: 14242 PH 2025-08-09  0801 F4LEC          59  05     HA2YL         59  05     0
		QSO: 14227 PH 2025-08-09  0805 F4LEC          59  05     IU7QCK        59  05     0
		"""        
		freq = adif["FREQ"].replace('.', '')
		modo = "PH" if adif["MODE"].upper() in ["SSB", "PH"] else adif["MODE"].upper()
		fecha = f"{adif['QSO_DATE'][:4]}-{adif['QSO_DATE'][4:6]}-{adif['QSO_DATE'][6:8]}"
		#hora = adif['TIME_ON'][:2] + adif['TIME_ON'][2:4]
		hora = adif['TIME_ON'][:6]
		return f"QSO: {freq:5} {modo:2} {fecha}  {hora} {adif['STATION_CALLSIGN']:12}   {adif ['RST_SENT']:4}     {adif['CALL']:12} {adif ['RST_RCVD']:4}"

	def tabla_to_cabrillo(self):
		#QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
		lista= self.hoja_qso.leer_tabla () #Lista de tuplas
		
		self.set_header() #configura el HEADER
		res=self.cabecera.lee_diccionario()#Lee HEADER cabrillo
		for qso in lista:#Lineas QSOs
			#print(qso) # tupla QSO
			res +="QSO: "
			for data in qso: #recorre las tuplas, los QSOs
				res += data + "\t"
			res +='\n'
		
		return res
		
	def set_header(self):
		""" configura HEADER cabrillo con Datos """
		self.cabecera.set_value("CALLSIGN",self.station_callsign)
		
if __name__ == "__main__":
    print("soft version ", VERSION_SOFT)
    app = InterfaceGraphique()
    app.mainloop()

"""
CABRILLO EXAMPLE 

START-OF-LOG: 3.0
CONTEST: 
CALLSIGN: 
LOCATION: 
CATEGORY-OPERATOR: 
CATEGORY-ASSISTED: 
CATEGORY-BAND: 
CATEGORY-POWER: 
CATEGORY-MODE: 
CATEGORY-TRANSMITTER: 
CATEGORY-OVERLAY: 
GRID-LOCATOR: 
CLAIMED-SCORE: 
CLUB: 
CREATED-BY: 
NAME: 
ADDRESS: 
ADDRESS-CITY: 
ADDRESS-STATE-PROVINCE: 
ADDRESS-POSTALCODE: 
ADDRESS-COUNTRY:
OPERATORS: 
SOAPBOX: .

QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
QSO: 14242 PH 2025-08-09  0801 F4LEC          59  05     HA2YL         59  05     0
QSO: 14227 PH 2025-08-09  0805 F4LEC          59  05     IU7QCK        59  05     0
END-OF-LOG:

--------------------------------------------------------------------------------------
ADIF EXAMPLE

ADIF v3.1.0 Export from KLog
https://www.klog.xyz/klog
<PROGRAMVERSION:3>2.3
<PROGRAMID:4>KLOG 
<APP_KLOG_QSOS:2>19
<APP_KLOG_LOG_DATE_EXPORT:13>20250812-1012
<EOH>
<CALL:5>IQ4FE <QSO_DATE:8>20250809 <TIME_ON:6>075200 <FREQ:5>7.148 <BAND:3>40M <FREQ_RX:5>7.148 <BAND_RX:3>40M <MODE:3>SSB <MY_GRIDSQUARE:8>JN33JU07 <STATION_CALLSIGN:5>F4LEC <CQZ:2>15 <ITUZ:2>28 <DXCC:3>248 <CONT:2>EU <CONTACTED_OP:0> <EQ_CALL:0> <EQSL_QSLSDATE:8>20250809 <EQSL_QSL_SENT:1>Q <LOTW_QSLSDATE:8>20250809 <LOTW_QSL_SENT:1>Q <CLUBLOG_QSO_UPLOAD_DATE:8>20250809 <CLUBLOG_QSO_UPLOAD_STATUS:1>M <OPERATOR:0> <OWNER_CALLSIGN:0> <RST_SENT:2>59 <RST_RCVD:2>59 <TX_PWR:2>50 <EOR>
<CALL:5>HA2YL <QSO_DATE:8>20250809 <TIME_ON:6>080100 <FREQ:6>14.242 <BAND:3>20M <FREQ_RX:6>14.242 <BAND_RX:3>20M <MODE:3>SSB <MY_GRIDSQUARE:8>JN33JU07 <STATION_CALLSIGN:5>F4LEC <CQZ:2>15 <ITUZ:2>28 <DXCC:3>239 <CONT:2>EU <CONTACTED_OP:0> <EQ_CALL:0> <EQSL_QSLSDATE:8>20250809 <EQSL_QSL_SENT:1>Q <LOTW_QSLSDATE:8>20250809 <LOTW_QSL_SENT:1>Q <CLUBLOG_QSO_UPLOAD_DATE:8>20250809 <CLUBLOG_QSO_UPLOAD_STATUS:1>M <OPERATOR:0> <OWNER_CALLSIGN:0> <RST_SENT:2>59 <RST_RCVD:2>59 <TX_PWR:2>50 <EOR>
<CALL:6>IU7QCK <QSO_DATE:8>20250809 <TIME_ON:6>080500 <FREQ:6>14.227 <BAND:3>20M <FREQ_RX:6>14.227 <BAND_RX:3>20M <MODE:3>SSB <MY_GRIDSQUARE:8>JN33JU07 <STATION_CALLSIGN:5>F4LEC <CQZ:2>15 <ITUZ:2>28 <DXCC:3>248 <CONT:2>EU <CONTACTED_OP:0> <EQ_CALL:0> <EQSL_QSLSDATE:8>20250809 <EQSL_QSL_SENT:1>Q <LOTW_QSLSDATE:8>20250809 <LOTW_QSL_SENT:1>Q <CLUBLOG_QSO_UPLOAD_DATE:8>20250809 <CLUBLOG_QSO_UPLOAD_STATUS:1>M <OPERATOR:0> <OWNER_CALLSIGN:0> <RST_SENT:2>59 <RST_RCVD:2>59 <TX_PWR:2>50 <EOR>

"""
