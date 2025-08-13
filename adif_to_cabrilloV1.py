import tkinter as tk #Gui
from tkinter import ttk
#from tktooltip import ToolTip #infobulles
from tkinter import filedialog
from tkinter import colorchooser

import re

VERSION_SOFT= "1"
	
import tkinter as tk
from tkinter import ttk, filedialog, END
import re

VERSION_SOFT = "1.0"


"""
QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0
QSO: 14242 PH 2025-08-09  0801 F4LEC          59  05     HA2YL         59  05     0
QSO: 14227 PH 2025-08-09  0805 F4LEC          59  05     IU7QCK        59  05     0
"""
class HojaExcelApp:

	def __init__(self, parent, adif_records):
		self.parent = parent
		self.adif_records = adif_records
		self.crear_hoja_excel()

	def update_cell(self):
		selected = self.tree.focus()
		if selected:
			self.tree.item(selected, values=(
				self.FREQ_RX.get(),
				self.MODE.get(),
				self.QSO_DATE.get(),
				self.TIME_ON.get(),
				self.STATION_CALLSIGN.get(),
				self.DATA1.get(),
				self.CALL.get(),
				self.DATA2.get()

			))

	def on_select(self, event):
		selected = self.tree.focus()
		if selected:
			values = self.tree.item(selected, "values")
			campos = [self.FREQ_RX, self.MODE, self.QSO_DATE, self.TIME_ON,
					  self.STATION_CALLSIGN, self.DATA1, self.CALL, self.DATA2]

			for entry, valor in zip(campos, values):
				entry.delete(0, END)
				entry.insert(0, valor)
			
	def crear_hoja_excel(self):
		"""QSO:  7148 PH 2025-08-09  0752 F4LEC          59  05     IQ4FE         59  05     0"""
		columns = ("FREQ_RX", "MODE","QSO_DATE","TIME_ON","STATION_CALLSIGN","DATA1","CALL","DATA2")
		self.tree = ttk.Treeview(self.parent, columns=columns, show='headings')

		for col in columns:
			self.tree.heading(col, text=col)

		"""
		for row in self.adif_records:
			self.tree.insert("", END, values=row)
		"""
		for row in self.adif_records:
			while len(row) < len(columns):
				row.append("")	
					
		self.tree.pack()
		self.tree.bind("<<TreeviewSelect>>", self.on_select)
		
		self.FREQ_RX = tk.Entry(self.parent)
		self.FREQ_RX.pack()
		
		self.MODE = tk.Entry(self.parent)
		self.MODE.pack()
		
		self.QSO_DATE = tk.Entry(self.parent)
		self.QSO_DATE.pack()
		
		self.TIME_ON= tk.Entry(self.parent)
		self.TIME_ON.pack()
		
		self.STATION_CALLSIGN = tk.Entry(self.parent)
		self.STATION_CALLSIGN.pack()	
				
		self.DATA1 = tk.Entry(self.parent)
		self.DATA1.pack()
		
		self.CALL= tk.Entry(self.parent)
		self.CALL.pack()			
		
		self.DATA2 = tk.Entry(self.parent)
		self.DATA2.pack()	

		btn = tk.Button(self.parent, text="Actualizar Fila", command=self.update_cell)
		btn.pack()

	def cargar_datos(self, nuevos_datos):
		"""Borra la tabla y carga nuevos datos"""
		for item in self.tree.get_children():
			self.tree.delete(item)
		for row in nuevos_datos:
			self.tree.insert("", END, values=row)


class InterfaceGraphique(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Adif to Cabrillo by F4LEC')
        self.resizable(False, False)
        # self.geometry("1000x500")

        self.creeGui()

        # Crear la hoja excel en FrameSup
        self.hoja = HojaExcelApp(self.FrameSup, "")
	
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

    def OpenFile(self):
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
                # Añadimos columnas a la hoja (puedes ajustar las columnas como quieras)
                datos_tabla.append([adif["FREQ"], adif["MODE"],adif["QSO_DATE"], adif["TIME_ON"],adif ["STATION_CALLSIGN"],adif ["RST_SENT"],adif["CALL"],adif["RST_RCVD"]])
                line = self.adif_to_cabrillo_line(adif)
                print(line)

        # Cargamos nuevos datos en la tabla
        self.hoja.cargar_datos(datos_tabla)

    def parse_adif_record(self, record):
        """Recupera datos del ADIF klog crea  KEYs  para cabrillo
        <CALL:6>IU7QCK <QSO_DATE:8>20250809 <TIME_ON:6>080500 <FREQ:6>14.227 <BAND:3>20M <FREQ_RX:6>14.227 <BAND_RX:3>20M <MODE:3>SSB <MY_GRIDSQUARE:8>JN33JU07 <STATION_CALLSIGN:5>F4LEC <CQZ:2>15 <ITUZ:2>28 <DXCC:3>248 <CONT:2>EU <CONTACTED_OP:0> <EQ_CALL:0> <EQSL_QSLSDATE:8>20250809 <EQSL_QSL_SENT:1>Q <LOTW_QSLSDATE:8>20250809 <LOTW_QSL_SENT:1>Q <CLUBLOG_QSO_UPLOAD_DATE:8>20250809 <CLUBLOG_QSO_UPLOAD_STATUS:1>M <OPERATOR:0> <OWNER_CALLSIGN:0> <RST_SENT:2>59 <RST_RCVD:2>59 <TX_PWR:2>50 <EOR>"""

        def get_field(name):
            match = re.search(fr"<{name}:(\d+)>(.*?)($|<)", record)
            return match.group(2).strip() if match else ""
        return {# <RST_SENT:2>59 <RST_RCVD:2>59
            "CALL": get_field("CALL"),
            "QSO_DATE": get_field("QSO_DATE"),
            "TIME_ON": get_field("TIME_ON"),
            "FREQ": get_field("FREQ"),
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
        hora = adif['TIME_ON'][:2] + adif['TIME_ON'][2:4]
        return f"QSO: {freq:5} {modo:2} {fecha}  {hora:4} {adif['STATION_CALLSIGN']:12}   {adif ['RST_SENT']:4}     {adif['CALL']:12} {adif ['RST_RCVD']:4}"

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
