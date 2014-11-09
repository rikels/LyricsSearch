'''
	* You'll need to download pycurl, xmltodic, BeautifulSoup and maybe json, but i think that is a default one
	* Easiest method to do so: "(sudo) pip install pycurl xmltodict BeautifulSoup json"
	
	* ViewLyrics Open Searcher
	* Developed by PedroHLC
	* Converted to python by Rikels
	* Last update: 5-11-2014
	
	* lyricswikia Lyric returner
	* Developed by Rikels
	* Last update: 29-8-2014
'''

import hashlib
import pycurl
import StringIO
import io
import httplib, urllib
import xmltodict
import json
from BeautifulSoup import BeautifulSoup
import re

#function to return python workable results from Minilyrics
def MiniLyrics(artist,title):
    search_url = "search.crintsoft.com/searchlyrics.htm"
    search_query_base = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?><searchV1 client=\"ViewLyricsOpenSearcher\" artist=\"{artist}\" title=\"{title}\" OnlyMatched=\"1\" />"
    search_useragent = "MiniLyrics";
    search_md5watermark = "Mlv1clt4.0"

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
        header = [  "User-Agent: {ua}".format(ua=ua),
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

    if('search_result' not in locals()):
        #didn't receive a reply from the server
        print ("FAILED")
    else:
        #Server returned possible answers
        xml = vl_dec(search_result)
        xml = xmltodict.parse(xml)
        server_url = str(xml["return"]["@server_url"])
        result = []
        i = 0
        for item in xml["return"]["fileinfo"]:
            #because the rating will sometimes not be filled, it could give an error, so the rating will be 0 for unrated items
            try:
                rating = item["@rate"]
            except:
                rating = 0
            result.append({'artist': item["@artist"], 'title': item["@title"], 'rating': rating, 'filetype': item["@link"].split(".")[-1], 'url': (server_url + item["@link"])})
            i += 1
    return(result)


#function to return lyrics grabbed from lyricswikia
def LyricWikia(artist,title):
    curl = pycurl.Curl()
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(curl.MAXREDIRS, 5)
    curl.setopt(curl.CONNECTTIMEOUT, 15)
    curl.setopt(curl.TIMEOUT, 15)
    curl_url = 'http://lyrics.wikia.com/api.php?artist={artist}&song={title}&fmt=json'.format(artist=artist,title=title).replace(" ", "%20")
    #first we have to query for the right url
    curl.setopt(curl.URL, curl_url)
    #creating a string to be able to store the retrieved data in
    curl_data = StringIO.StringIO()
    #setting the option to write the retrieved data to the string
    curl.setopt(pycurl.WRITEFUNCTION, curl_data.write)
    curl.perform()
    #We got some bad formatted data... So we need to fix stuff :/
    curl_return = curl_data.getvalue()
    curl_return = curl_return.replace("\'","\"")
    curl_return = curl_return.replace("song = ","")
    curl_return = json.loads(curl_return)
    if curl_return["lyrics"] != "Not found":
        #set the url to the url we just recieved, and retrieving it
        curl.setopt(curl.URL, str(curl_return["url"]))
        curl.perform()
        soup = BeautifulSoup(curl_data.getvalue())
        soup = soup.find("div", {"class": "lyricbox"})
        [elem.extract() for elem in soup.findAll('div')]
        [elem.replaceWith('\n') for elem in soup.findAll('br')]
        soup = BeautifulSoup(str(soup),convertEntities=BeautifulSoup.HTML_ENTITIES)
        soup = BeautifulSoup(re.sub(r'(<!--[.\s\S]*-->)','',str(soup)))
        [elem.extract() for elem in soup.findAll('script')]
        return soup.getText()
    else:
        return