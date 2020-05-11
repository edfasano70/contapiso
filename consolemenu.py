def consolemenu(params):
	i=0
	for p in params:
		i+=1
		print(i,'·',p[0])
	print(0,'· salir')
	while True:
		error=False
		sel=int(input())
		if sel==0:
			break
		elif sel>i or error==True:
			print('opción errónea')
		else:
			eval(params[sel-1][1])


menu1=[]
menu1.append(['print','print(\'hola mundo\')'])
menu1.append(['input','input(\'entra un número\')'])
menu1.append(['whatever','print(\'cualcosa\')'])
menu1.append(['menu2','consolemenu(menu2)'])

menu2=[]
menu2.append(['print','print(\'hola mundo 2\')'])
menu2.append(['input','input(\'entra una letra\')'])
menu2.append(['whatever','print(\'cualcosa due\')'])


consolemenu(menu1)