# Python program to convert 
# text file to pdf file 

import fpdf
from fpdf import FPDF 

# save FPDF() class into 
# a variable pdf 
pdf = FPDF() 

# Add a page 
pdf.add_page() 

# set style and size of font 
# that you want in the pdf 
#pdf.AddFont("FreeMono")
pdf.set_font("Courier", size = 10) 

# open the text file in read mode 
f = open("prueba.txt", "r") 

# insert the texts in pdf 
pdf.image('logo.gif',10,6,30)
for x in f: 
	#pdf.cell(200, 10, txt = x, ln = 1, align = 'c') 
	pdf.cell(0, 4, txt = x, ln = 1, align = 'C', border=0) 


# save the pdf with name .pdf 
pdf.output("mygfg.pdf") 
