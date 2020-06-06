#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programa de gestión de gastos de condominio

from condo import *

APP_NAME	=	'Sistema de Gestión Condominial'
APP_ALIAS	=	'Contapiso'
VERSION 	=	'0.2.9 pre-beta'

INIFILE 	=	__name__.replace('_','')+'.json'
DATABASE 	=	'database/condominio.db3'

table 		=	'locales'
period 		=	'012020'

table_parameters={}
table_parameters_initial={}

#APPLICATION SPECIFIC WIDGETS

def table_selector():
	#	Función:
	#		Explora la base de datos, crea menú de selección, devuelve el nombre de la tabla
	#		o Null si la opción entrada no es válida
	global DATABASE,table_parameters
	flag=False
	title='Tablas Disponibles'
	tables=[]
	for t in database_table_list(DATABASE):
		if 'gastos' not in t:
			tables.append(t)
		else:
			if flag==False:
				flag=True
				tables.append('gastos')

	menu_tables=[]
	for t in tables:
		menu_tables.append([table_parameters[t]['caption'],t])

	i=0
	print('\n'+title)
	print('-'*len(title))
	for p in menu_tables:
		i+=1
		print(i,'·',p[0])
	error=False
	sel=input('\n» ')
	if sel=='': sel=0
	try:
		sel=int(sel)
	except:
		sel=0
		error=True
	if sel==0:
		res=None
	elif sel>i or error==True:
		console_msgbox('error','Valor NO ES VALIDO',True)
		res=None
	else:
		res=menu_tables[sel-1][1]
	return res

#END OF APPLICATION SPECIFIC WIDGETS

#APPLICATION SPECIFIC FUNCTIONS

def new_period():
	#	Función:
	#		Crea una copia de la tabla gastos con el nombre gastos_MMYYYY donde MMYYYY es el
	#		período 
	global DATABASE,period
	if 'gastos_'+period not in database_table_list(DATABASE):

		create_gastos_sql="CREATE TABLE gastos{} ( \
		    id             INTEGER        PRIMARY KEY ASC AUTOINCREMENT, \
		    locales_codigo VARCHAR( 10 ),\
		    documento      VARCHAR( 80 ),\
		    descripcion    VARCHAR( 80 ),\
		    precio         REAL           DEFAULT ( 0.0 ),\
		    cantidad       REAL           DEFAULT ( 0.0 ));".format('_'+period)

		con = lite.connect(DATABASE)
		cur = con.cursor()
		cur.execute(create_gastos_sql)
		con.close()
		console_msgbox('alert','Se creó la tabla gastos_'+period)
	else:
		pass
	console_msgbox('ok','Cambio a período {}/{}'.format(period[0:2],period[2:]))

def modify_table_row(id_name,id_value):
	# 	Función:
	# 		Modifica un registro preguntando valores
	# 	Entrada:
	# 		database: str <- nombre de la base de datos
	# 		table: str <- nombre de la tabla
	# 		id_name: str <- nombre de la columna apuntador normalmente 'id'
	# 		id_value: str <- valor a modificar
	# 	Regresa:
	# 		DEBERIA regresar bool - True si se modificó
	global DATABASE,table,table_parameters
	res=True
	if row_id_exist(DATABASE,table,id_name,id_value):
		row=row_get(DATABASE,table,id_name,id_value)
		data={}
		for c in row.keys():
			cStyle=table_parameters[table]['columns'][c]
			while True:
				caption=cStyle.get('caption')
				helper=cStyle.get('helper')

				if row[c]==None or row[c]=='':
					row[c]=cStyle.get('default_value','')
				if cStyle.get('enabled'):
					tmp=input('{} : {} [{}]='.format(caption,helper,row[c]))
				else:
					print('{} : {}'.format(caption,row[c]))
					data[c]=str(row[c])
					break
				if tmp=='': tmp=row[c]
				res, tmp, msg=validateInput(tmp,cStyle)
				if msg!='':print(msg)
				if res:
					data[c]=tmp 
					break
		row_update(DATABASE,table,data)
		console_msgbox('ok','Registro actualizado')
	else:
		console_msgbox('error','El registro id={} NO EXISTE'.format(id_value))
		res=False
	return res

