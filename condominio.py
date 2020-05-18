#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programa de gestión de gastos de condominio

from condo import *

INIFILE='condominio.json'
DATABASE='condominio.db3'
VERSION='0.1 alpha'

iniFile=INIFILE
database=DATABASE
table='locales'
period='012020'

def tableSelector():
	#	Función:
	#		Explora la base de datos, crea menú de selección, devuelve el nombre de la tabla
	#		o Null si la opción entrada no es válida
	global DATABASE,views
	flag=False
	title='Tablas Disponibles'
	tablas=[]
	for t in tableList(DATABASE):
		if 'gastos' not in t:
			tablas.append(t)
		else:
			if flag==False:
				flag=True
				tablas.append('gastos')

	menuTablas=[]
	for t in tablas:
		menuTablas.append([views[t]['caption'],t])

	i=0
	print('\n'+title)
	print('-'*len(title))
	for p in menuTablas:
		i+=1
		print(i,'·',p[0])
	error=False
	sel=input('\n>> ')
	if sel=='': sel=0
	try:
		sel=int(sel)
	except:
		sel=0
		error=True
	if sel==0:
		res=None
	elif sel>i or error==True:
		consoleMsgBox('error','Valor NO ES VALIDO',True)
		res=None
	else:
		res=menuTablas[sel-1][1]
	return res

def removeDictionaryKey(d,k):
	#	Función:
	#		Remueve una clave de un diccionario trabajando directamente sobre el mismo
	if d.get(k,False):
		d.pop(k)

def assignValue2Key(d,k,v=None): 
	#	Función:
	#		Asigna el valor por defecto a una clave en un diccionario y si no existe la crea
	if d.get(k,None)==None:
		d[k]=v

def crearTablaPeriodo():
	#	Función:
	#		Crea una copia de la tabla gastos con el nombre gastos_MMYYYY donde MMYYYY es el
	#		período 
	global DATABASE,period
	if 'gastos_'+period not in tableList(DATABASE):

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
		consoleMsgBox('alert','Se creó la tabla gastos_'+period)
	else:
		pass
	consoleMsgBox('ok','Cambio a período {}/{}'.format(period[0:2],period[2:]))

def manejoTablas():
	global DATABASE,table,period,views
	while True:
		clear()
		header=views[table].get('header','')
		header+='<{} in {}>'.format(table,DATABASE)
		print(header+'\n')

		firstRow=True
		for rl in renderTableAuto(views[table]):
			if firstRow: 
				print(Style.BRIGHT+rl+Style.RESET_ALL)
				firstRow=False
			else:
				print(rl+Style.RESET_ALL)

		print('\n'+views[table].get('footer','EoT\n'))

		tmp=input('>>> {0}N{1}uevo {0}M{1}odificar {0}B{1}orrar {0}S{1}alir > '.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL)).upper()
		
		command=tmp.split(' ')
		opcion=command[0]
		if len(command)>1:
			opPar=int(command[1])
		else:
			opPar=0

		if opcion=='S':
			break

		elif opcion=='N':
			data={'id':str(maxId(DATABASE,table,'id')+1)}
			if insertRow(DATABASE,table,data):
				consoleMsgBox('ok','Nuevo registro ingresado',False)
				# modificarRegistro('id',data['id'],views.get(table,{'database':DATABASE,'table':table}))
				modificarRegistro('id',data['id'],views[table])
			else:
				consoleMsgBox('error','No se pudo ingresar el registro')

		elif opcion=='M':
			if opPar==0:
				id=int(input('[?] Ingrese ID del registro a MODIFICAR > '))
			else:
				id=opPar
			modificarRegistro('id',id,views[table])

		elif opcion=='B':
			if opPar==0:
				id=int(input('[?] Ingrese ID del registro a BORRAR > '))
			else:
				id=opPar
			if recordExist(DATABASE,table,'id',id):
				deleteRow(DATABASE,table,'id',id)
				defragmentTable(DATABASE,table)
				consoleMsgBox('ok','Operación exitosa. Registro id={} BORRADO'.format(id),False)
			else:
				consoleMsgBox('error','Registro id={} no existe'.format(id),False)

		else:
			consoleMsgBox('error','Opción NO VALIDA')
		input('Pulse ENTER para continuar...')
	clear()

