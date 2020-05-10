#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programa de gestión de gastos de condominio

from condo import *

iniFile='condominio.json'
database='condominio.db3'
table='locales'
period='012020'

def crearTablaPeriodo():
	global database,period
	if 'gastos_'+period not in tableList(database):

		create_gastos_sql="CREATE TABLE gastos{} ( \
		    id             INTEGER        PRIMARY KEY ASC AUTOINCREMENT, \
		    locales_codigo VARCHAR( 10 ),\
		    documento      VARCHAR( 80 ),\
		    descripcion    VARCHAR( 80 ),\
		    precio         REAL           DEFAULT ( 0.0 ),\
		    cantidad       REAL           DEFAULT ( 0.0 ));".format('_'+period)

		con = lite.connect(database)
		cur = con.cursor()
		cur.execute(create_gastos_sql)
		con.close()
		consoleMsgBox('alert','Se creó la tabla gastos_'+period)
	else:
		pass
	consoleMsgBox('ok','Cambio a período {}/{}'.format(period[0:2],period[2:]))

def manejoTablas():
	global database,table,period,views
	while True:
		clear()

		header=views[table].get('header','')
		header+='<{} in {}>'.format(table,database)
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
			print(database,table)
			input()
			data={'id':str(maxId(database,table,'id')+1)}
			if insertRow(database,table,data):
				consoleMsgBox('ok','Nuevo registro ingresado',False)
				modificarRegistro('id',data['id'],views.get(table,{'database':database,'table':table}))
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
			if recordExist(database,table,'id',id):
				deleteRow(database,table,'id',id)
				defragmentTable(database,table)
				consoleMsgBox('ok','Operación exitosa. Registro id={} BORRADO'.format(id),False)
			else:
				consoleMsgBox('error','Registro id={} no existe'.format(id),False)


		else:
			print('[!] Opción no válida. H para ayuda')
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

		if views.get(t,False)==False:
			views[t]={}

		views[t]['database']=views[t].get('database',database)
		views[t]['table']=views[t].get('table',t)
		views[t]['caption']=views[t].get('caption',t)
		views[t]['sql']=views[t].get('sql','SELECT * FROM {}'.format(t))
		views[t]['header']=views[t].get('header','')
		views[t]['footer']=views[t].get('footer','')
		views[t]['columns']=views[t].get('columns',{})

		columns=[]
		for c in getRow(views[t]['database'],views[t]['table'],'id',1).keys():
			columns.append(c)
		for c in getRowSql(views[t]['database'],views[t]['sql']).keys():
			if c not in columns:
				columns.append(c)
		for c in columns:
			if views[t]['columns'].get(c,False)==False:
				views[t]['columns'][c]={"type":"str"}

			views[t]['columns'][c]['caption']=views[t]['columns'][c].get('caption',c)
			views[t]['columns'][c]['helper']=views[t]['columns'][c].get('helper',c)
			
			if views[t]['columns'][c].get('type','str')=='str':
				views[t]['columns'][c]['capitalize']=views[t]['columns'][c].get('capitalize',None)
				views[t]['columns'][c]['lenght_min']=views[t]['columns'][c].get('lenght_min',None)
				views[t]['columns'][c]['lenght_max']=views[t]['columns'][c].get('lenght_max',None)
				views[t]['columns'][c]['allowedChars']=views[t]['columns'][c].get('allowedChars','ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')

			if views[t]['columns'][c].get('type','str')=='int':
				views[t]['columns'][c]['decimal_places']=0
				views[t]['columns'][c]['min']=views[t]['columns'][c].get('min',None)
				views[t]['columns'][c]['max']=views[t]['columns'][c].get('max',None)

			if views[t]['columns'][c].get('type','str')=='float':
				views[t]['columns'][c]['decimal_places']=2
				views[t]['columns'][c]['min']=views[t]['columns'][c].get('min',None)
				views[t]['columns'][c]['max']=views[t]['columns'][c].get('max',None)

			views[t]['columns'][c]['visible']=views[t]['columns'][c].get('visible',True)
			views[t]['columns'][c]['enabled']=views[t]['columns'][c].get('enabled',True)

try:
	with open(iniFile) as file: views = json.load(file)
except:
	print('ADVERTENCIA: archivo descriptorio {} no existe. Se crea plantilla vacía...'.format(iniFile))
	views={}

validateViews()

while True:
	clear()
	print('MENU')
	print('====')
	print('{0}1) T{1}ablas'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}2) R{1}eportes'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}3) P{1}eríodo [{2}/{3}]'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL,period[0:2],period[2:]))
	print('{0}4) I{1}mportar datos'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}5) E{1}xportar datos'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}0) S{1}alir'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	tmp=input('>>> Seleccione > ')[0:1].upper()
	if tmp=='1' or tmp=='T':
		tmp=(tableList(database))
		tmp2=[]
		for t in tmp:
			if 'gastos_' not in t:
				tmp2.append(t)
		tmp=tmp2

		print('Tablas disponibles :')
		i=1
		for t in tmp:
			tmp2=views[t]['caption']
			print('{0}{2}{1}) {3}'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL,i,tmp2))
			i+=1
		tmp2=input('>>> Seleccione > ')[0:1].upper()
		errorFlag=False
		try:
			tmp2=int(tmp2)-1
			table=tmp[tmp2]
		except:
			errorFlag=True
		if errorFlag:	
		 	consoleMsgBox('error','Valor introducido NO EXISTE',True)
		else:
			if table=='gastos':
				table='gastos_'+period
				views[table]=views['gastos']
				views[table]['sql']=views['gastos']['sql'].replace('gastos','gastos_'+period)
				views[table]['header']=views['gastos']['header'].format(period[0:2],period[2:])
				views[table]['table']=table
			manejoTablas()
			if table[0:6]=='gastos':
				views.pop(table)

	if tmp=='2' or tmp=='R':
		if input('Generar reporte? (S/N)').upper()=='S': generarReporte(database,int(input('Inicio?')),int(input('Cantidad?')))
	if tmp=='3' or tmp=='P':
		month=input('Mes [MM] ? ')[0:2]
		year=input('Año [YYYY] ? ')[0:4]
		period=month+year
		crearTablaPeriodo()
		input()
	if tmp=='4' or tmp=='I':
		filename=input('[?] Ingrese NOMBRE del archivo a importar > ')
		importCsv(database,table,filename)
	if tmp=='5' or tmp=='E':
		pass
	if tmp=='0' or tmp=='S':
		break


clear()

fic = open(iniFile, "w")
fic.write(json.dumps(views,indent=4))
fic.close()

sys.exit()