def table_crud_management():
	#	Función:
	#		Implementa las funciones CRUD sobre la tabla 'table' en 'DATABASE'
	global DATABASE,table,period,table_parameters

	terminal_width,terminal_heigth=terminal_size()

	while True:
		clear()
		header=table_parameters[table].get('header','')
		header+='<{} in {}>'.format(table,DATABASE)
		print(header+'\n')

		firstRow=True
		for rl in renderTableAuto(DATABASE,table_parameters[table]):
			if len(rl)>terminal_width:
				rl=rl[0:terminal_width]
			if firstRow: 
				print(Style.BRIGHT+rl+Style.RESET_ALL)
				firstRow=False
			else:
				print(rl+Style.RESET_ALL)

		print('\n'+table_parameters[table].get('footer','FdlT\n'))

		print('» {0}N{1}uevo {0}M{1}odificar {0}B{1}orrar » '.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL),end='')
		tmp=input().upper()
		
		command=tmp.split(' ')
		opcion=command[0]
		if len(command)>1:
			opPar=int(command[1])
		else:
			opPar=0

		if opcion=='':
			break

		elif opcion=='N':
			data={'id':str(table_max_id(DATABASE,table,'id')+1)}
			if row_insert(DATABASE,table,data):
				console_msgbox('ok','Nuevo registro ingresado',False)
				# modify_table_row('id',data['id'],table_parameters[table])
				modify_table_row('id',data['id'])
			else:
				console_msgbox('error','No se pudo ingresar el registro')

		elif opcion=='M':
			if opPar==0:
				id=int(console_input('Ingrese ID del registro a MODIFICAR'))
				# id=int(input('[?]  > '))
			else:
				id=opPar
			modify_table_row('id',id)

		elif opcion=='B':
			if opPar==0:
				id=int(console_input('Ingrese ID del registro a BORRAR'))
				# id=int(input('[?] Ingrese ID del registro a BORRAR > '))
			else:
				id=opPar
			if row_id_exist(DATABASE,table,'id',id):
				row_delete(DATABASE,table,'id',id)
				table_defrag(DATABASE,table)
				console_msgbox('ok','Operación exitosa. Registro id={} BORRADO'.format(id),False)
			else:
				console_msgbox('error','Registro id={} no existe'.format(id),False)

		else:
			console_msgbox('error','Opción NO VALIDA')
		input('Pulse ENTER para continuar...')
	clear()

def validate_table_parameters():
	#	Función:
	#		Valida el dict 'table_parameters' que contiene toda la información de despliegue de las tablas
	#		Ingresa valores por defecto
	#	Pendiente:
	#		Que regrese un bool que sea True si se modificó 'table_parameters'
	global DATABASE,table_parameters
	tmp=(database_table_list(DATABASE))

	console_msgbox('ok','Validando parámetros de Base de Datos')

	if 'gastos' not in tmp:

		create_gastos_sql="CREATE TABLE gastos ( \
		    id             INTEGER        PRIMARY KEY ASC AUTOINCREMENT, \
		    locales_codigo VARCHAR( 10 ),\
		    documento      VARCHAR( 80 ),\
		    descripcion    VARCHAR( 80 ),\
		    precio         REAL           DEFAULT ( 0.0 ),\
		    cantidad       REAL           DEFAULT ( 0.0 ));"

		con = lite.connect(DATABASE)
		cur = con.cursor()
		cur.execute(create_gastos_sql)
		con.close()

		row_insert(database,'gastos',{'id':1})

		tmp.append('gastos')

	tmp2=[]
	for t in tmp:
		if 'gastos_' not in t:
			tmp2.append(t)
	tmp=tmp2 

	for t in tmp:
		assign_value_2_dictkey(table_parameters,t,{})
		vt=table_parameters[t]
		assign_value_2_dictkey(vt,'table',t)
		assign_value_2_dictkey(vt,'caption',t)
		assign_value_2_dictkey(vt,'sql','SELECT * FROM {}'.format(t))
		assign_value_2_dictkey(vt,'header','')
		assign_value_2_dictkey(vt,'footer','')
		assign_value_2_dictkey(vt,'columns',{})

		columns=[]
		# print(vt.get('table'))
		# for c in row_get(DATABASE,vt.get('table'),'id',1).keys():

		row_insert(DATABASE,vt.get('table'),{'id':0}) #evitamos encontrarnos con una tabla vacía

		for c in row_query_get(DATABASE,'SELECT * FROM {} LIMIT 1'.format(vt.get('table'))).keys():
			columns.append(c)
		for c in row_query_get(DATABASE,vt.get('sql')).keys():
			if c not in columns:
				columns.append(c)

		row_delete(DATABASE,vt.get('table'),'id',0) #cancela lo de arriba

		vt_c=vt['columns']

		for c in columns:
			assign_value_2_dictkey(vt_c,c,{'type':'str'})
			vt_c2=vt_c[c]
			assign_value_2_dictkey(vt_c2,'caption',c)
			assign_value_2_dictkey(vt_c2,'helper',c)
			
			if vt_c2['type']=='str':
				assign_value_2_dictkey(vt_c2,'capitalize')
				assign_value_2_dictkey(vt_c2,'lenght_min')
				assign_value_2_dictkey(vt_c2,'lenght_max')
				assign_value_2_dictkey(vt_c2,'allowed_chars','ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')

			elif vt_c2['type']=='int':
				assign_value_2_dictkey(vt_c2,'decimal_places',0)
				assign_value_2_dictkey(vt_c2,'min')
				assign_value_2_dictkey(vt_c2,'max')

			elif vt_c2['type']=='float':
				assign_value_2_dictkey(vt_c2,'decimal_places',2)
				assign_value_2_dictkey(vt_c2,'min')
				assign_value_2_dictkey(vt_c2,'max')

			assign_value_2_dictkey(vt_c2,'visible',True)
			assign_value_2_dictkey(vt_c2,'enabled',True)

