#!/usr/bin/python3

import base64
from socket import *
import re
import hashlib
from base64 import b64encode, decode
from base64 import b64decode
import binascii
import struct 
import urllib.request
import urllib.parse
import threading
import datetime
import sys
import struct
import array
import time
from threading import Thread
import os
import time
import struct
import select
import hashlib
import base64
from sys import *
from multiprocessing import Process, current_process

class yinkana():

	#Metodo cogido de las pistas para el reto 5 del GitHub de David Villa. Calcula el cheksum del header que le pasamos.
	def cksum(self,pkt):
		if len(pkt) % 2 == 1:
			pkt += b'\0'
		s = sum(array.array('H', pkt))
		s = (s >> 16) + (s & 0xffff)
		s += s >> 16
		s = ~s
		if sys.byteorder == 'little':
			s=((s>>8) & 0xff) | s<<8

		return s & 0xffff
	

	#Metodo auxiliar al que le pasamos un mensaje, y que utilizo para ->
	#1. Imprimir con el bucle for el enunciado bien splitteado.
	#2. Separar bien la clave para pasársela al reto siguiente.
	#En todos los retos se obtiene el mismo "formato" de enunciado, por lo que podemos utilizar el método para todos los retos.
	def auxiliarKeys(self,msg):
		for i in msg.decode().split("\n"):
			print(i)
		key_to_reto=msg.decode().split('\n')[0]
		key=key_to_reto.split(':')[1]
		return key



	#Reto 0: Identificarse en the-hub
	def reto0(self):

		sock=socket(AF_INET,SOCK_STREAM)
		server=('rick',2000)
		sock.connect(server)
		msg=sock.recv(1024)
		for i in msg.decode().split("\n"):
			print(i)

		#Mandamos identificador codificado.
		sock.send("jovial_rubin".encode())

		#Bucle while True para seguir recibiendo información hasta que llegue el enunciado del siguiente reto
		while True:
			msg=sock.recv(1024)

			if msg.decode().split(':')[0]=='identifier':
				break
		sock.close()
		key=self.auxiliarKeys(msg)
		return key


	#Reto 1. Upper
	def reto1(self,key):
		sock= socket(AF_INET,SOCK_DGRAM)
		server= ('rick',4000)

		#Socket bind a nosotros mismos(localhost) con el puerto que hemos elegido aleatoriamente
		port=5673
		sock.bind(('0.0.0.0',port))

		#El mensaje que tenemos que enviar se forma concatenando el puerto y el id.
		msg=str(port)+' '+key
		print('Mensaje a enviar...')
		print(msg, '\n')
		sock.sendto(msg.encode(), server)

		#Aquí se recibe la "upper-query?" y envíamos.
		msg,server=sock.recvfrom(1024)
		msg=key.upper()
		print('Key en mayúsculas...')
		print(msg,'\n')
		sock.sendto(msg.encode(), server)

		#Y el servidor ya nos devolvería el enunciado siguiente
		msg,server=sock.recvfrom(1024)
		key=self.auxiliarKeys(msg)
		sock.close()
		return key

	#Reto 2. Word Counter
	def reto2(self,key):
		
		sock=socket(AF_INET,SOCK_STREAM)
		server=('rick',3002)
		sock.connect(server)
		contador=0				#Variable entera para contar las palabras que hay antes del flag.

		# Bucle prinicpal. Vamos recibiendo datos indefinidamente hasta que encontremos el flag.
		# Para saber si lo hemos encontrado o no utilizamos el método String.find().
		# Si devuelve -1, contamos los espacios (y \n \t) del mensaje entero, ya que no hemos encontrado el flag. Linea 121
		# Y si devuelve un valor distinto, es decir, si que lo encuentra, cuenta espacios etc. hasta la posicion del flag.
		while 1:
			msg=sock.recv(1024).decode()
			if msg.find("that's it")==-1:
				contador=contador+msg.count(" ")+msg.count("\n")+msg.count("\t")
			else:
				posicion=msg.find("that's it")
				contador= contador+msg[0:posicion].count(" ")+ msg[0:posicion].count("\n")+msg[0:posicion].count("\t")
				break
		
		
		print('Hay ',contador, ' palabras antes\n')
		mensaje=key+' '+str(contador)
		print('Mensaje a enviar\n',mensaje,'\n')
		sock.send(mensaje.encode())

		# Seguimos recibiendo datos hasta encontrar el enunciado siguiente.
		while True:
			msg=sock.recv(1024)

			if msg.decode().split(':')[0]=='identifier':
				break

		key=self.auxiliarKeys(msg)
		return key
		

	#Reto 3: Encontrar palabra anterior cuando la suma de números leídos supere 1200.
	def reto3(self,key):

		sock=socket(AF_INET,SOCK_STREAM)
		server=('rick',5500)
		sock.connect(server)

		#Recibimos el primer segmento e inicializamos salir, contador y palabra.
		msg=sock.recv(1024)
		salir=0
		contador=0
		palabra=""
		print('Analizando texto...')

		#Bucle que ejecuta la lógica principal del reto. La condicion de salida la controlamos con la variable salir.
		#Iteramos cada palabra del texto recibido. Si es un número, actualizamos el valor de contador, y si esta variable contador
		#supera los 1200, salir se vuelve 1.

		#En caso contrario, guardamos la palabra en "palabra". Al finalizar el bucle, ahí tendremos la última palabra leída.
		while True:
			for i in msg.decode().split():
				if i.isdigit()==True:
					contador=contador+int(i)
					if contador>1200:
						salir=1
						break
				else:
					palabra=i
			msg=msg+sock.recv(1024)
			if salir==1:
				break
		
		#Enviamos solución al server
		print('Palabra anterior -> ',palabra, '\n')
		mensaje=palabra +' '+ key 
		print('Mensaje a enviar...')
		print(mensaje,'\n')
		sock.send(mensaje.encode())

		while True:
			msg=sock.recv(1024)

			if msg.decode().split(':')[0]=='identifier':
				break

		key=self.auxiliarKeys(msg)
		return key


	#Reto 4: SHA1
	def reto4(self,key):
		sock=socket(AF_INET,SOCK_STREAM)
		server=('rick',9003)
		sock.connect(server)
		sock.send(key.encode())

		#Cogemos del mensaje recibido los datos (Contenido y Tamaño en bytes)
		msg=sock.recv(1024)		
		sum=msg.split(b':',1)[1]
		print('\nSize')
		size=msg.split(b':',1)[0].decode()
		print(size)

		#Calculamos SHA sum del archivo y envíamos seguidamente.
		m=hashlib.sha1()
		#Seguimos cogiendo datos hasta que lleguemos al tamaño total
		while int(size)!=len(sum):
			sum=sum+sock.recv(1024)
		m.update(sum)
		sha1=m.digest()
		sock.send(sha1)
		msg=sock.recv(2048)
		key=self.auxiliarKeys(msg)
		return key

	
	#Reto 5: WYP Request
	def reto5(self,key):

		#Variables:
		# Cheksum= Lo calculamos con el método chksum explicado arriba
		# Claveb64= La clave que concatenamos al final de la cabecera, previamente codificada en base 64(Linea 229)
		# Struct.pack= En la primera variable tenemos "!" que indica el orden de los bytes (big-endian), después tres bytes, y enteros,
		# siendo el último "1" el que representa el número de secuencia.

		cheksum=0
		sock=socket(AF_INET,SOCK_DGRAM)
		claveb64=base64.b64encode(key.encode())
		print(claveb64)
		header=struct.pack('!3sBHHH',b'WYP',0,0,0,1)+claveb64
		checksum =self.cksum(header)
		print('Cheksum -> ', checksum, '\n')
		print('Header que envio...')
		header=struct.pack('!3sBHHH',b'WYP',0,0,checksum,1)+claveb64
		print(header)

		sock.sendto(header,('rick',6000))
		msg,server=sock.recvfrom(2048)
		msg=base64.b64decode(msg[8:])
		sock.close()
		key=self.auxiliarKeys(msg)
		return key
	
	#Reto 6: GET Web Server
	def reto6(self,key):
		print('hola')
		sock=socket(AF_INET, SOCK_STREAM)
		sock.connect('rick',8003)
		mensaje=key+' '+ '3687'
		sock.send(mensaje.encode())
		print('Envia key')

		sock_server=socket(AF_INET,SOCK_STREAM)
		sock_server.bind(('0,0,0,0',3687))
		sock_server.listen(100)
		print('entra al bucle')
		while True:
			sock, server=sock_server.accept()
			msg=sock.recv(1024)
			print(msg)
			print('tamos dentro')
			peticion=msg.decode().split('\n')[0]
			GetOrPost=peticion.split()[0]

			if GetOrPost=='GET':
				new=msg.decode().split('code:')[1]
				print(new)
				return new.split()[0]
			rfc=msg.decode()
			rfc=rfc[rfc.find('rfc'):rfc.find('HTTP')-1]
			peticion=urllib.request(url='http://rick:81/rfc/'+rfc)

			with urllib.request.urlopen(peticion) as url:
				texto= url.read().decode('utf-8')
			 
			date=datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
			cabecera='HTTP/1.1 200 OK\r\n'+'Date: '+date+'\r\n'+'Content-Type: text/plain\r\n'+'Content-Length: '+ str(len(texto))+ '\r\n'
			paquete=cabecera+texto+'\r\n'
			sock.send(paquete.encode())

		sock_server.close()
		sock.close()
	
	

# Clase main del programa. Desde aquí creo un objeto yinkana, y llamo a los métodos de su clase, pasándole como argumento al reto i 
# la clave del reto i-1
def main():
	y=yinkana()

	key=y.reto0()
	key=y.reto1(key)
	key=y.reto2(key)
	key=y.reto3(key)
	key=y.reto4(key)
	key=y.reto5(key)
	#key=y.reto6(key)

main()