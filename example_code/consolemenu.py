def consolemenu(title,params):
	while True:
		i=0
		print(title)
		print('-'*len(title))
		for p in params:
			i+=1
			print(i,'·',p[0])
		print(0,'· salir')
		error=False
		sel=int(input('\n>> '))
		if sel==0:
			pass
		elif sel>i or error==True:
			print('opción errónea')
		else:
			eval(params[sel-1][1])
		break

menu1=[]
menu1.append(['print','print(\'hola mundo\')'])
menu1.append(['input','input(\'entra un número\')'])
menu1.append(['whatever','print(\'cualcosa\')'])
menu1.append(['menu2','consolemenu(\'menu secundario\',menu2)'])

menu2=[]
menu2.append(['print','print(\'hola mundo 2\')'])
menu2.append(['input','input(\'entra una letra\')'])
menu2.append(['whatever','print(\'cualcosa due\')'])


consolemenu('menu principal',menu1)