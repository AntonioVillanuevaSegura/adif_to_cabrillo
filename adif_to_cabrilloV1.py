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
	"""Crea las hojas excel para mostrar datos en la parte grafica """
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
	""" Header cabrillo se utiliza en la clase AdifCabrillo"""
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

class AdifCabrillo:
	""" clase para gestion Adif y Cabrillo"""
	def __init__(self,adif_data,hoja_excel_app):
		self.header=Header()
		self.adif_data=adif_data
		self.hoja_excel_app=hoja_excel_app #instancia HojaExcelApp
		
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
			#"FREQ": (get_field("FREQ") or "").replace('.', ''),
			"FREQ": (get_field("FREQ") or "").replace('.', '').ljust(4, '0'),
			"MODE": get_field("MODE"),
			"STATION_CALLSIGN": get_field("STATION_CALLSIGN"),
			"RST_SENT": get_field("RST_SENT"),
			"RST_RCVD": get_field("RST_RCVD"),            
		}
	"""
	def adif_to_cabrillo_line(self, adif):
		# Crea linea cabrillo
		#QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
     
		freq = adif["FREQ"].replace('.', '')
		modo = "PH" if adif["MODE"].upper() in ["SSB", "PH"] else adif["MODE"].upper()
		fecha = f"{adif['QSO_DATE'][:4]}-{adif['QSO_DATE'][4:6]}-{adif['QSO_DATE'][6:8]}"
		#hora = adif['TIME_ON'][:2] + adif['TIME_ON'][2:4]
		hora = adif['TIME_ON'][:6]
		return f"QSO: {freq:5} {modo:2} {fecha}  {hora} {adif['STATION_CALLSIGN']:12}   {adif ['RST_SENT']:4}     {adif['CALL']:12} {adif ['RST_RCVD']:4}"
	"""
	def formatear_qso_tuple(self,qso_tuple):
		""" formatea espacios segun norma cabrillo"""
		freq, mode, date, time, call1, rst1, call2, rst2 = qso_tuple
		return (
			f"QSO: {freq:>5} "
			f"{mode:<3} "
			f"{date} "
			f"{time:>4} "
			f"{call1:<13} "
			f"{rst1:<3} "
			f"{call2:<13} "
			f"{rst2:<3}"
		)
		
	def tabla_to_cabrillo(self):
		#QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
		#lista= self.hoja_excel_app.hoja_qso.leer_tabla () #Lista de tuplas
		lista= self.hoja_excel_app.leer_tabla () #Lista de tuplas
		
		#Configura el Header
		#self.set_header() #configura el HEADER
		
		res=self.header.lee_diccionario()#Lee HEADER cabrillo
		
		for qso in lista:#Lineas QSOs
			#print(qso) # tupla QSO
			res +=self.formatear_qso_tuple(qso)
			"""
			res +="QSO: "
			for data in qso: #recorre las tuplas, los QSOs
				res += data + "\t"
			"""
			res +='\n'
		
		return res
		
	def set_header(self,header_dict):
		""" recupera un diccionario con los valores del header CABRILLO """
		self.header.set_value("CONTEST",header_dict ["CONTEST"] )		
		self.header.set_value("CALLSIGN",header_dict ["CALLSIGN"] )
		self.header.set_value("LOCATION",header_dict ["LOCATION"] )
		self.header.set_value("CATEGORY-OPERATOR",header_dict ["CATEGORY-OPERATOR"] )
		self.header.set_value("CATEGORY-ASSISTED",header_dict ["CATEGORY-ASSISTED"] )
		self.header.set_value("CATEGORY-BAND",header_dict ["CATEGORY-BAND"] )	
		self.header.set_value("CATEGORY-POWER",header_dict ["CATEGORY-POWER"] )
		self.header.set_value("CATEGORY-MODE",header_dict ["CATEGORY-MODE"] )
		self.header.set_value("CATEGORY-TRANSMITTER",header_dict ["CATEGORY-TRANSMITTER"] )
		self.header.set_value("CATEGORY-OVERLAY",header_dict ["CATEGORY-OVERLAY"] )	
		self.header.set_value("GRID-LOCATOR",header_dict ["GRID-LOCATOR"] )
		self.header.set_value("CLAIMED-SCORE",header_dict ["CLAIMED-SCORE"] )
		self.header.set_value("CLUB",header_dict ["CLUB"] )
		self.header.set_value("NAME",header_dict ["NAME"] )	
		self.header.set_value("ADDRESS",header_dict ["ADDRESS"] )
		self.header.set_value("ADDRESS-CITY",header_dict ["ADDRESS-CITY"] )
		self.header.set_value("ADDRESS-STATE-PROVINCE",header_dict ["ADDRESS-STATE-PROVINCE"] )
		self.header.set_value("ADDRESS-POSTALCODE",header_dict ["ADDRESS-POSTALCODE"] )	
		self.header.set_value("ADDRESS-COUNTRY",header_dict ["ADDRESS-COUNTRY"] )
		self.header.set_value("OPERATORS",header_dict ["OPERATORS"] )
		self.header.set_value("SOAPBOX",header_dict ["SOAPBOX"] )

	def carga_adif(self):
		adif_records_raw = self.adif_data.split("<EOR>")
		datos_tabla = [] #Crea una lista 

		for record in adif_records_raw:
			if "<CALL:" in record:
				adif = self.parse_adif_record(record)
				self.station_callsign=adif ["STATION_CALLSIGN"] #Lo utilizo en el HEADER
				# Añadimos columnas a la hoja excel
				datos_tabla.append([adif["FREQ"], adif["MODE"],adif["QSO_DATE"], adif["TIME_ON"],adif ["STATION_CALLSIGN"],adif ["RST_SENT"],adif["CALL"],adif["RST_RCVD"]])
				#line = self.adif_to_cabrillo_line(adif)
				#print(line)

		# Cargamos nuevos datos en la tabla
		#self.hoja_qso.cargar_datos(datos_tabla)	
		return datos_tabla #devuelve una lista para cargar en la hoja excel

			
