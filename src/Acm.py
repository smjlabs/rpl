from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
import math
import sqlite3
from datetime import datetime



class Acm:
    def __init__(self, keyword, limit):
        self.keyword = keyword
        # self.keyword = "Deep Learning"
        url = "https://dl.acm.org/action/doSearch?"
        params = {
            'AllField': keyword, 
            'ConceptID': 118230,
            'expand' : 'all',
            'startPage': 0,
            'pageSize' : 50,
        }
        self.url = url + urllib.parse.urlencode(params)
        self.limit = limit

    def getTotal(self):
        opts = webdriver.FirefoxOptions()
        opts.headless = True
        browser_driver = webdriver.Firefox(options=opts)

        browser_driver.set_window_position(0, 0)
        browser_driver.get(self.url)

        #get html page source
        html_source = browser_driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        browser_driver.quit()

        allrecords = soup.find("span", {"class": "hitsLength"})
        if allrecords is not None:
            allrecords = allrecords.getText()
            allrecords = int(allrecords.replace(',', ''))
            return allrecords
        else:
            return 0

    def scrapping(self):
        opts = webdriver.FirefoxOptions()
        opts.headless = True
        browser_driver = webdriver.Firefox(options=opts)

        browser_driver.set_window_position(0, 0)
        browser_driver.get(self.url)

        #get html page source
        html_source = browser_driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        browser_driver.quit()

        allrecords = soup.find("span", {"class": "hitsLength"})
        if allrecords is not None:
            allrecords = allrecords.getText()
            allrecords = int(allrecords.replace(',', ''))
            if allrecords > 0 : 
                # lakukan looping sebanyak
                for _page in range( math.ceil(allrecords/50) ):
                    url = "https://dl.acm.org/action/doSearch?"
                    params = {
                        'AllField': self.keyword, 
                        'ConceptID': 118230,
                        'expand' : 'all',
                        'startPage': _page,
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
                                        if len(authors) == auth:
                                            author = author + authorval
                                        else: 
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
                                check = conn.execute('SELECT * FROM scrapping_data WHERE (url=? AND title=? AND sumber=? AND keyword=?)', (nurl, title,'acm',self.keyword))
                                if check.fetchone() is None:
                                    conn.execute("insert into scrapping_data (url, title, author, tahun_terbit, abstract, sumber, keyword) values (?, ?, ?, ?, ?, ?, ?)", [nurl, title, author, tahun_terbit, abstract, 'acm', self.keyword])
                                    conn.commit()

                                conn.close()

                            conn1 = sqlite3.connect("./database.sqlite")
                            records1 = conn1.execute("select * from scrapping_data where (sumber=? AND keyword=?)",('acm',self.keyword)).fetchall()
                            if len(records1) >= int(self.limit) or len(records1) == int(allrecords):
                                break

        return True