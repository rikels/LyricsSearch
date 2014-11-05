'''
  * ViewLyrics Open Searcher
  * Developed by PedroHLC
  * Converted to python by Rikels
  * Last update: 17-10-2014
  * You'll need to download pycurl and xmltodict
  * Easiest method to do so: "(sudo) pip install pycurl"
'''

import hashlib
import pycurl
import StringIO
import httplib, urllib
import xmltodict

search_url = "search.crintsoft.com/searchlyrics.htm"
search_query_base = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?><searchV1 client=\"ViewLyricsOpenSearcher\" artist=\"{artist}\" title=\"{title}\" OnlyMatched=\"1\" />"
search_useragent = "MiniLyrics";
search_md5watermark = "Mlv1clt4.0"

#asking the user to input an artist and title
artist = raw_input("Artist: ")
title = raw_input("Title: ")

#hex is a registered value in python, so i used hexx as an alternative
def hexToStr(hexx):
	string = ''
	i=0
	while(i < (len(hexx)-1) ):
		string += chr(int(hexx[i] + hexx[i+1], 16))
		i += 2
	return (string)

def vl_enc(data, md5_extra):
	datalen = len(data)
	md5 = hashlib.md5()
	md5.update(str(data)+str(md5_extra))
	hasheddata = hexToStr(md5.hexdigest())
	j = 0
	i = 0
	while(i < datalen):
		j += ord(data[i])
		i += 1
	magickey = chr(int(round(float(j)/float(datalen))))
	encddata = list(xrange(len(data)))
	if isinstance(magickey, int):
		pass
	else:
		magickey = ord(magickey)
	for i in range(datalen):
		#Python doesn't do bitwise operations with characters, so we need to convert them to integers first.
		#It also doesn't like it if you put integers in the ord() to be translated to integers, that's what the IF, ELSE is for.
		if isinstance(data[i], int):
			encddata[i] = data[i] ^ magickey
		else:
			encddata[i] = ord(data[i]) ^ magickey
	result = "\x02" + chr(magickey) + "\x04\x00\x00\x00" + str(hasheddata) + bytearray(encddata)
	return(result)

search_encquery = vl_enc(search_query_base.format(artist = artist, title = title), search_md5watermark)

def http_post(url, data, ua):
	#I could set the user agent with Pycurl itself, but since we're already creating a header, I just pasted in here.
	header = [	"User-Agent: {ua}".format(ua=ua),
				"Content-Length: {content_length}".format(content_length = len(data)),
				"Connection: Keep-Alive",
				"Expect: 100-continue",
				"Content-Type: application/x-www-form-urlencoded"
				]
	curl = pycurl.Curl()
	curl.setopt(pycurl.TIMEOUT, 15)
	curl.setopt(pycurl.HTTPHEADER, header)
	curl.setopt(pycurl.URL, url)
	#creating a string to be able to store the retrieved data in
	curl_data = StringIO.StringIO()
	#setting the option to write the retrieved data to the string
	curl.setopt(pycurl.WRITEFUNCTION, curl_data.write)
	#making it a HTTP post request
	curl.setopt(pycurl.POST, 1)
	#setting the data to be posted
	curl.setopt(pycurl.POSTFIELDS, str(data))
	#trying to keep the script as sturdy as possible
	try:
		curl.perform()
		response = curl_data.getvalue()
		return(response)
	except:
		pass
	#if the request was denied, or the connection was interrupted, retrying. (up to five times)
	fail_count = 0
	while (curl_data.getvalue() == "") and (fail_count < 5):
		fail_count += 1
		print("buffer was empty, retry time: {fails}".format(fails=fail_count))
		try:
			curl.perform()
		except:
			pass
		if fail_count >= 5:
			print ("didn't receive anything from the server, check the connection...")
			return

try:
	search_result = http_post(search_url, search_encquery, search_useragent);
except:
	print("something went wrong, could be a lot of things :(")
def vl_dec(data):
	magickey = data[1]
	result = ""
	i = 22
	datalen = len(data)
	if isinstance(magickey, int):
		pass
	else:
		magickey = ord(magickey)
	for i in range(22 ,datalen):
		#python doesn't do bitwise operations with characters, so we need to convert them to integers first.
		if isinstance(data[i], int):
			result += chr(data[i] ^ magickey)
		else:
			result += chr(ord(data[i]) ^ magickey)
	return(result)

if('search_result' not in globals()):
	#didn't receive a reply from the server
	print ("FAILED")
else:
	#Server returned possible answers
	result = vl_dec(search_result)
	print(result)
	result = xmltodict.parse(result)
	for item in result["return"]["fileinfo"]:
	print(u"{artist} - {title}.{file_type}".format(artist = item["@artist"], title = item["@title"], file_type = item["@link"].split(".")[-1]))