class InterfaceGraphique(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Adif to Cabrillo by F4LEC')
		self.resizable(False, False)
		# self.geometry("1000x500")
		
		#Declara Variables HEAD cabrillo
		self.variablesCabrillo()
		
		self.creeGui()
		
		#instancia clase header Header
		self.cabecera= Header() 
		
		# Crear la hoja excel en FrameSup HEADER CABRILLO
		#self.hoja_header = HojaExcelApp(self.FrameSup, "",1)		

		# Crear la hoja excel en FrameMed QSOs
		self.hoja_qso = HojaExcelApp(self.FrameMed,"",0)		
		
	def mostrar_config(self):
		if self.FrameSup.winfo_ismapped():
			self.FrameSup.grid_remove()
		else:
			self.FrameSup.grid()
		
	def creeGui(self):
		# Frames para colocar diferentes partes
		self.FrameSup = tk.Frame(self, borderwidth=2)
		self.FrameSup.grid(row=0, column=0, sticky="nsew")

		self.FrameMed = tk.Frame(self, borderwidth=2)
		self.FrameMed.grid(row=1, column=0, sticky="nsew")

		self.FrameButtons = tk.Frame(self, borderwidth=2)
		self.FrameButtons.grid(row=2, column=0, sticky="ew")

		# Botón para abrir archivo ADIF
		self.ReadFileButton = tk.Button(self.FrameButtons, text="Open ADIF", bg="red",
										command=self.OpenFile)
		self.ReadFileButton.grid(row=0, column=2)
		
		# Botón para exportar cabrillo
		self.WriteButton = tk.Button(self.FrameButtons, text="Write Cabrillo", bg="green",
										command=self.WriteFile)
		self.WriteButton.grid(row=0, column=3)	
		
		#Boton ocultar configuracion
		self.boton_mostrar = tk.Button(self.FrameButtons, text="Config",bg="Yellow" ,
										command = self.mostrar_config)
										
		self.boton_mostrar.grid(row=0, column=4)
		
		self.headerCabrillo()		
	
	def variablesCabrillo(self):
		""" variables tk utilizadas en el HEAD cabrillo"""
		#Variables HEAD cabrillo
		self.contest_var = tk.StringVar()		
		self.callsign_var = tk.StringVar()
		self.location_var = tk.StringVar()
		self.category_operator_var = tk.StringVar()
		self.category_assisted_var=tk.StringVar()
		self.category_band_var = tk.StringVar()
		self.category_power_var = tk.StringVar()
		self.category_mode_var = tk.StringVar()	
		self.category_transmiter_var = tk.StringVar()
		self.category_overlay_var =tk.StringVar()
		self.grid_locator_var=tk.StringVar()			
		self.claimed_score_var = tk.StringVar()		
		self.club_var = tk.StringVar()
		self.name_var = tk.StringVar()
		self.address_var = tk.StringVar()
		self.address_city_var = tk.StringVar()
		self.address_state_var = tk.StringVar()
		self.address_postalcode_var = tk.StringVar()
		self.address_country_var = tk.StringVar()
		self.operators_var = tk.StringVar()
		self.soapbox_var = tk.Text()	
			
	def creaDiccionarioHeader (self):
		""" Crea un diccionario  para pasar a otra clase """
		header_cabrillo_dict= dict()
		header_cabrillo_dict['CONTEST']=self.contest_var.get()		
		header_cabrillo_dict['CALLSIGN']=self.callsign_var.get()
		header_cabrillo_dict['LOCATION']=self.location_var.get()
		header_cabrillo_dict['CATEGORY-OPERATOR']=self.category_operator_var.get()
		header_cabrillo_dict['CATEGORY-ASSISTED']=self.category_assisted_var.get()
		header_cabrillo_dict['CATEGORY-BAND']=self.category_band_var.get()
		header_cabrillo_dict['CATEGORY-POWER']=self.category_power_var.get()
		header_cabrillo_dict['CATEGORY-MODE']=self.category_mode_var.get()
		header_cabrillo_dict['CATEGORY-TRANSMITTER']=self.category_transmiter_var.get()
		header_cabrillo_dict['CATEGORY-OVERLAY']=self.category_overlay_var.get()
		header_cabrillo_dict['GRID-LOCATOR']=self.grid_locator_var.get()
		header_cabrillo_dict['CLAIMED-SCORE']=self.claimed_score_var.get()
		header_cabrillo_dict['CLUB']=self.club_var .get()
		header_cabrillo_dict['NAME']=self.name_var.get()
		header_cabrillo_dict['ADDRESS']=self.address_var.get()
		header_cabrillo_dict['ADDRESS-CITY']=self.address_city_var.get()
		header_cabrillo_dict['ADDRESS-STATE-PROVINCE']=self.address_state_var.get()
		header_cabrillo_dict['ADDRESS-POSTALCODE']=self.address_postalcode_var.get()
		header_cabrillo_dict['ADDRESS-COUNTRY']=self.address_country_var.get()
		header_cabrillo_dict['OPERATORS']=self.operators_var.get()
		header_cabrillo_dict['SOAPBOX']=self.soapbox_text.get("1.0", "end").strip() [:68]
		return header_cabrillo_dict

	def headerCabrillo (self):	
		""" campos graficos HEAD cabrillo"""
		# Opciones categorias
		operator_options = ['SINGLE-OP', 'MULTI-OP', 'CHECKLOG']
		assisted_options = ['ASSISTED', 'NON-ASSISTED']
		band_options = ['ALL','160M', '80M', '40M', '20M', '15M', '10M', '6M', '2M']
		power_options = ['HIGH', 'LOW', 'QRP']
		mode_options = ['SSB','CW','AM','FM']
		transmitter_options = ['ONE', 'TWO', 'UNLIMITED']
		overlay_options = ['CATEGORY-OVERLAY: CLASSIC', 'CATEGORY-OVERLAY: ROOKIE', 'CATEGORY-OVERLAY:  YOUTH']
		certificate_options= ['YES','NO']

		#  Frame superior self.FrameSup
		
		tk.Label(self.FrameSup, text="CONTEST:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
		tk.Entry(self.FrameSup, textvariable=self.contest_var).grid(row=0, column=3, sticky="we", padx=5, pady=2)		
		
		tk.Label(self.FrameSup, text="CALLSIGN:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(self.FrameSup, textvariable=self.callsign_var).grid(row=0, column=1, sticky="we", padx=5, pady=2)

		tk.Label(self.FrameSup, text="LOCATION:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(self.FrameSup, textvariable=self.location_var).grid(row=1, column=1, sticky="we", padx=5, pady=2)

		tk.Label(self.FrameSup, text="CATEGORY-OPERATOR:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
		ttk.Combobox(self.FrameSup, textvariable=self.category_operator_var, values=operator_options, state="readonly").grid(row=2, column=1, sticky="we", padx=5, pady=2)
		self.category_operator_var.set(operator_options[0])

		tk.Label(self.FrameSup, text="CATEGORY-ASSISTED:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
		ttk.Combobox(self.FrameSup, textvariable=self.category_assisted_var, values=assisted_options, state="readonly").grid(row=3, column=1, sticky="we", padx=5, pady=2)
		
		tk.Label(self.FrameSup, text="CATEGORY-BAND:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
		ttk.Combobox(self.FrameSup, textvariable=self.category_band_var, values=band_options, state="readonly").grid(row=4, column=1, sticky="we", padx=5, pady=2)
		self.category_band_var.set(band_options[0])		
		
		tk.Label(self.FrameSup, text="CATEGORY-POWER:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
		ttk.Combobox(self.FrameSup, textvariable=self.category_power_var, values=power_options, state="readonly").grid(row=5, column=1, sticky="we", padx=5, pady=2)
		self.category_power_var.set(power_options[0])
			
		tk.Label(self.FrameSup, text="CATEGORY-MODE:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
		ttk.Combobox(self.FrameSup, textvariable=self.category_mode_var, values=mode_options, state="readonly").grid(row=6, column=1, sticky="we", padx=5, pady=2)
		self.category_mode_var.set(mode_options[0])	
		
		tk.Label(self.FrameSup, text="CATEGORY-TRANSMITER:").grid(row=7, column=0, sticky="e", padx=5, pady=2)
		ttk.Combobox(self.FrameSup, textvariable=self.category_transmiter_var, values=transmitter_options , state="readonly").grid(row=7, column=1, sticky="we", padx=5, pady=2)
				
		tk.Label(self.FrameSup, text="CLAIMED-SCORE:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(self.FrameSup, textvariable=self.claimed_score_var).grid(row=8, column=1, sticky="we", padx=5, pady=2)
	
		tk.Label(self.FrameSup, text="CLUB:").grid(row=9, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(self.FrameSup, textvariable=self.club_var).grid(row=9, column=1, sticky="we", padx=5, pady=2)
		
		# Dirección 
		
		addr_frame = tk.LabelFrame(self.FrameSup, text="Dirección")
		addr_frame.grid(row=10, column=0, columnspan=2, sticky="we", padx=5, pady=5)

		tk.Label(addr_frame, text="NAME:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.name_var).grid(row=0, column=1, sticky="we", padx=5, pady=2)
	
		tk.Label(addr_frame, text="ADDRESS:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.address_var).grid(row=1, column=1, sticky="we", padx=5, pady=2)

		tk.Label(addr_frame, text="CITY:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.address_city_var).grid(row=2, column=1, sticky="we", padx=5, pady=2)

		tk.Label(addr_frame, text="STATE/PROVINCE:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.address_state_var).grid(row=3, column=1, sticky="we", padx=5, pady=2)

		tk.Label(addr_frame, text="POSTAL CODE:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.address_postalcode_var).grid(row=4, column=1, sticky="we", padx=5, pady=2)

		tk.Label(addr_frame, text="COUNTRY:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.address_country_var).grid(row=5, column=1, sticky="we", padx=5, pady=2)
		
		tk.Label(addr_frame, text="GRID-LOCATOR:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
		tk.Entry(addr_frame, textvariable=self.grid_locator_var).grid(row=6, column=1, sticky="we", padx=5, pady=2)		
	
		# SOAPBOX multilinea
		tk.Label(self.FrameSup, text="SOAPBOX:").grid(row=11, column=0, sticky="ne", padx=5, pady=2)
		self.soapbox_text = tk.Text(self.FrameSup, height=4, width=40)
		self.soapbox_text.grid(row=11, column=1, sticky="we", padx=5, pady=2)
		
		self.soapbox_var = self.soapbox_text.get("1.0", "end").strip()
		
		self.columnconfigure(1, weight=1)
		addr_frame.columnconfigure(1, weight=1)		
		
	def WriteFile(self):
		#Enviar datos del header CABRILLO para pasar a clase AdifCabrillo
		header_cabrillo_dict = self.creaDiccionarioHeader () 
		
		#Enviar datos diccionario HEADER a la instancia de clase
		self.adif_cabrillo.set_header (header_cabrillo_dict) #
		
		# Abre la ventana para seleccionar ubicación y nombre del archivo a guardar
		ruta_guardado = filedialog.asksaveasfilename(
			title="Guardar archivo como",
			defaultextension=".log",  # extensión por defecto
			filetypes=[("Archivos logs", "*.log"), ("Todos los archivos", "*.*")]
		)
		
		if ruta_guardado:
			# contendio a escribir
			contenido= self.adif_cabrillo.tabla_to_cabrillo () #
			
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
			
		#Instancia clase AdifCabrillo
		self.adif_cabrillo =AdifCabrillo(adif_data,self.hoja_qso)	
			
		#lista con datos del QSO desde el Adif cargado	
		datos_tabla = self.adif_cabrillo.carga_adif() 
		
		#Recupera el indicativo desde el Adif 
		#self.station_callsign = self.adif_cabrillo.get_callsign()		
		
		#Crea Excel con estos datos ,  en el programa
		self.hoja_qso.cargar_datos(datos_tabla)


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
