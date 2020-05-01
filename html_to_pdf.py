from weasyprint import HTML
#HTML(string=html_out).write_pdf("report.pdf")

filename='reporte.html'

txt='\
 id                         DESCRIPCION                          PRECIO(Bs)   CANT SUBTOTAL(Bs)  <br>\
------------------------------------------------------------------------------------------------<br>\
   1 PERSONAL ADMINISTRATIVO (1)                                 1,000,000.00  1.0  1,000,000.00 <br>\
   2 PERSONAL DE MANTENIMIENTO (1)                                 600,000.00  1.0    600,000.00 <br>\
   3 CESTATICKETS (1)                                              300,000.00  1.0    300,000.00 <br>\
   4 IVSS PATRONO JULIO 2018 (1)                                   200,000.00  1.0    200,000.00 <br>\
   5 PAGO DE CANTV                                                  50,000.00  1.0     50,000.00 <br>\
   6 HIDROCAPITAL 16/05 AL 16/06/2018                               50,000.00  1.0     50,000.00 <br>\
   7 ADQUISICIÓN MATERIAL DE LIMPIEZA (VARIOS)                     750,000.00  1.0    750,000.00 <br>\
   8 CORPOELEC 16/06 AL 17/07/18                                 1,000,000.00  1.0  1,000,000.00 <br>\
   9 ANTICIPO CUOTA INICIAL TRABAJOS FILTRACIÓN ÁREAS COMUNES    5,000,000.00  1.0  5,000,000.00 <br>\
  10 ANTICIPO ACEITE MINERAL 20W-50 PARA MANT. ASCENSOR (4 LTS)  3,000,000.00  1.0  3,000,000.00 <br>\
  11 MANTENIMIENTO ASCENSORES AGOSTO 2018 (ANTICIPO)               500,000.00  1.0    500,000.00 <br>\
  12 ASEO CUARTO DE BASURA P.B                                     150,000.00  1.0    150,000.00 <br>\
  13 SUPERVISIÓN MANTENIMIENTO NOCTURNO                            200,000.00  1.0    200,000.00 <br>\
  14 RECICLAJE DE CARTUCHO HP 45A  (2 PARTE DE 2)                  350,000.00  1.0    350,000.00 <br>\
------------------------------------------------------------------------------------------------<br>\
                                                                  SUBTOTAL (Bs):   13,150,000.00<br>\
                                                             RESERVA (10%) (Bs):    1,315,000.00<br>\
                                                     -------------------------------------------<br>\
                                                                     TOTAL (Bs):   14,465,000.00<br>\
                                                     -------------------------------------------<br>\
                    ALICUOTA (%):  0.6400                 MONTO x ALICUOTA (Bs):       92,576.00<br>\
                                                SALDO MES(ES) ANTERIOR(ES) (Bs):       32,500.00<br>\
                                                      INTERES DE MORA (1%) (Bs):          325.00<br>\
                                                     -------------------------------------------<br>\
                                                             TOTAL A PAGAR (Bs):      125,401.00<br>'

replaces={'encabezado':'encabezado de prueba','texto':txt}
html_out=''
txt=txt.replace(' ','·')

fic = open(filename, "r")
lines = fic.readlines()
fic.close()

keys=replaces.keys()
for i in range(0,len(lines)):
	for k in keys:
		r='{{'+k+'}}'
		lines[i]=lines[i].replace(r,replaces.get(k))

filename='reporte_new.html'
fic=open(filename,'w')
fic.writelines(lines)
fic.close()

for l in lines:
	html_out+=l


print(html_out)
HTML(string=html_out).write_pdf("reporte.pdf")


