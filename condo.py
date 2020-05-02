# modulo de rutinas del programa condominio

import sqlite3 as lite
import sys
import os
import colorama
from colorama import *
colorama.init(autoreset=True)

def clear():
#
# Descripción: Borra la consola
#
    import os
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def isNumber(s):
#
# Descripción: Devuelve True si s es del object tipo int o float
# Entrada:
#	s 		- 	valor a checkear
# Regresa:
#	bool	-	True si s es int o float
#
	res=False
	if type(s)==type(1):
		res=True
	elif type(s)==type(1.0):
		res=True
	return res

def dict_factory(cursor, row):
#
# Descripción: Función necesaria para que fetch en la base de datos devuelva dict
# Entrada:
#	cursor 	- 	apuntador del resultado
#	row 	- 	datos regresados
# Regresa:
#	dict	-	con los resultados
#
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def generarReporte(database,inicio,cantidad,output='console',input_file='',output_file=''):
	#output puede ser console, html, pdf
	#obtenemos el total de gastos
	con = lite.connect(database)
	with con:
		cur = con.cursor()
		cur.execute('SELECT SUM(precio*cantidad) FROM gastos')
		res=cur.fetchone()
		if res[0]==None:
			res=[0]
	if con: con.close()
	subtotal=res[0]
	reserva=subtotal*10/100
	total_gastos=subtotal+reserva

	#acá obtenemos alícuota y saldo
	for i in range(inicio,inicio+cantidad):
		con = lite.connect(database)
		with con:
			cur = con.cursor()
			cur.execute('SELECT alicuota, saldo, local, propietario, inquilino FROM locales WHERE id = {}'.format(i))
			res=cur.fetchone()
		if con: con.close()
		alicuota,saldo,local,propietario,inquilino=res[0:5]#,res[1],res[2],res[3],res[4]
		interes_mora=saldo*1/100
		monto_alicuota=alicuota*total_gastos/100
		if output=='console' or output=='pdf':
				res=[]

				res.append('Reporte #{}'.format(i))
				res.append('Local       : {}'.format(local))
				res.append('Propietario : {}'.format(propietario))
				if propietario!=inquilino: res.append('Inquilino   : {}'.format(inquilino))

				report_lines=renderTableAuto(database,'gastos',params)

				max_width=0
				firstRow=True
				for rl in report_lines:
					res.append(rl)
					if len(rl)>max_width: max_width=len(rl)

				report_width_str='{:>'+str(max_width-1)+'}'

				res.append(report_width_str.format('SUBTOTAL (Bs): {:>15,.2f}'.format(subtotal)))
				res.append(report_width_str.format('RESERVA (10%) (Bs): {:>15,.2f}'.format(reserva)))
				separator='-------------------------------------------'
				res.append(report_width_str.format(separator))

				res.append(report_width_str.format('TOTAL (Bs): {:>15,.2f}'.format(total_gastos)))
				res.append(report_width_str.format(separator))

				res.append(report_width_str.format('{:>25}{:>55}'.format('ALICUOTA (%): {:>7,.4f}'.format(alicuota),'MONTO x ALICUOTA (Bs): {:>15,.2f}'.format(monto_alicuota))))
				tmp1='SALDO MES(ES) ANTERIOR(ES) (Bs): {:>15,.2f}'.format(saldo)
				res.append(report_width_str.format(tmp1))
				tmp1='INTERES DE MORA (1%) (Bs): {:>15,.2f}'.format(interes_mora)
				res.append(report_width_str.format(tmp1))
				total_a_pagar=monto_alicuota+saldo+interes_mora
				res.append(report_width_str.format(separator))
				tmp1='TOTAL A PAGAR (Bs): {:>15,.2f}'.format(total_a_pagar)
				res.append(report_width_str.format(tmp1))

				for r in res:
					print(r)

				if input('Desea generar PDF?').upper()=='S':
					pdf = FPDF() 
					pdf.add_page() 
					pdf.set_font("Courier", size = 8) 
					pdf.image('logo.jpg',10,6,30)
					for r in res: 
						pdf.cell(0, 4, txt = r, ln = 1, align = 'C', border=0) 
					pdf.output("mygfg.pdf")

					if input('Desea enviar vía email?').upper()=='S':
						sender_email = 'alvafasa@gmail.com'
						receiver_email = 'edmundofasano@gmail.com'
						subject = "Check THIS out"
						sender_password='Irama2017'

						yag = yagmail.SMTP(user=sender_email, password=sender_password)

						contents = [
						  "This is the first paragraph in our email",
						  "As you can see, we can send a list of strings,",
						  "being this our third one",
						  "mygfg.pdf"
						]

						yag.send(receiver_email, subject, contents)

		elif output=='html':
			pass
		elif output=='pdf':
			pass
		else:
			pass


