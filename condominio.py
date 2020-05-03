#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programa de gestión de gastos de condominio

# Pendientes:
# 	Panda para importar, exportar a csv y excel
#	arreglar lo de la modificación de datos
#	menu principal 
#		manejo de tablas
#		seleccion de periodo
#		reportes
#		facturacion
#		salir
#	menu secundario
#		arreglar lo de la entrada de comandos

import json
import condo
from condo import *
import fpdf
from fpdf import FPDF
import yagmail

con = None

database='condominio.db3'
table='locales'
period='012020'

with open('condominio.json') as file: views = json.load(file)

def manejoTablas():
	global table,database,period,views
	while True:
		clear()

		if table=='gastos':
			views[table]['sql']="SELECT id, locales_codigo as local, descripcion, precio, cantidad, precio*cantidad as subtotal FROM gastos WHERE mmyyyy='{}'".format(period)
			views[table]['header']+='  PERIODO : {}'.format(period)

		firstRow=True
		for rl in renderTableAuto(views.get(table,{'database':database,'table':table})):
			if firstRow: 
				print(Style.BRIGHT+rl+Style.RESET_ALL)
				firstRow=False
			else:
				print(rl+Style.RESET_ALL)

		tmp=input('>>> {0}N{1}uevo {0}M{1}odificar {0}B{1}orrar {0}S{1}alir > '.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL)).upper()
		#[0:1]
		
		command=tmp.split(' ')
		#print(command)
		opcion=command[0]
		if len(command)>1:
			opPar=int(command[1])
		else:
			opPar=0

		if opcion=='S':
			break
		elif opcion=='N':
			data={}
			data['id']=str(maxId(database,table,'id')+1)
			if insertRow(database,table,data):
				print('[Ok] Nuevo registro ingresado')
				modificarRegistro('id',data['id'],views[table])
			else:
				print('[!] ERROR: No se pudo ingresar el registro')




		elif opcion=='M':
			#print('opPar',opPar)
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
			#id=int(input('<?> Ingrese ID del registro a BORRAR_'))
			if recordExist(database,table,'id',id):
				deleteRow(database,table,'id',id)
				defragmentTable(database,table)
				print('[Ok] Operación exitosa. Registro BORRADO')
			else:
				print('[!] ERROR: Registro no existe')



		else:
			print('[!] Opción no válida. H para ayuda')
		input('Pulse ENTER para continuar...')

	clear()



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
		print('Tablas disponibles :',tmp)
		tmp2=input('[?] Ingrese NOMBRE de la tabla > ')
		if tmp2 in tmp:
			table=tmp2
			manejoTablas()
		else:
			print('[!] ERROR: Valor introducido NO EXISTE')

	if tmp=='2' or tmp=='R':
		if input('Generar reporte? (S/N)').upper()=='S': generarReporte(database,int(input('Inicio?')),int(input('Cantidad?')))
	if tmp=='3' or tmp=='P':
		month=input('Mes [MM] ? ')
		year=input('Año [YYYY] ? ')
		period=month+year
		print('período {}'.format(period))
		input()
	if tmp=='4' or tmp=='I':
		filename=input('[?] Ingrese NOMBRE del archivo a importar > ')
		importCsv(database,table,filename)
	if tmp=='5' or tmp=='E':
		pass
	if tmp=='0' or tmp=='S':
		break


clear()
sys.exit()