def validate_app_parameters():
	#	Función:
	#		Valida el dict 'table_parameters' que contiene toda la información de despliegue de las tablas
	#		Ingresa valores por defecto
	#	Pendiente:
	#		Que regrese un bool que sea True si se modificó 'table_parameters'
	global DATABASE,table,period,app_parameters

	console_msgbox('ok','Validando parámetros de Aplicación')
	assign_value_2_dictkey(app_parameters,'database',DATABASE)
	DATABASE=app_parameters['database']
	# assign_value_2_dictkey(app_parameters,'table',table)
	# table=app_parameters['table']
	assign_value_2_dictkey(app_parameters,'period',period)
	period=app_parameters['period']
	assign_value_2_dictkey(app_parameters,'sender_email','some@gmail.com')
	assign_value_2_dictkey(app_parameters,'sender_password','123456')

def export_table_to_xls(): # <-falta descripcion
	global DATABASE,table,period
	import pandas as pd
	query=query_get(DATABASE,'SELECT * FROM {}'.format(table))
	first_row=True
	data_dict={}
	for q in query:
		if first_row:
			first_row=False
			row_keys=q.keys()
			for r in row_keys:
				assign_value_2_dictkey(data_dict,r,[])
		for r in row_keys:
			data_dict[r].append(q[r])
	data_frame=pd.DataFrame.from_dict(data_dict)
	data_frame.to_excel('xls/{}.xlsx'.format(table), sheet_name=table, index=False)

def import_xls_into_table(): # <- falta descripción
	global DATABASE,table,period
	import pandas as pd
	data_frame=pd.read_excel('xls/{}.xlsx'.format(table))#, sheet_name=table)
	data_frame=data_frame.fillna('')
	data_dict=data_frame.to_dict('records')
	for d in data_dict:
		# print('\nrecord')
		# print(d)
		d.pop('id')
		row_insert(DATABASE,table,d)
	# input()
	table_defrag(DATABASE,table)

