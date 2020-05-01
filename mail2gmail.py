import yagmail

sender_email = 'alvafasa@gmail.com'
receiver_email = 'edmundofasano@gmail.com'
subject = "Check THIS out"
#sender_password = input(f'Please, enter the password for {sender_email}:n')
sender_password='Irama2017'

yag = yagmail.SMTP(user=sender_email, password=sender_password)

contents = [
  "This is the first paragraph in our email",
  "As you can see, we can send a list of strings,",
  "being this our third one",
  "mygfg.pdf"
]

yag.send(receiver_email, subject, contents)