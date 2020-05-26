#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programa de gestión de gastos de condominio

from condo import *

INIFILE 	=	__name__.replace('_','')+'.json'
DATABASE 	=	'database/condominio.db3'
VERSION 	=	'0.1 alpha'

table 		=	'locales'
period 		=	'012020'

#CONSOLE WIDGETS

def console_menu(title,options,exit_caption='Salir',null_exit=False):
	#	Función:
	# 		Crea un menú por consola de selección simple
	# 	Entradas:
	# 		title: str <- título del menú
	# 		options: list <- contiene pares de opción y comando a ejecutar
	# 		exitOption: str <- nombre que va a tener la opción de salida del menú
	# 		nullExit: bool <- si es true se sale del menú solo pulsando ENTER
	# 	Regresa:
	# 		bool <- TRUE si se seleccionó una opción válida
	res=False
	while True:
		i=0
		print('\n'+title)
		print('-'*len(title))
		for p in options:
			i+=1
			print(i,'·',p[0])
		print(0,'· '+exit_caption)
		error=False
		sel=input('\n» ')
		if sel=='':
			if null_exit:
				sel=0
			else:
				sel=i+1
		try:
			sel=int(sel)
		except:
			sel=-1
			error=True
		if sel==0:
			res=True
		elif sel>i or error==True:
			console_msgbox('error','Valor NO ES VALIDO',True)
		else:
			eval(options[sel-1][1])
		break
	return res

#END OF CONSOLE WIDGETS

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

#DICTIONARY FUNCTIONS

def rm_dict_key(dict_name,dict_key):
	#	Función:
	#		Remueve una clave de un diccionario trabajando directamente sobre el mismo
	if dict_name.get(dict_key,False):
		dict_name.pop(dict_key)

def assign_value_2_dictkey(dict_name,dict_key,value=None): 
	#	Función:
	#		Asigna el valor por defecto a una clave en un diccionario y si no existe la crea
	if dict_name.get(dict_key,None)==None:
		dict_name[dict_key]=value

#END OF DICTIONARY FUNCTIONS

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
		for c in row_get(DATABASE,vt.get('table'),'id',1).keys():
			columns.append(c)
		for c in row_query_get(DATABASE,vt.get('sql')).keys():
			if c not in columns:
				columns.append(c)

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
				assign_value_2_dictkey(vt_c2,'allowedChars','ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')

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

def option_report():
	#	*** SUBRUTINA ***
	#	Función:
	#		Llama a generarReporte()
	global DATABASE,table,table_parameters,period
	if input('Generar reporte? (S/N)').upper()=='S':
		generarReporte(DATABASE,int(input('Inicio?')),int(input('Cantidad?')))

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
	#	Pendiente:
	#		que pida nombre de archivo
	#		formato xlsx
	global DATABASE,table,table_parameters,period
	filename=input('[?] Ingrese NOMBRE del archivo a importar > ')
	importCsv(database,table,filename)

def option_export():
	#	*** SUBRUTINA ***
	#	Función:
	#		Exporta datos de una tabla a un archivo externo
	#		usa tableSelector()
	global DATABASE,table,table_parameters,period
	sel=tableSelector()
	if sel==None:
		console_msgbox('error','Valor NO ES VALIDO',True)
	else:
		table=sel
		if table=='gastos':
			table='gastos_'+period
			table_parameters[table]=table_parameters['gastos'].copy()
			table_parameters[table]['sql']=table_parameters['gastos']['sql'].replace('gastos','gastos_'+period)
			table_parameters[table]['header']=table_parameters['gastos']['header'].format(period[0:2],period[2:])
			table_parameters[table]['table']=table
		filename=input('[?] NOMBRE del archivo a exportar (sin extensión) > ')

		if filename!='': exportCsv(database,table,filename+'.csv')

		if table[0:6]=='gastos':
			table_parameters.pop(table)

#END OF OPTIONS SUBROUTINES

def main():
	global DATABASE,table,period,table_parameters

	try:
		with open(DATABASE+'.json') as file: table_parameters = json.load(file)
	except:
		console_msgbox('alert','archivo Json: <{}> no existe. Se crea plantilla vacía...'.format(DATABASE+'.json'),True)
		# print('ADVERTENCIA: archivo descriptorio {} no existe. Se crea plantilla vacía...'.format(iniFile))
		table_parameters={}

	#viewOld=table_parameters.copy()

	validate_table_parameters()

	while True:
		clear()
		say(
			'KaiKei',
			font="slick",
			align='left'
		)
		dummy='GESTION DE CONDOMINIO ver. {}'.format(VERSION)
		print(dummy)
		print('='*len(dummy))

		menu1=[]
		menu1.append(['Datos','option_tables()'])
		menu1.append(['Tablas',"consoleMenu('Tablas',menu2)"])
		menu1.append(['Período','option_period()'])
		menu1.append(['Reportes','option_report()'])

		menu2=[]
		menu2.append(['Importar','option_import()'])
		menu2.append(['Exportar','option_export'])
		
		if console_menu('Opciones',menu1): break

	clear()

	if console_input('Guardar cambios en Configuración? (s/n)').upper()=='S':
		console_msgbox('alert','GUARDANDO cambios en el archivo Json')
		fic = open(DATABASE+'.json', "w")
		fic.write(json.dumps(table_parameters,indent=4))
		fic.close()


	# if table_parameters==viewOld:
	# 	console_msgbox('ok','SIN cambios en archivo Json')
	# else:
	# 	console_msgbox('alert','GUARDANDO cambios en el archivo Json')
	# 	fic = open(iniFile, "w")
	# 	fic.write(json.dumps(table_parameters,indent=4))
	# 	fic.close()

	console_msgbox('ok','Bye!\n')

if __name__ == '__main__':
	main()
else:
	console_msgbox('error','Este programa no puede ser llamado como módulo\n')
	console_msgbox('ok','Bye!\n')
sys.exit()