def validateViews():
	global database,view
	tmp=(tableList(database))

	if 'gastos' not in tmp:
		create_gastos_sql="CREATE TABLE gastos ( \
		    id             INTEGER        PRIMARY KEY ASC AUTOINCREMENT, \
		    locales_codigo VARCHAR( 10 ),\
		    documento      VARCHAR( 80 ),\
		    descripcion    VARCHAR( 80 ),\
		    precio         REAL           DEFAULT ( 0.0 ),\
		    cantidad       REAL           DEFAULT ( 0.0 ));"

		con = lite.connect(database)
		cur = con.cursor()
		cur.execute(create_gastos_sql)
		con.close()

		insertRow(database,'gastos',{'id':1})

		tmp.append('gastos')

	tmp2=[]
	for t in tmp:
		if 'gastos_' not in t:
			tmp2.append(t)
	tmp=tmp2 

	for t in tmp:
		assignValue2Key(views,t,{})

		vt=views[t]
		assignValue2Key(vt,'database',database)
		assignValue2Key(vt,'table',t)
		assignValue2Key(vt,'caption',t)
		assignValue2Key(vt,'sql','SELECT * FROM {}'.format(t))
		assignValue2Key(vt,'header','')
		assignValue2Key(vt,'footer','')
		assignValue2Key(vt,'columns',{})

		columns=[]
		for c in getRow(vt.get('database'),vt.get('table'),'id',1).keys():
			columns.append(c)
		for c in getRowSql(vt.get('database'),vt.get('sql')).keys():
			if c not in columns:
				columns.append(c)

		vt_c=vt['columns']

		for c in columns:
			assignValue2Key(vt_c,c,{'type':'str'})

			vt_c2=vt_c[c]
			assignValue2Key(vt_c2,'caption',c)
			assignValue2Key(vt_c2,'helper',c)
			
			if vt_c2['type']=='str':
				assignValue2Key(vt_c2,'capitalize')
				assignValue2Key(vt_c2,'lenght_min')
				assignValue2Key(vt_c2,'lenght_max')
				assignValue2Key(vt_c2,'allowedChars','ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')

			elif vt_c2['type']=='int':
				assignValue2Key(vt_c2,'decimal_places',0)
				assignValue2Key(vt_c2,'min')
				assignValue2Key(vt_c2,'max')

			elif vt_c2['type']=='float':
				assignValue2Key(vt_c2,'decimal_places',2)
				assignValue2Key(vt_c2,'min')
				assignValue2Key(vt_c2,'max')

			assignValue2Key(vt_c2,'visible',True)
			assignValue2Key(vt_c2,'enabled',True)

def consoleMenu(title,options,exitOption='Salir',nullExit=False):
	#	Función:
	#		Crea un menú por consola de selección simple
	res=False
	while True:
		i=0
		print('\n'+title)
		print('-'*len(title))
		for p in options:
			i+=1
			print(i,'·',p[0])
		print(0,'· '+exitOption)
		error=False
		sel=input('\n>> ')
		if sel=='':
			if nullExit:
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
			consoleMsgBox('error','Valor NO ES VALIDO',True)
		else:
			eval(options[sel-1][1])
		break
	return res

def opcionTablas():
	global DATABASE,table,views,period
	sel=tableSelector()
	if sel!=None:
	# 	consoleMsgBox('error','Valor NO ES VALIDO',True)
	# else:
		table=sel
		if table=='gastos':
			table='gastos_'+period
			views[table]=views['gastos'].copy()
			views[table]['sql']=views['gastos']['sql'].replace('gastos','gastos_'+period)
			views[table]['header']=views['gastos']['header'].format(period[0:2],period[2:])
			views[table]['table']=table
		manejoTablas()
		if table[0:6]=='gastos':
			views.pop(table)

def opcionReportes():
	global DATABASE,table,views,period
	if input('Generar reporte? (S/N)').upper()=='S': generarReporte(database,int(input('Inicio?')),int(input('Cantidad?')))

def opcionPeriodo():
	global DATABASE,table,views,period
	month=input('Mes [MM] ? ')[0:2]
	year=input('Año [YYYY] ? ')[0:4]
	period=month+year
	crearTablaPeriodo()
	input()

def opcionImportar():
	global DATABASE,table,views,period
	filename=input('[?] Ingrese NOMBRE del archivo a importar > ')
	importCsv(database,table,filename)

def opcionExportar():
	global DATABASE,table,views,period
	sel=tableSelector()
	if sel==None:
		consoleMsgBox('error','Valor NO ES VALIDO',True)
	else:
		table=sel
		if table=='gastos':
			table='gastos_'+period
			views[table]=views['gastos'].copy()
			views[table]['sql']=views['gastos']['sql'].replace('gastos','gastos_'+period)
			views[table]['header']=views['gastos']['header'].format(period[0:2],period[2:])
			views[table]['table']=table
		filename=input('[?] NOMBRE del archivo a exportar (sin extensión) > ')

		if filename!='': exportCsv(database,table,filename+'.csv')

		if table[0:6]=='gastos':
			views.pop(table)

try:
	with open(iniFile) as file: views = json.load(file)
except:
	print('ADVERTENCIA: archivo descriptorio {} no existe. Se crea plantilla vacía...'.format(iniFile))
	views={}

viewOld=views.copy()

validateViews()

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
	menu1.append(['Datos','opcionTablas()'])
	menu1.append(['Tablas',"consoleMenu('Tablas',menu2)"])
	menu1.append(['Período','opcionPeriodo()'])
	menu1.append(['Reportes','opcionReportes()'])

	menu2=[]
	menu2.append(['Importar','opcionImportar()'])
	menu2.append(['Exportar','opcionExportar'])
	
	if consoleMenu('Opciones',menu1): break

clear()

if views==viewOld:
	consoleMsgBox('ok','SIN cambios en archivo Json')
else:
	consoleMsgBox('alert','GUARDANDO cambios en el archivo Json')
	fic = open(iniFile, "w")
	fic.write(json.dumps(views,indent=4))
	fic.close()

print('bye!\n')

sys.exit()