def renderTableAuto(params):
#
# Descripción: Genera el código para imprimir una tabla
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	style    - dict   - tiene todos los parámetros que dibujan la tabla
#	output	 - string - puede ser console, str, html
# Regresa:
#	string	-	con todo el codigo para mostrar la tabla
# Pendiente:
# 	opción html
# 	eliminar la versión vieja
#
	database=params.get('database')
	table=params.get('table')
	header=params.get('header','DUMMY header')
	footer=params.get('footer','DUMMY footer')
	sql=params.get('sql','SELECT * FROM {}'.format(table))

	con = lite.connect(database)
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute(sql)
	rows=cur.fetchall()
	cur.close()

	#convertimos el resultado en una matriz
	rows = list(rows)
	data = []
	keys = []
	tmp2=[]

	for k in rows[0].keys():
		keys.append(k)
		try:
			tmp2.append(params['columns'][k]['caption'])
		except:
			tmp2.append(k)

	#data.append(tmp)
	data.append(tmp2)

	for r in rows:
		tmp	= []
		for k in r.values():
			tmp.append(k)
		data.append(tmp)
	for row in data:
		for i in range(0,len(row)):
			if row[i]==None:
				row[i]=''
			if isNumber(row[i]): #si la columna es int o float lo convertimos a str formateado
				try:
					tmp=params['columns'][keys[i]]['decimal_places']    #style['decimalplaces'][i]
				except:
					tmp=2
				#print(keys[i],tmp)
				tmp='>{:,.'+str(tmp)+'f}'
				row[i]=tmp.format(row[i])
	#acá se obtiene el ancho máximo de las columnas
	colWidth=[]
	firstRow=True
	for row in data:
		if firstRow:
			firstRow=False
			for i in range(0,len(row)):
				colWidth.append(len(row[i]))
		else:
			for i in range(0,len(row)):
				if len(row[i])>colWidth[i]:
					colWidth[i]=len(row[i])
	#a continuación ponemos todas las celdas al máximo de ancho
	firstRow=True
	for row in data:
		if firstRow:
			firstRow=False
			for i in range(0,len(row)):
				tmp='{:^'+str(colWidth[i])+'}'
				row[i]=tmp.format(row[i])
		else:
			for i in range(0,len(row)):
				if row[i][0:1]!='>':
					row[i]=row[i]+colWidth[i]*' '
					row[i]=row[i][0:colWidth[i]]
				else:
					row[i]=colWidth[i]*' '+row[i][1:]
					row[i]=row[i][colWidth[i]*(-1):]
	max_width=0
	t2=''
	res=header+'\n'
	firstRow=True
	output=[]
	for row in data:
		t2=''
		res=''
		res+=t2+' '
		for r in row:
			res += r+' '
		output.append(res)
		if len(res)>max_width: max_width=len(res)
	output.insert(1,'-'*(max_width-1))
	output.insert(0,params.get('header','{} in {}'.format(table,database)))
	output.insert(1,' '*(max_width-1))

	output.append(' '*(max_width-1))
	output.append(params.get('footer','EoT\n'))
	
	return(output)


def showTable(database,table,style):
#
# Descripción: Muestra una tabla por consola
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	style    - dict   - tiene todos los parámetros que dibujan la tabla
# Regresa:
#	nada
#
	style_h=style.get('header',{})
	style_d=style.get('data',{})
	sql=style.get('sql','SELECT * FROM {}'.format(table))
	#print(sql)
	style_title=Fore.BLACK+Back.CYAN+Style.BRIGHT
	style_bold=Style.BRIGHT
	con = lite.connect(database)
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute(sql)
	printHeader=True
	lines=1
	while True:
		row = cur.fetchone()
		if row == None:
			break
		row = dict(zip(row.keys(),row))
		if printHeader:
			printHeader=False
			keys=row.keys()
			tmp=[]
			for k in keys:
				tmp.append(k)
			keys=tmp
			print('TABLA: {}{}\n'.format(style_bold,table.upper()))
			header=('{}'.format(style_title))
			for i in range(0,len(keys)):
				header+=style_h.get(keys[i],'{} ').format(keys[i])
			print(header)
		values=row.values()
		tmp=[]
		for v in values:
			if v==None:
				tmp.append('None')
			else:
				tmp.append(v)
		values=tmp
		if style.get('zebra',False)==True and lines%2==0:
			line=Back.WHITE+Fore.BLACK
		else:
			line=Fore.WHITE+Back.BLACK
		lines+=1
		for i in range(0,len(values)):
			line+=style_d.get(keys[i],'{} ').format(values[i])
		print(line)
	con.close()

