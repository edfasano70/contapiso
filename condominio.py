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

with open('condominio.json') as file:
    views = json.load(file)

if input('Generar reporte? (S/N)').upper()=='S': generarReporte(database,int(input('Inicio?')),int(input('Cantidad?')))

input('Presione ENTER para continuar...')

while True:
	clear()
	firstRow=True
	for rl in renderTableAuto(views.get(table,{'database':database,'table':table})):
		if firstRow: 
			print(Style.BRIGHT+rl+Style.RESET_ALL)
			firstRow=False
		else:
			print(rl+Style.RESET_ALL)

	opcion=input('{0}[N]{1}uevo {0}[M]{1}odificar {0}[B]{1}orrar {0}[I]{1}mportar {0}[E]{1}xportar {0}[T]{1}abla e{0}[X]{1}it ?_'.format(Fore.YELLOW+Style.BRIGHT,Style.RESET_ALL)).upper()[0:1]
	if opcion=='X':
		break
	elif opcion=='N':
		data={}
		data['id']=str(maxId(database,table,'id')+1)
		if insertRow(database,table,data):
			print('<Ok> Nuevo registro ingresado')
			modificarRegistro('id',data['id'],views[table])
		else:
			print('<!> No se pudo ingresar el registro')




	elif opcion=='M':
		id=int(input('<?> Ingrese ID del registro a Modificar_'))
		modificarRegistro('id',id,views[table])



	elif opcion=='B':
		id=int(input('<?> Ingrese ID del registro a BORRAR_'))
		if recordExist(database,table,'id',id):
			deleteRow(database,table,'id',id)
			defragmentTable(database,table)
			print('<Ok> Operación exitosa')
		else:
			print('<!> Registro no existe')



	elif opcion=='I': #importar csv
		filename=input('<?> Ingrese NOMBRE del archivo a importar_')
		importCsv(database,table,filename)



	elif opcion=='E': #exportar csv
		pass



	elif opcion=='T':
		tmp=(tableList(database))
		print('Tablas disponibles :',tmp)
		tmp2=input('<?> Ingrese NOMBRE de la tabla_')
		if tmp2 in tmp:
			table=tmp2
		else:
			print('<!> Valor introducido incorrecto')



	else:
		input('<!> Opción no válida.')
	input('Pulse ENTER para continuar...')



clear()
sys.exit()