# from urllib.request import  Request
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
import math
import sqlite3
from datetime import datetime

keyword = "Indonesia"

url = "https://dl.acm.org/action/doSearch?"
params = {
    'AllField': keyword, 
    'ConceptID': 118230,
    'expand' : 'all',
    'startPage': 0,
    'pageSize' : 50,
}

url = url + urllib.parse.urlencode(params)
# options browser driver
opts = webdriver.FirefoxOptions()
opts.headless = True
# call browser driver

browser_driver = webdriver.Firefox(options=opts)
browser_driver.set_window_position(0, 0)
browser_driver.get(url)

#get html page source
html_source = browser_driver.page_source
soup = BeautifulSoup(html_source, "html.parser")
browser_driver.quit()

# get total records
allrecords = soup.find("span", {"class": "hitsLength"})
if allrecords is not None:
    allrecords = allrecords.getText()
    allrecords = int(allrecords.replace(',', ''))
    if allrecords > 0 : 
        # lakukan looping sebanyak
        for x in range( math.ceil(allrecords/50) ):
            url = "https://dl.acm.org/action/doSearch?"
            params = {
                'AllField': keyword, 
                'ConceptID': 118230,
                'expand' : 'all',
                'startPage': x,
                'pageSize' : 50,
            }
            url = url + urllib.parse.urlencode(params)
            browser_driver = webdriver.Firefox(options=opts)
            browser_driver.set_window_position(0, 0)
            browser_driver.get(url)

            html_source = browser_driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")
            browser_driver.quit()

            getdata = soup.find_all("span", {"class": "hlFld-Title"})
            if len(getdata)> 0:
                for link in getdata:
                    acm_link_master = link.find("a",href=True).get("href")
                    if acm_link_master is not None:
                        nurl = "https://dl.acm.org"+acm_link_master
                        
                        browser_driverl = webdriver.Firefox(options=opts)
                        browser_driverl.set_window_position(0, 0)
                        browser_driverl.get(nurl)
                        html_source = browser_driverl.page_source
                        browser_driverl.quit()
                    
                        soup = BeautifulSoup(html_source, "html.parser")
                        title = soup.find("h1", {"class": "citation__title"})
                        if title is not None : 
                            title = title.getText()
                        else: 
                            title = ""

                        authors = soup.find_all("li",{"class":"loa__item"})
                        if len(authors)>0 :
                            author = ""
                            for auth in authors:
                                authorval = auth.find("a",title=True).get("title")
                                author = author + authorval+ ", "
                        else:
                            author = ""

                        tahun_terbit = soup.find("span",{"class" : "CitationCoverDate"})
                        if tahun_terbit is not None :
                            tahun_terbit = tahun_terbit.getText()
                            tahun_terbit = datetime.strptime(tahun_terbit, "%d %B %Y")
                            tahun_terbit = tahun_terbit.strftime("%Y-%m-%d")
                        else:
                            tahun_terbit = ""
                        
                        abstract = soup.find("div",{"class" : "abstractSection abstractInFull"})
                        if abstract is not None:
                           abstract = abstract.getText()
                        else:
                            abstract = ""
                        
                        conn = sqlite3.connect("./database.sqlite")
                        check = conn.execute('SELECT * FROM acm WHERE (url=? AND title=?)', (nurl, title))
                        if check.fetchone() is None:
                            conn.execute("insert into acm (url, title, author, tahun_terbit, abstract) values (?, ?, ?, ?, ?)", [nurl, title, author, tahun_terbit, abstract])
                            conn.commit()

                        conn.close()