def getRow(database,table,id_name,id_value):
#
# Descripción: Obtiene una línea de datos de una base de datos SQLite
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	id_name  - string - nombre de la columna de apuntador normalmente 'id'
#	id_value - string - valor a buscar
# Regresa:
#	dict - valores retornados
#
	con = lite.connect(database)
	con.row_factory = lite.Row #
	with con:
		cur = con.cursor()
		cur.execute('SELECT * FROM {0} WHERE {1} = {2}'.format(table,id_name,id_value))
		row = cur.fetchone()
		row=dict(zip(row.keys(), row)) #
	if con: con.close()
	return row

def getTable(database,table):
#
# Descripción: Obtiene todos los datos de una base de datos SQLite
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
# Regresa:
#	list - valores retornados DEBERIA ser dict
#
	con = lite.connect(database)
	cur = con.cursor()
	res=sql='SELECT * FROM {0}'.format(table)
	cur.execute(sql)
	rows = cur.fetchall()
	if con: con.close()
	return rows

def tableList(database):
#
# Descripción: Obtiene una línea de datos de una base de datos SQLite
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	id_name  - string - nombre de la columna de apuntador normalmente 'id'
#	id_value - string - valor a buscar
# Regresa:
#	tuple - valores retornados
#
	con = lite.connect(database)
	#con.row_factory = lite.Row #
	cur = con.cursor()
	cur.execute("select name from sqlite_master where type='table' and name!='sqlite_sequence'")
	res=[]
	while True:
		row = cur.fetchone()
		if row == None:
			break
		res.append(row[0])
	if con: con.close()
	return res

def insertRow(database,table,data):
#
# Descripción: Inserta una línea de datos de una base de datos SQLite
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	data     - dict   - datos en forma de pares key-value
# Regresa:
#	bool - True si se ingresó el dato correctamente
#
	res = True
	keys=data.keys()
	tmp=''
	for k in keys:
		tmp+=k+','
	keys=tmp[0:len(tmp)-1]
	tmp=''
	values=data.values()
	for v in values:
		tmp+="'"+str(v)+"',"
	data=tmp[0:len(tmp)-1]
	con = lite.connect(database)
	with con:
		cur = con.cursor()
		try:
			sql='INSERT INTO {} ({}) VALUES ({})'.format(table,keys,data)
			cur.execute(sql)
			con.commit()
		except:
		 	res = False
	if con: con.close()
	return res

def changeRowId(database,table,old_id,new_id): #REVISAR
#
# Descripción: cambia el id  a una línea de datos de una base de datos SQLite
# Entrada:
# 	database - string - nombre de la base de datos
# 	table    - string - nombre de la tabla
# 	old_id	 - integer- id a cambiar
# 	new_id	 - integer- id nuevo
# Regresa:
# 	bool - True si se ingresó el dato correctamente OJO::: hay que revisar
#
	res = True
	con = lite.connect(database)
	with con:
		cur = con.cursor()
		sql="UPDATE {} SET id={} WHERE id={}".format(table,new_id,old_id)
		try:
			#print(sql)
			cur.execute(sql)
		except:
		 	res = False
	if con: con.close()
	return res

def updateRow(database,table,data): #REVISAR
#
# Descripción: cambia el id  a una línea de datos de una base de datos SQLite
# Entrada:
# 	database - string - nombre de la base de datos
# 	table    - string - nombre de la tabla
# 	old_id	 - integer- id a cambiar
# 	new_id	 - integer- id nuevo
# Regresa:
# 	bool - True si se ingresó el dato correctamente OJO::: hay que revisar
#
	res = True
	keys=data.keys()
	subs=''
	for k in keys:
		subs+="{} = '{}',".format(k,data[k])
	subs=subs[0:len(subs)-1]
	con = lite.connect(database)
	sql="UPDATE {} SET {} WHERE id='{}'".format(table,subs,data['id'])
	with con:
		cur = con.cursor()
		try:
			cur.execute(sql)
			con.commit()
		except:
		 	res = False
	if con: con.close()
	return res

def deleteRow(database,table,id_name,id_value):
#
# Descripción: Borra una línea de datos de una base de datos SQLite
# Entrada:
# 	database - string - nombre de la base de datos
# 	table    - string - nombre de la tabla
# 	id_name  - string - nombre de la columna de apuntador normalmente 'id'
# 	id_value - string - valor a buscar
# Regresa:
# 	bool - True si se ingresó el dato correctamente
#
	con = lite.connect(database)
	cur = con.cursor()
	cur.execute('DELETE FROM {} WHERE {} = {}'.format(table,id_name,id_value))
	con.commit()
	con.close()

