import requests
import json
import re
import datetime
import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime


class Scrapping:
    def __init__(self):
        self.domain = 'http://www.ceo.kerala.gov.in'
        self.base_url = self.domain + '/erollArchives.html'
        self.session = requests.Session()
        self.log_file = open('error.txt', 'a')
        self.outfolder = "output/"
        self.create_folder_if_not_exists(self.outfolder)

    def start(self):
        for year in range(2011, 2012):
            for lac in range(1, 141):
                self.save_path = self.outfolder + "year{}/".format(year) + "pdfs{}".format(lac)
                self.create_folder_if_not_exists(self.save_path)
                self.getBoothList(year, lac)

    def getBoothList(self, year, lac):
        data = {
            "rollYear": year,
            "lacNo": 9
        }        
        try:
            r = self.session.post(self.base_url, data = data, headers = {}, timeout=10)
            html = r.content.decode('utf-8')
            soup=BeautifulSoup(html,'lxml')
            rows = soup.find('div', {'aria-live':'polite'}).find_all("a")
            for row in rows:
                self.pdf_url = row['href']
                booth_id = row.text
                print(booth_id, self.pdf_url)
                try:
                    self.download_pdf()
                except Exception as e:
                    self.log_file.write('{} [Failed] {} {} {} {}\n'.format(datetime.now(), year, lac, booth_id, self.pdf_url))
                    self.log_file.write('{} [Error] {}\n'.format(datetime.now(), e))
                    print("Skip", year, lac, booth_id, self.pdf_url)
        except Exception as e:
            print(self.pid, "Get details Failed")
            print(e)
            return 0          

    def download_pdf(self):
        html = self.session.get(self.pdf_url).text
        soup=BeautifulSoup(html,'lxml')
        self.pdf_download_url = soup.find('form', {'id':'eRollDownloadFormId'}).get('action')
        print(self.pdf_download_url)
        self.download_file()

    def download_file(self):
        local_filename = self.save_path + "/" + self.pdf_url.split('/')[-1]
        # NOTE the stream=True parameter below
        if os.path.exists(local_filename):
            return local_filename

        with requests.get(self.pdf_download_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        return local_filename

    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)
            
if __name__ == "__main__":
    scrap = Scrapping()
    scrap.start()
