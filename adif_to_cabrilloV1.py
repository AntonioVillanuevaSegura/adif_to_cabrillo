"""
F4LEC Antonio Villanueva
Conversor Adif a Cabrillo , para los concursos 
Recupera el Adif creado con Klog y lo convierte en Cabrillo

24/02/26 anado opcion contest COUPE DU REF , hay que escribir REF-SSB en CONTEST
bug 28/10/25 error frecuencia Klog crear  14.2 o 28.43 y cabrillo produce 1420 o 2843 parse_adif_record

Se pueden modificar las celdas manualmente o utilizar algun
automatismo del combobox .... Cada concurso es diferente
antes de enviar confirmar que todo este bien 

59+SERIE introduce 59 + un numero incremental 
SERIE Solo introduce un incremental en SERIAL_SEND
59+DATO Introduce 59 + el dato que recupera en la entrada 
DATO Solo recupera el dato en la entrada 
COMMENT recupera de los comentarios el primer campo para SERIAL_SEND
y SERIAL_RCVD , pueden estar separados por espacio , - o /

para COUPE du REF REF-SSB ejemplo

START-OF-LOG: 2.0
REF-SECTION: 06
CALLSIGN: F4LEC
CATEGORY: SINGLE-OP ALL LOW
CLAIMED-SCORE:  33810
CONTEST: REF-SSB
CREATED-BY: WINREF-HF V9.7.18
NAME: VILLANUEVA ANTONIO
ADDRESS:  BEAUSOLEIL  FRANCE
RIG: ICOM 7300

"""
#https://cqww.com/cabrillo.htm

import tkinter as tk #Gui
from tkinter import ttk, filedialog, END
from tkinter import filedialog
from tkinter import colorchooser

import re

VERSION_SOFT= "3.0"
	
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

#CONTEST REF-SSB COUPE Du REF
HEADER_COUPE_DU_REF="""START-OF-LOG: 2.0
REF-SECTION:
CALLSIGN:
CATEGORY:
CLAIMED-SCORE:
CONTEST:
CREATED-BY: 
NAME: 
ADDRESS:
RIG:
"""