def maxId(database,table,id_name):
#
# Descripción: Devuelve el máximo valor de la columna en una base de datos SQLite
# Notas: sólo funciona para valores enteros
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	id_name  - string - nombre de la columna de apuntador normalmente 'id'
# Regresa:
#	int - valor máximo
#
	con = lite.connect(database)
	with con:
		cur = con.cursor()
		cur.execute('SELECT MAX({}) FROM {}'.format(id_name,table))
		res=cur.fetchone()
		if res[0]==None:
			res=[0]
	if con: con.close()
	return int(res[0])

def recordExist(database,table,id_name,id_value):
#
# Descripción: Verifica que un registro exista en una base de datos SQLite
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
#	id_name  - string - nombre de la columna de apuntador normalmente 'id'
#	id_value - string - valor a buscar
# Regresa:
#	bool - True si existe
#
	res=False
	con = lite.connect(database)
	with con:
		cur = con.cursor()
		cur.execute('select count(id) from {} where {} = {}'.format(table,id_name,id_value))
		if cur.fetchone()[0]>0:
			res=True
	if con: con.close()
	return res

def defragmentTable(database,table):
#
# Descripción: Obtiene todos los datos de una base de datos SQLite
# Entrada:
#	database - string - nombre de la base de datos
#	table    - string - nombre de la tabla
# Regresa:
#	list - valores retornados DEBERIA ser dict
#
	con = lite.connect(database)
	cur = con.cursor()
	sql='SELECT id FROM {}'.format(table)
	cur.execute(sql)
	rows = cur.fetchall()
	if con: con.close()
	i=1
	for r in rows:
		#print(r[0])
		if r[0]!=i:
			changeRowId(database,table,r[0],i)
		i+=1
	return rows

def insertEmptyRow(database,table,id):
	pass

def exportCsv(database,table,filename):
#
# Descripción: exporta una tabla especificada a  un archivo delimitado por comas CSV
# Entrada:
# 	database - string - nombre de la base de datos
# 	table    - string - nombre de la tabla
# 	filename - string - nombre del archivo a importar
# Regresa:
# 	DEBERIA regresar bool - True si se cargó sin problemas el archivo
# Pendientes:
#	validar si el archivo existe, número de registros cargados, etc
#
	fic = open(filename, "w")
	fic.close()

def importCsv(database,table,filename):
#
# Descripción: importa un archivo delimitado por comas CSV a la base de datos y tabla especificada
# Entrada:
# 	database - string - nombre de la base de datos
# 	table    - string - nombre de la tabla
# 	filename - string - nombre del archivo a importar
# Regresa:
# 	DEBERIA regresar bool - True si se cargó sin problemas el archivo
# Pendientes:
#	validar si el archivo existe, número de registros cargados, etc
#
	fic = open(filename, "r")
	lines = fic.readlines()
	fic.close()
	headerFlag=True
	for line in lines:
		line=line.replace('\'','').replace('\n','')#.split(',')
		if headerFlag:
			headerFlag=False
			keys=[]
			for l in line.split(','):
				keys.append(l)
		else:
			values=line.split(',')
			data={}
			for i in range(0,len(keys)):
				data[keys[i]]=values[i]
			if recordExist(database,table,data['id']):
				data['id']=str(maxId(database,table)+1)
			print(data)
			insertRow(database,table,data)

def modificarRegistro(id_name,id_value,style):
#
# Descripción: modifica un registro preguntando valores
# Entrada:
# 	database - string - nombre de la base de datos
# 	table    - string - nombre de la tabla
# 	id_name  - string - nombre de la columna apuntador normalmente 'id'
#	id_value - string - valor a modificar
# Regresa:
# 	DEBERIA regresar bool - True si se modificó
#
	database=style['database']
	table=style['table']

	if recordExist(database,table,id_name,id_value):
		row=getRow(database,table,id_name,id_value)
		data={}
		for c in row.keys():
			try:
				cStyle=style['columns'][c]
			except:
				cStyle={'type':'str'}
			while True:
				try:
					caption=cStyle['caption']
				except:
					caption=c
				helper=cStyle.get('helper','')

				if cStyle.get('enabled',True):
					tmp=input('{} : {} [{}]='.format(caption,helper,row[c]))
				else:
					print('{} :{}'.format(caption,row[c]))
					data[c]=str(row[c])
					break
				if tmp=='' or tmp==row[c]:
					data[c]=str(row[c])
					break
				else:
					res,tmp=validateInput(tmp,cStyle)
					if res:
						data[c]=tmp 
						break



		updateRow(database,table,data)
		print('<Ok> Registro actualizado')
	else:
		print('<!> Registro no existe')

def validateInput(value,params={'type':'str'}):
	res=True
	type=params['type']
	if type=='str':
		pass
	elif type=='int':
		pass
	elif type=='float':
		pass
	elif type=='date':
		pass
	elif type=='bool':
		pass
	elif type=='email':
		pass
	else:
		pass

	return res, value