def generate_invoice(data,invoice_date='01/01/2020',invoice_number=1,output='console'):
	#output puede ser console, html, pdf
	global DATABASE,period,table_parameters

	#obtenemos el total de gastos
	res=row_query_get(DATABASE,'SELECT SUM(precio*cantidad) as subtotal from gastos_{} WHERE locales_codigo==\'0\' OR locales_codigo==\'\''.format(period))

	subtotal 		=	res['subtotal']
	reserva 		=	subtotal*10/100
	total_gastos	=	subtotal+reserva
	alicuota 		=	data['alicuota']
	saldo 			= 	data['saldo']
	interes_mora	=	saldo/100
	monto_alicuota	=	total_gastos*alicuota/100

	fondo_reserva	=	35000000

	if output=='console' or output=='pdf':
		res=[]

		# res.append('Factura #{}'.format(1))
		# res.append('Local       : {}'.format(data['local']))
		# res.append('Propietario : {}'.format(data['propietario']))
		# if data['propietario']!=data['inquilino']: res.append('Inquilino   : {}'.format(data['inquilino']))

		table_parameters['gastos_'+period]=table_parameters['gastos'].copy()
		table_parameters['gastos_'+period]['sql']='SELECT descripcion, precio, cantidad, precio*cantidad as subtotal FROM {} WHERE locales_codigo==\'0\' or locales_codigo==\'\''.format('gastos_'+period)       #table_parameters['gastos']['sql'].replace('gastos','gastos_'+period)

		report_lines=renderTableAuto(DATABASE,table_parameters['gastos_'+period])
		table_parameters.pop('gastos_'+period)

		max_width=0
		firstRow=True
		for rl in report_lines:
			if len(rl)>max_width: max_width=len(rl)

		report_width_str='{:<'+str(max_width-1)+'}'

		# res.append(report_width_str.format('Factura #{}'.format(1)))
		# res.append(report_width_str.format('Local       : {}'.format(data['local'])))
		# res.append(report_width_str.format('Propietario : {}'.format(data['propietario'])))
		# if data['propietario']!=data['inquilino']: res.append(report_width_str.format('Inquilino   : {}'.format(data['inquilino'])))
		# res.append('')

		for rl in report_lines:
			res.append(rl)

		report_width_str='{:>'+str(max_width-1)+'}'

		separator='-------------------------------------------'
		res.append(report_width_str.format(separator))

		res.append(report_width_str.format('SUBTOTAL (Bs): {:>15,.2f}'.format(subtotal)))
		res.append(report_width_str.format('RESERVA (10%) (Bs): {:>15,.2f}'.format(reserva)))
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

	elif output=='html':
		pass
	else:
		pass

	if output=='console':
		for r in res:
			print(r)
		print()
		console_msgbox('ok','Fin de la Factura',enter=True)

	elif output=='pdf':
		filename=period+'_'+data['codigo']+'.pdf'
		pdf = FPDF() 
		pdf.add_page() 
		pdf.set_font("Courier", size = 10, style='B') 
		# pdf.image('resources/logo.jpg',10,6,30)
		pdf.image('resources/header.jpg',5,0,200)
		pdf.image('resources/footer.jpg',5,270,200)
		for i in range(0,6):
			pdf.cell(0, 3, txt = '', ln = 1, align = 'C', border=0)
		pdf.cell(0,5,txt='Fecha: {}'.format(invoice_date),ln=1,align='R',border=0)
		pdf.set_text_color(255,0,0)
		pdf.cell(0,5,txt='Recibo Nº {}'.format(invoice_number),ln=1,align='R',border=0)
		pdf.set_text_color(0,0,0)
		pdf.cell(0,5,txt='RECIBO DE CONDOMINIO',align='C',ln=1)
		pdf.set_font("Courier", size = 8, style='B')
		pdf.set_fill_color(200,200,200) 
		pdf.cell(40,5,txt='LOCAL',ln=0,align='C',border=1,fill=True) 
		pdf.cell(75,5,txt='PROPIETARIO',ln=0,align='C',border=1,fill=True) 
		pdf.cell(75,5,txt='INQUILINO',ln=1,align='C',border=1,fill=True) 
		pdf.set_font("Courier", size = 8) 
		pdf.cell(40,5,txt=data['local'],ln=0,align='C',border=1) 
		pdf.cell(75,5,txt=data['propietario'],ln=0,align='C',border=1) 
		pdf.cell(75,5,txt=data['inquilino'],ln=1,align='C',border=1)

		pdf.set_font("Courier", size = 8, style='B') 
		pdf.cell(0,3,ln=1)
		pdf.cell(0,5,txt='RELACION DE GASTOS COMUNES DEL MES',ln=1,align='C',border=1,fill=True)
		pdf.cell(0,3,ln=1)
		pdf.set_font("Courier", size = 8) 


		pdf.set_font("Courier",size=7.5)
		for r in res: 
			pdf.cell(0, 3, txt = r, ln = 1, align = 'C', border=0) 

		pdf.cell(0,8,txt='',ln=1,border=0,fill=False)

		pdf.cell(10,5,txt='',ln=0,border=0,fill=False)
		pdf.cell(30,5,txt='',ln=0,border=0,fill=False)
		pdf.cell(35,5,txt='Saldo Anterior (Bs)',ln=0,border=1,fill=True,align='C')
		pdf.cell(35,5,txt='Cargo (Bs)',ln=0,border=1,fill=True,align='C')
		pdf.cell(35,5,txt='Abono (Bs)',ln=0,border=1,fill=True,align='C')
		pdf.cell(35,5,txt='Total (Bs)',ln=1,border=1,fill=True,align='C')

		pdf.cell(10,5,txt='',ln=0,border=0,fill=False)
		pdf.cell(30,5,txt='Fondo de Reserva',ln=0,border=1,fill=True,align='C')
		pdf.cell(35,5,txt='{:>15,.2f}'.format(fondo_reserva),ln=0,border=1,fill=False,align='R')
		pdf.cell(35,5,txt='',ln=0,border=1,fill=False,align='C')
		pdf.cell(35,5,txt='{:>15,.2f}'.format(reserva),ln=0,border=1,fill=False,align='R')
		pdf.cell(35,5,txt='{:>15,.2f}'.format(fondo_reserva+reserva),ln=1,border=1,fill=False,align='R')

		pdf.cell(10,5,txt='',ln=0,border=0,fill=False)
		pdf.cell(30,5,txt='Por cobrar a Ud.',ln=0,border=1,fill=True,align='C')
		pdf.cell(35,5,txt='{:>15,.2f}'.format(saldo),ln=0,border=1,fill=False,align='R')
		pdf.cell(35,5,txt='{:>15,.2f}'.format(monto_alicuota),ln=0,border=1,fill=False,align='R')
		pdf.cell(35,5,txt='',ln=0,border=1,fill=False,align='C')
		pdf.cell(35,5,txt='{:>15,.2f}'.format(saldo+monto_alicuota),ln=1,border=1,fill=False,align='R')

		pdf.output('pdf/'+filename)


	elif output=='html':
		pass
	else:
		pass