class HojaExcelApp:
	"""Crea las hojas excel para mostrar datos en la parte grafica """
	def __init__(self, parent, adif_records, mode=0):
		self.parent = parent
		self.adif_records = adif_records
		self.crear_hoja_excel(mode)

	def crear_hoja_excel(self,mode=0):
		columns = ("FREQ_RX", "MODE", "QSO_DATE", "TIME_ON",
				   "STATION_CALLSIGN", "SERIAL_SEND", "CALL", "SERIAL_RCVD","COMMENT")
		if mode == 1:
			# Creamos la lista solo con las claves antes de ":"
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
		#self.modifica_columnas_serial() #TEST
					
	def leer_tabla (self):
		"""Recorre todas las filas de la tabla y devuelve una lista con sus valores"""
		datos = []
		for item_id in self.tree.get_children():  # IDs de cada fila
			fila = self.tree.item(item_id, "values")  # tupla con los valores de las columnas
			#print(fila)  # mostrar en consola debug
			datos.append(fila)
		return datos

	def numero_filas(self):
		""" numero de lineas filas del tablero """
		# Obtener todos los ítems en la raíz (nivel superior)
		items = self.tree.get_children()

		# Cantidad de filas
		return len(items)
		
	def modifica_columnas_serial (self,value="59"):
		""" modifica el SERIAL_SEND de forma numerica """
		for linea in range (0,self.numero_filas()):
			valor_str = f"{linea:03d}"
			self.modifica_columna(linea, "SERIAL_SEND", value +" "+ valor_str)

	def modifica_columnas_modelo (self,value="59"):
		""" modifica el SERIAL_SEND segun modelo """
		for linea in range (0,self.numero_filas()):
			self.modifica_columna(linea, "SERIAL_SEND", value )			
		
	def modifica_columna(self,linea, col, value):
		""" modifica una linea de una columna"""
		#ej :self.modifica_columna(0, "SEND_VALUE", "XXX")	
		items = self.tree.get_children()
		if items:
			primer_item = items[linea]
			self.tree.set(primer_item, col, value)
				
	def modifica_con_comentario(self,dato):
		"""Recupera la primera parte del comentario para SERIAL_SEND"""
		items = self.tree.get_children()  # Obtener todos los ítems (filas)
		for linea in range(self.numero_filas()):
			item_id = items[linea]  # ID del ítem en esa fila
			# Obtener el valor de la columna 'comment' para este ítem
			comment_valor = self.tree.set(item_id, "COMMENT")
			
			first_value=""
			second_value=""
			
			#Analiza posibles separadores COMMENT TIPO 5906 5983 p.e
			separadores = ["/", "=", " ", ","]
			
			if (any(sep in comment_valor for sep in separadores)):
			
				if '-' in comment_valor:
					first_value = comment_valor.split('-', 1)[0]     # primer campo antes de separador
					if len(comment_valor)>1:
						second_value = comment_valor.split('-', 1)[1]     #2° campo despues separador
				elif ',' in comment_valor:	
					first_value = comment_valor.split(',', 1)[0]     # primer campo antes de separador
					if len(comment_valor)>1:				
						second_value = comment_valor.split(',', 1)[1]     #2° campo despues separador	
				elif '/' in comment_valor:	
					first_value = comment_valor.split('/', 1)[0]      # primer campo antes de separador
					if len(comment_valor)>1:				
						second_value = comment_valor.split('/', 1)[1]     #2° campo despues separador					
				elif ' ' in comment_valor:			
					first_value = comment_valor.split(' ', 1)[0]		# primer campo antes de separador
					if len(comment_valor)>1:				
							second_value = comment_valor.split(' ', 1)[1]     #2° campo despues separador					
			else:#Comment solo tiene 1  valor retornado por el contacto RCVD
				if dato.get()=="":
					first_value="59 XX"
				else:
					first_value="59 "+dato.get() #59 +recupera DATO 
				second_value="59 "+	comment_valor
			
			#Crea un espacio entre 59 y el control
			first_value = first_value[:2] + "  " + first_value[2:]
			second_value = second_value[:2] + "  " + second_value[2:]			
			
			self.modifica_columna(linea, "SERIAL_SEND", first_value)
			
			if second_value:
				self.modifica_columna(linea, "SERIAL_RCVD", second_value)
			else:
				self.modifica_columna(linea, "SERIAL_RCVD", "") #Vacio
				
	def modifica_con_comentario59(self):
		"""Recupera la primera parte del comentario para SERIAL_SEND y anade 59 delante"""
		items = self.tree.get_children()  # Obtener todos los ítems (filas)
		for linea in range(self.numero_filas()):
			item_id = items[linea]  # ID del ítem en esa fila
			# Obtener el valor de la columna 'comment' para este ítem
			comment_valor = self.tree.set(item_id, "COMMENT")
			
			first_value=""
			second_value=""
			
			if '-' in comment_valor:
				first_value = comment_valor.split('-', 1)[0]     # primer campo antes de separador
				if len(comment_valor)>1:
					second_value = comment_valor.split('-', 1)[1]     #2° campo despues separador
			elif ',' in comment_valor:	
				first_value = comment_valor.split(',', 1)[0]     # primer campo antes de separador
				if len(comment_valor)>1:				
					second_value = comment_valor.split(',', 1)[1]     #2° campo despues separador	
			elif '/' in comment_valor:	
				first_value = comment_valor.split('/', 1)[0]      # primer campo antes de separador
				if len(comment_valor)>1:				
					second_value = comment_valor.split('/', 1)[1]     #2° campo despues separador					
			elif ' ' in comment_valor:			
				first_value = comment_valor.split(' ', 1)[0]		# primer campo antes de separador
				if len(comment_valor)>1:				
						second_value = comment_valor.split(' ', 1)[1]     #2° campo despues separador					
					
			#print(f"Fila {linea} - COMMENT: {comment_valor}") #Debug
			
			self.modifica_columna(linea, "SERIAL_SEND", "59 "+first_value)
			
			if second_value:
				self.modifica_columna(linea, "SERIAL_RCVD","59 "+ second_value)
			else:
				self.modifica_columna(linea, "SERIAL_RCVD", "") #Vacio				
				
