# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 22:49:13 2020

@author: pat4444
"""
import os, requests, zipfile, re, csv, io, numpy, pickle, gzip
from bs4 import BeautifulSoup


header = {

            'Host': 'ehw.fit.vutbr.cz',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'cs,sk;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': '_ranaCid=466197829.1564849665; _ga=GA1.2.905331781.1564849665',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'

        }


reg_codes = {
                'PHA' : '00.csv',
                'STC' : '01.csv',
                'JHC' : '06.csv',
                'PLK' : '03.csv',
                'KVK' : '19.csv',
                'ULK' : '04.csv',
                'LBK' : '18.csv',
                'HKK' : '05.csv',
                'PAK' : '17.csv',
                'OLK' : '14.csv',
                'MSK' : '07.csv',
                'JHM' : '06.csv',
                'ZLK' : '15.csv',
                'VYS' : '16.csv'
            }



data_columns =  [
                    'p1', 'p36', 'p37', 'p2a', 'weekday(p2a)', 'p2b',
                    'p6', 'p7','p8','p9','p10','p11','p12', 'p13a', 'p13b', 'p13c',
                    'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24',
                    'p27', 'p28', 'p34', 'p35', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a',
                    'p50b', 'p51', 'p52', 'p53', 'p55a', 'p57', 'p58', 'a', 'b', 'd', 'e', 'f', 'g', 'h',
                    'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's','t','p5a', 'region'
                ]



p = '/'

class DataDownloader:
    
    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/",folder="data", cache_filename="data_{}.pkl.gz"):
        self.cache_filename = cache_filename
        self.url = url
        self.cache = {}
        self.folder = folder
        
        self.make_clean_numpy_arrs_list()
       
        if not os.path.isdir(folder):
            os.mkdir(folder)
            
    """
    Stazeni vsech zipu z url
    """
    def download_data(self):
        
        r = requests.get(self.url, headers = header)
        soup = BeautifulSoup(r.text,'html.parser')
        
        for i in soup.find_all(class_='btn btn-sm btn-primary'):
            self.download_and_save(i.get('href')[5:])
        
    
    """
    Stahne a ulozi
    """
    def download_and_save(self, filename):
        
        r = requests.get(self.url+'data/'+filename, stream = True, headers = header)
        if r.ok:
            print("saving to", os.path.abspath(os.path.abspath(self.folder)+ p + filename))
            with open(os.path.abspath(self.folder) + p + filename, 'wb') as f:        
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:  # HTTP status code 4XX/5XX
            pass
            print("Download failed: status code {}\n".format(r.status_code))
            print(r.iter_content(), r.text)
            
    
    """
    Vytvoreni listu prazdnych numpy poli pro pozdejsi vkladani numpy poli
    """
    def make_clean_numpy_arrs_list(self):
        
        self.numpy_list = []
        self.temp_list = []
        
        for col in range(65): 
             self.numpy_list.append([])
             self.temp_list.append([])
       
        
        
        
    def parse_region_data(self, region):
        
        self.make_clean_numpy_arrs_list()
        
        usable_zips = ["datagis2016.zip", "datagis-rok-2017.zip",  "datagis-rok-2018.zip",  "datagis-rok-2019.zip"]
        html_zip_list = []
        downloaded_zip_list = []
        last_year = []
        r = requests.get(self.url,headers = header)
        soup = BeautifulSoup(r.text,'html.parser')
        
        # Zjisteni vsech souboru co jsou na strance ehw.fit.vutbr/izv
        for i in soup.find_all(class_='btn btn-sm btn-primary'):
             html_zip_list.append(i.get('href')[5:])
        
        # Zjisteni vsec stazenych souboru
        for filename in os.listdir(os.path.abspath(self.folder)):
            if filename.endswith(".zip"):
                downloaded_zip_list.append(filename)
                    
                
        # Stazeni pokud je na internetu nejaky soubor, ktery jeste neni stazeny
        for i in html_zip_list:
            if i not in downloaded_zip_list:
                self.download_and_save(i)
                downloaded_zip_list.append(i)
                
        # Pridani posledniho souboru z aktualniho roku
        for i in downloaded_zip_list:
            if re.match('datagis\-[0-9]{2}\-2020.*', i) is not None:
                last_year.append(i)
        last_year.sort()
        
        usable_zips.append(last_year[len(last_year)-1])
            
        
        # Pro vsechny nejnovejsi stazene soubory - zpracuj vsechny csv soubory dle zadaneho regionu
        for i in usable_zips:
            with zipfile.ZipFile(os.path.abspath(self.folder) + p + i, "r") as f:
                for name in f.namelist():
                    if reg_codes[region] == name:
                        self.read_csv_file(f.open(name), region)
                        
        
        # region je zpracovany, uloz ho do numpy pole
        for col in range(65):
            if col == 1 or col == 2 or (col >= 4 and col <= 44) or col in (56, 60, 61, 63):
                self.numpy_list[col] = numpy.array(self.temp_list[col], dtype = 'u8')
           
            elif col == 3:
                self.numpy_list[col] = numpy.array(self.temp_list[col],dtype = 'U10')
           
            elif (col >= 45 and col <= 50):
                self.numpy_list[col] = numpy.array(self.temp_list[col],dtype = 'f8')
           
            else:
                self.numpy_list[col] = numpy.array(self.temp_list[col])
    
        
        self.temp_list.clear()
        
        
        # Ulozi zpracovany region do cache
        self.cache[region]= self.numpy_list.copy()
        
        file_name = (self.cache_filename).format(region)
        
        # Ulozi cache do souboru pkl.gz
        
        pkl_gz_file = gzip.open(os.path.abspath(self.folder) + p + file_name, 'wb')
        pickle.dump(self.numpy_list.copy(), pkl_gz_file)
        pkl_gz_file.close()
        
        
        return (data_columns, self.numpy_list)
    
    
    def read_csv_file(self, csv_file, region):
        
       
        
        csv_reader = csv.reader(io.TextIOWrapper(csv_file, encoding = 'windows-1250'), delimiter=';')
         
        for row in csv_reader:
            for col in range(64):
                if (col == 1 or col == 2 or (col >= 4 and col <= 50) or col in (56, 60, 61, 63)):
                    if (col >= 45 and col <= 50):
                         row[col] = (row[col]).replace(',', '.')
                    try:
                        float(row[col])
                    except: 
                        row[col] = 999999999 # Nevalidni hodnota u intu nebo floatu
                
                self.temp_list[col].append(row[col])
                
            self.temp_list[64].append(region)
       
          
                    
    def get_list(self, regions = None):
        
        
        if regions == None: #Zpracij vsechny regiony
            regions = []
            for i in reg_codes.keys(): regions.append(i)
                
       
        ret_numpy_list = []
       
        for c, i in enumerate(regions):
            file_name = (self.cache_filename).format(i)
            
            if i in self.cache: #je v cache
                pass
            
            elif os.path.isfile(os.path.abspath(self.folder) + p + file_name): # v cache neni ale existuje zpracovany soubor
                 with gzip.open(os.path.abspath(self.folder) + p + file_name, "rb") as f:
                    self.cache[i] = pickle.load(f)
            else: # neni ani v cache ani neexistuje soubor - musi se zpracovat
                 self.parse_region_data(i)
               
            
            if len(regions) == 1: 
                ret_numpy_list = (self.cache[i]).copy()
                break
            
            if c == 0:
                ret_numpy_list = (self.cache[i]).copy()
                continue
            
            for j in range(65):
                ret_numpy_list[j] = numpy.append(ret_numpy_list[j], self.cache[i][j])
         
                    
        return (data_columns, ret_numpy_list)
        
        
          
            
      
        
        
       
                
    
if __name__== "__main__":
    x = DataDownloader()
    c = x.get_list(['ZLK', 'OLK', 'MSK'])

    print('Sloupce', data_columns)
    
    print('Celkovy pocet zaznamu: ', len(c[1][0]))
    print('Kraje: Zlinsky, Olomoucky, Moravskoslezsky')
    





            
            
            
            
            
