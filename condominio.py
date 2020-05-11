#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programa de gestión de gastos de condominio

from condo import *

iniFile='condominio.json'
database='condominio.db3'
table='locales'
period='012020'
version='0.1 alpha'

def tableSelector():
	global database,views
	flag=False
	tablas=[]
	for t in tableList(database):
		if 'gastos' not in t:
			tablas.append(t)
		else:
			if flag==False:
				flag=True
				tablas.append('gastos')

	print('Tablas disponibles :')
	i=1
	for t in tablas:
		print('{0}{2}{1}) {3}'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL,i,views[t].get('caption',t)))
		i+=1
	tmp=input('>>> Seleccione > ')
	try:
		tmp=int(tmp)-1
		if tmp<0:tmp=None
		res=tablas[tmp]
	except:
		res=None

	return res

def removeDictionaryKey(d,k): #trabaja directamente sobre el diccionario
	if d.get(k,False):
		d.pop(k)

def assignValue2Key(d,k,v=None): #asigna el valor por defecto a una key en un dict sin importar si existe
    if d.get(k,None)==None:
    	d[k]=v

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
	say(
        'GESTION DE CONDOMINIO ver. {}'.format(version),
        space=False,
        font="console",
        colors=["black"],
        background="white",
        align="left"
    )
	#print('GESTION DE CONDOMINIO ver. {}\n'.format(version))
	print('\nMENU')
	print('====')
	print('{0}1) T{1}ablas'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}2) R{1}eportes'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}3) P{1}eríodo [{2}/{3}]'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL,period[0:2],period[2:]))
	print('{0}4) I{1}mportar datos'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}5) E{1}xportar datos'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	print('{0}0) S{1}alir'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL))
	tmp=input('>>> Seleccione > ')[0:1].upper()
	if tmp=='1' or tmp=='T':
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

	if tmp=='0' or tmp=='S':
		break

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