def renderTableAuto(database,params):
	#	Función:
	# 		Genera el código para imprimir una tabla
 	#	Entrada:
 	#		params: dict <-contiene todos los parámetros para generar la tabla
	#			table: string <- nombre de la tabla <- no
	#			style: dict <- tiene todos los parámetros que dibujan la tabla
	#	Regresa:
	#		list : con todo el codigo para mostrar la tabla
 	#	Pendiente:
 	#		validar errores
 	#		opción html
	table 	=	params.get('table')
	sql 	=	params.get('sql','SELECT * FROM {}'.format(table))
	rows=query_get(database,sql)
	if rows!=[]:
		data = []
		keys = []
		tmp  = []

		for k in rows[0].keys():
			keys.append(k)
			try:
				tmp.append(params['columns'][k]['caption'])
			except:
				tmp.append(k)

		data.append(tmp)

		for r in rows:
			tmp	= []
			for k in r.values():
				tmp.append(k)
			data.append(tmp)
		for row in data:
			for i in range(0,len(row)):
				if row[i]==None:
					row[i]=''
				if is_number(row[i]): #si la columna es int o float lo convertimos a str formateado
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
		res=''
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
	else:
		output=['La tabla está vacía...\n']

	return(output)

def email_invoice(data):
	sender_email 	= 	'alvafasa@gmail.com'
	receiver_email 	= 	'edmundofasano@gmail.com'
	subject 		= 	"Check THIS out"
	sender_password	=	'Irama2017'

	yag = yagmail.SMTP(user=sender_email, password=sender_password)

	contents = [
	  "This is the first paragraph in our email",
	  "As you can see, we can send a list of strings,",
	  "being this our third one",
	  "mygfg.pdf"
	]
	yag.send(receiver_email, subject, contents)