class Header:
	""" Header cabrillo crea 2 tipos de Header REF-SSB coupe du REF y normal"""
	def __init__(self,opcion=""):
		self.opcion =opcion		
		self.crea_diccionario()
		
	def crea_diccionario(self):
		""" Inicializa el direccionario con keys HEADER cabrillo"""
		self.header_dict = {}
		
		if self.opcion!="REF-SSB":
			print ("NORMAL en crea diccionario");
			for linea in HEADER.strip().splitlines():
				if ":" in linea:  # aseguramos que la línea tiene separador
					clave, valor = linea.split(":", 1)  # split solo en el primer ':'
					self.header_dict[clave.strip()] = valor.strip()	
		else:#REF-SSB
			print ("REF-SSB en crea diccionario");
			for linea in HEADER_COUPE_DU_REF.strip().splitlines():
				if ":" in linea:  # aseguramos que la línea tiene separador
					clave, valor = linea.split(":", 1)  # split solo en el primer ':'
					self.header_dict[clave.strip()] = valor.strip()			
						
	def lee_diccionario(self):
		""" Lee el diccionario key , value string """
		res=""
		for key,value in self.header_dict.items():
			res += key +': '+value+'\n'
		return res
		
	def get_diccionario(self):
		""" retorna el diccionario """
		return self.header_dict;
		
			
	def set_value(self,key,value):
		""" set key with value in dict"""
		self.header_dict[key]=value

class AdifCabrillo:
	""" clase para gestion Adif y Cabrillo"""
	def __init__(self,adif_data,hoja_excel_app):
		#self.header=Header()
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
			"QSO_DATE": f"{get_field('QSO_DATE')[:4]}-{get_field('QSO_DATE')[4:6]}-{get_field('QSO_DATE')[6:8]}",
			"TIME_ON": get_field("TIME_ON")[:4],
			#"FREQ": (get_field("FREQ") or "").replace('.', '').ljust(4, '0'),
			"FREQ": (lambda f: (f.replace('.', '').ljust(4 if f.split('.')[0] and len(f.split('.')[0]) == 1 else 5, '0')) if '.' in f else f)(
			get_field("FREQ") or ""),
			"MODE": get_field("MODE"),
			"STATION_CALLSIGN": get_field("STATION_CALLSIGN"),
			"RST_SENT": get_field("RST_SENT"),
			"RST_RCVD": get_field("RST_RCVD"),  
			"COMMENT": get_field("COMMENT"),            
		}

	def formatear_qso_tuple(self,qso_tuple):

		""" formatea espacios segun norma cabrillo"""
		freq, mode, date, time, call1, data1, call2, data2,*rest = qso_tuple
		return (
			f"QSO: {freq:>5} "
			f"{mode:<3} "
			f"{date} "
			f"{time:>4} "
			f"{call1:<13} "
			f"{data1:<3} "
			f"{call2:<13} "
			f"{data2:<3}"
		)
		
	def tabla_to_cabrillo(self):
		""" crea cabrillo desde los datos graficos de la tabla"""
		#QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
		lista= self.hoja_excel_app.leer_tabla () #Lista de tuplas
		
		#print ("Tabla to cabrillo")
		#self.header.crea_diccionario()
		#res=self.header.lee_diccionario()#Lee HEADER cabrillo
		
		res=""
		for qso in lista:#Lineas QSOs
			#print(qso) # tupla QSO debug
			res +=self.formatear_qso_tuple(qso)
			res +='\n'	
		res+="END-OF-LOG:"
		return res

	def carga_adif(self):
		adif_records_raw = self.adif_data.split("<EOR>")
		
		#print (adif_records_raw) #DEBUG
		datos_tabla = [] #Crea una lista 

		for record in adif_records_raw:#Recorre lineas y busca <CALL
			if "<CALL:" in record:
				adif = self.parse_adif_record(record)
				self.station_callsign=adif ["STATION_CALLSIGN"] #Lo utilizo en el HEADER
				
				# Añadimos columnas a la hoja excel
				if "COMMENT" in record:
					datos_tabla.append([ adif["FREQ"], adif["MODE"],adif["QSO_DATE"], adif["TIME_ON"],adif ["STATION_CALLSIGN"],adif ["RST_SENT"],adif["CALL"],adif["RST_RCVD"],adif["COMMENT"] ])
				else:
					datos_tabla.append([ adif["FREQ"], adif["MODE"],adif["QSO_DATE"], adif["TIME_ON"],adif ["STATION_CALLSIGN"],adif ["RST_SENT"],adif["CALL"],adif["RST_RCVD"] ])
				
				
		#elimina duplicados
		datos_tabla_sin_duplicados = list(map(list, set(map(tuple, datos_tabla))))
		datos_tabla =datos_tabla_sin_duplicados
		
		# Ordena datos_tabla por QSO_DATE y TIME_ON 
		datos_tabla.sort(key=lambda x: (x[2], x[3]))
		
		return datos_tabla #devuelve una lista para cargar en la hoja excel

	def get_callsign (self):
		""" return callsign """
		return self.station_callsign
		