#END OF APPLICATION SPECIFIC FUNCTIONS

#OPTIONS SUBROUTINES

def option_tables():
	#	*** SUBRUTINA ***
	#	Función:
	#		Llama a tableSelector()
	# 		Llama a table_crud_management() si la opción es válida
	#		Si la tabla es gastos cambia los parámetros a la tabla de gastos del período
	global DATABASE,table,table_parameters,period
	sel=table_selector()
	if sel!=None:
		table=sel
		if table=='gastos':
			table='gastos_'+period
			table_parameters[table]=table_parameters['gastos'].copy()
			table_parameters[table]['sql']=table_parameters['gastos']['sql'].replace('gastos','gastos_'+period)
			table_parameters[table]['header']=table_parameters['gastos']['header'].format(period[0:2],period[2:])
			table_parameters[table]['table']=table
		table_crud_management()
		if table[0:6]=='gastos':
			table_parameters.pop(table)

def option_period():
	#	*** SUBRUTINA ***
	#	Función:
	#		Cambia el período
	global DATABASE,table,table_parameters,period
	month=input('Mes [MM] ? ')[0:2]
	year=input('Año [YYYY] ? ')[0:4]
	period=month+year
	new_period()
	input()

def option_import():
	#	*** SUBRUTINA ***
	#	Función:
	#		Importa datos de archivo externo
	global DATABASE,table,table_parameters,period

	print(Style.BRIGHT+Fore.YELLOW+'\n# Importante!!!'+Style.RESET_ALL)
	print(' El correcto funcionamiento de esta opción depende los sigientes factores:')
	print('→ El archivo a importar debe estar en formato \'xls\' con extensión \'.xlsx\'')
	print('→ El nombre del archivo debe ser el mismo que el nombre de la tabla en la base de datos')
	print('→ Con la excepción de la tabla \'gastos\' que será importada en la tabla del período correspondiente')
	sel=table_selector()
	if sel!=None:
		filename=''
		table=sel
		if table=='gastos':
			table='gastos_'+period
		if console_captcha():
			import_xls_into_table()

def option_export():
	#	*** SUBRUTINA ***
	#	Función:
	#		Exporta datos de una tabla a un archivo externo
	#		usa tableSelector()
	global DATABASE,table,table_parameters,period
	sel=table_selector()
	if sel!=None:
		table=sel
		if table=='gastos':
			table='gastos_'+period
		export_table_to_xls()

def option_table_delete_all_records():
	global DATABASE,table,table_parameters,period
	sel=table_selector()
	if sel!=None:
		if console_captcha():
			table=sel
			if table=='gastos':
				table='gastos_'+period
			table_delete_all_rows(DATABASE,table)

def option_generate_invoices():
	#	*** SUBRUTINA ***
	#	Función:
	#		Genera todas las facturas y las guarda en pdf en la carpeta /pdf
	global DATABASE,table,table_parameters,period
	invoice_number=int(console_input('Número del primer recibo?',default='1'))
	invoice_date=console_input('Fecha a imprimir?',default='01/01/2020')
	res=query_get(DATABASE,'SELECT * FROM locales')
	print('Generando Facturas...')
	total_invoices=int(res[-1]['id'])
	for r in res:
		generate_invoice(r,output='pdf',invoice_number=invoice_number,date=invoice_date)
		console_progressbar(int(r['id']),total_invoices,30)
		break

def option_email_invoices():
	console_msgbox('ok','Opción enviar facturas',enter=True)

#END OF OPTIONS SUBROUTINES