class InterfaceGraphique(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Adif to Cabrillo by F4LEC')
		self.resizable(False, False)
		# self.geometry("1000x500")
		
		#Declara Variables HEAD cabrillo
		self.variablesCabrillo()
		
		self.creeGui()

		# Crear la hoja excel en FrameMed QSOs
		self.hoja_qso = HojaExcelApp(self.FrameMed,"",0)		
		
	def mostrar_config(self):
		if self.FrameSup.winfo_ismapped():
			self.FrameSup.grid_remove()
		else:
			self.FrameSup.grid()
		
	def creeGui(self):
		# Frames 
		#Frame HEADER cabrillo
		self.FrameSup = tk.Frame(self, borderwidth=2)
		self.FrameSup.grid(row=0, column=0, sticky="nsew")	
		
		#Frame tabla tipo excel , QSO adif->cabrillo
		self.FrameMed = tk.Frame(self, borderwidth=2)
		self.FrameMed.grid(row=1, column=0, sticky="nsew")

		#Frame botones inferiores, cargar adif, escribir cabrillo, ocultar
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
				
		#Combobox SERIAL_SEND : SERIAL_RCVD		
		self.serial_options_var = tk.StringVar()
		serial_options = ['59+SERIE','SERIE','59 + DATO','DATO','COMMENT',"59+COMMENT"]
		
		tk.Label(self.FrameButtons, text="SERIAL_SEND").grid(row=0, column=5, sticky="e", padx=5, pady=2)
		#self.combobox =ttk.Combobox(self.FrameButtons, textvariable=self.serial_options_var, values=serial_options, state="readonly").grid(row=0, column=6, sticky="we", padx=5, pady=2)
		
		self.combobox = ttk.Combobox(self.FrameButtons, textvariable=self.serial_options_var, values=serial_options, state="readonly")
		self.combobox.grid(row=0, column=6, sticky="we", padx=5, pady=2)
		self.serial_options_var.set(serial_options[0])
		self.combobox.bind("<<ComboboxSelected>>", self.on_combobox_change)
		
		self.data_serial_var = tk.StringVar()
		tk.Label(self.FrameButtons, text="DATO ").grid(row=0, column=8, sticky="e", padx=5, pady=2)
		tk.Entry(self.FrameButtons, textvariable=self.data_serial_var).grid(row=0, column=9, sticky="we", padx=5, pady=2)	
		
		#Header cabrillo en la parte superior ocultable
		self.headerCabrillo()		

	def on_combobox_change(self,event):
		""" Gestion Combobox SERIAL_SEND SERIAL_RCVD """
		selected_value = self.combobox.get()
		if selected_value =='59+SERIE': #Escribe 59 + numero serie
			print ("59+SERIE")
			self.hoja_qso.modifica_columnas_serial("59")
		elif selected_value =='SERIE': #Escribe solo numero de serie 
			self.hoja_qso.modifica_columnas_serial("")
		elif selected_value =='DATO': #Escribe solo un dato 
			self.hoja_qso.modifica_columnas_modelo(self.data_serial_var.get())	
		elif selected_value =='59 + DATO': #Escribe solo un dato 
			self.hoja_qso.modifica_columnas_modelo("59 "+self.data_serial_var.get())	
		elif selected_value =='COMMENT': #Recupera 1a parte comentario self.datos_tabla
			self.hoja_qso.modifica_con_comentario(self.data_serial_var)	#puede utilizar el DATO para crear 59 06 , 59 DATO	
		elif selected_value =='59+COMMENT': #Recupera 1a parte comentario self.datos_tabla
			self.hoja_qso.modifica_con_comentario59()										
			
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
			
	def setDiccionarioHeader (self,header_cabrillo_dict):
		""" Set un diccionario de tipo HEADER  """
		if self.contest_var.get()!="REF-SSB":
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
		else:
			header_cabrillo_dict['REF-SECTION']=self.location_var.get()			
			header_cabrillo_dict['CALLSIGN']=self.callsign_var.get()
			header_cabrillo_dict['CATEGORY']=self.category_mode_var.get()
			header_cabrillo_dict['CLAIMED-SCORE']=self.claimed_score_var.get()
			header_cabrillo_dict['CONTEST']="REF-SSB" 
			header_cabrillo_dict['CREATED-BY']="F4LEC"
			header_cabrillo_dict['NAME']=self.name_var.get()			
			header_cabrillo_dict['ADDRESS']=self.address_var.get()
			header_cabrillo_dict['RIG']=""
		return header_cabrillo_dict		

	def headerCabrillo (self):	
		""" campos graficos HEAD cabrillo Frame superior ocultable"""
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

		# Abre la ventana para seleccionar ubicación y nombre del archivo a guardar
		ruta_guardado = filedialog.asksaveasfilename(
			title="Guardar archivo como",
			defaultextension=".log",  # extensión por defecto
			filetypes=[("Archivos logs", "*.log"), ("Todos los archivos", "*.*")]
		)
		
		if ruta_guardado:
			#HEADERs 
			header_cabrillo =Header(self.contest_var.get());#Instancia Clase Header apropiado
			header_cabrillo_dict=header_cabrillo.get_diccionario() #Obtiene el diccionario
			self.setDiccionarioHeader (header_cabrillo_dict) #Set HEADER segun interface grafica
			contenido =header_cabrillo.lee_diccionario() #Lee el Header diccionario de forma string 
			
			contenido += self.adif_cabrillo.tabla_to_cabrillo () #
			
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
		self.datos_tabla = self.adif_cabrillo.carga_adif() 
		
		#Crea Excel con estos datos ,  en el programa instancia HojaExcelApp
		self.hoja_qso.cargar_datos(self.datos_tabla)	
		
		#Debug QSO 
		"""
		for sublista in self.datos_tabla:
			print(sublista)
		"""
		#Recupera el indicativo desde el Adif 
		self.station_callsign = self.adif_cabrillo.get_callsign()			
		#Afecta callsign en header	
		self.callsign_var.set(self.station_callsign)
		
if __name__ == "__main__":
    print("soft version ", VERSION_SOFT)
    app = InterfaceGraphique()
    app.mainloop()