def main():
	global DATABASE,table,period,table_parameters,table_parameters_initial,app_parameters,INIFILE

	#Proceso de INIFILE 
	console_msgbox('ok','Cargando archivo de parámetros de Aplicación')
	try:
		with open(INIFILE) as file: app_parameters = json.load(file)
	except:
		console_msgbox('alert','archivo Json: <{}> no existe. Se crea plantilla vacía...'.format(INIFILE),True)
		app_parameters={}

	app_parameters_initial=app_parameters.copy()

	validate_app_parameters()

	#Proceso de <database>.json
	console_msgbox('ok','Cargando archivo de parámetros de Base de Datos')
	try:
		with open(DATABASE+'.json') as file: table_parameters = json.load(file)
	except:
		console_msgbox('alert','archivo Json: <{}> no existe. Se crea plantilla vacía...'.format(DATABASE+'.json'),True)
		table_parameters={}

	# table_parameters_initial=table_parameters.copy()

	validate_table_parameters()

	while True:
		clear()
		say(
			APP_ALIAS,
			font="slick",
			align='left'
		)
		dummy='{}{} ver. {}{}'.format(Style.BRIGHT,APP_NAME,VERSION,Style.RESET_ALL)
		print(dummy)
		print('-'*len(dummy))

		menu1=[]
		menu1.append(['Manejo de Datos','option_tables()'])
		menu1.append(['Mantenimiento de Tablas',''])
		menu1.append(['Cambio de Período.{} Actual → {}/{}{}'.format(Style.BRIGHT,period[0:2],period[2:],Style.RESET_ALL),'option_period()'])
		menu1.append(['Facturas (Generar y Enviar)',''])

		menu2=[]
		menu2.append(['Importar datos desde hoja de Excel','option_import()'])
		menu2.append(['Exportar datos a hoja de Excel','option_export()'])
		menu2.append(['Vaciar Tabla','option_table_delete_all_records()'])

		menu3=[]
		menu3.append(['Generar Facturas','option_generate_invoices()'])
		menu3.append(['Enviar Facturas por Email','option_email_invoices()'])
		
		option=console_menu('Opciones',menu1,exit_on_null=False)
		if option==0: 
			break
		elif option==-1:
			console_msgbox('error','Opción NO VALIDA',True)
		elif option==2:
			option_2=console_menu('Menú Tablas',menu2)
			if option_2==0 or option_2==-1:
				pass
			else:
				eval(menu2[option_2-1][1])
		elif option==4:
			option_4=console_menu('Menú Facturas',menu3)
			if option_4==0 or option_4==-1:
				pass
			else:
				eval(menu3[option_4-1][1])
		elif option==4:
			option_3=console_menu('Menú Facturas y Envío',menu3)
			if option_3==0 or option_3==-1:
				pass
			else:
				eval(menu3[option_3-1][1])
		else:
			eval(menu1[option-1][1])
	clear()

	# if console_input('Guardar cambios en Configuración? (s/n)').upper()=='S':
	# 	console_msgbox('alert','GUARDANDO cambios en el archivo Json')
	# 	fic = open(DATABASE+'.json', "w")
	# 	fic.write(json.dumps(table_parameters,indent=4))
	# 	fic.close()

	try:
		with open(DATABASE+'.json') as file: table_parameters_initial = json.load(file)
	except:
		console_msgbox('alert','archivo Json: <{}> no existe. Se crea plantilla vacía...'.format(DATABASE+'.json'),True)
		table_parameters_initial={}

	if table_parameters==table_parameters_initial:
		pass
		# console_msgbox('ok','SIN cambios en archivo <database>.Json')
	else:
		console_msgbox('alert','GUARDANDO cambios en el archivo < [database] >.json')
		fic = open(DATABASE+'.json', "w")
		fic.write(json.dumps(table_parameters,indent=4))
		fic.close()
		console_msgbox('alert','GUARDANDO respaldo')
		fic = open('bak/'+DATABASE+'_{}.json'.format(date_time_now()), "w")
		fic.write(json.dumps(table_parameters_initial,indent=4))
		fic.close()

	app_parameters['period']=period

	if app_parameters==app_parameters_initial:
		pass
		# console_msgbox('ok','nada cambió')
	else:
		console_msgbox('alert','ACTUALIZANDO < main.json >')
		fic = open(INIFILE, "w")
		fic.write(json.dumps(app_parameters,indent=4))
		fic.close()
		console_msgbox('alert','GUARDANDO respaldo < main.json.bak >')
		fic = open(INIFILE+'.bak', "w")
		fic.write(json.dumps(app_parameters_initial,indent=4))
		fic.close()		

	console_msgbox('ok','Bye!\n')

# print(console_input('entra algo',default='esto es'))
# sys.exit()


if __name__ == '__main__':
	main()
else:
	console_msgbox('error','Este programa no puede ser llamado como módulo\n')
	console_msgbox('ok','Bye!\n')
sys.exit()

