#----- Package Import -------
import pandas as pd
import numpy as np
import seaborn as sns
import requests
import re
import time
import random
import sys
from random import randint
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import date
session = HTMLSession()

#------ Function definition --------
def list_scrub (char_list, scrub_list):
    #Remove characters from the strings in one list
    for pos1, char in enumerate(char_list):
        for pos2, string in enumerate(scrub_list):
            scrub_list[pos2] = scrub_list[pos2].replace(char_list[pos1],'')
    return scrub_list;

banned_chars = ["[","]","(",")","+","-","*"]
banned_words = ["limited","Ireland","ltd","plc","hq","Inc","laptops","DT","client","refresh","RR","run rate"]
    

def string_count(string, x):
    #Count all isntances of x in a string (word by word)
    counter = 0
    string = string.split()
    for ele in string:
        if (ele == x):
            counter = counter + 1
    return counter

#--------- Body  -----------

#Import company name (cn) and company country (cc)
input_name = "List.csv"

path = str(sys.path[0]) + "\\" + input_name
df = pd.read_csv(path , header = 0)
df.columns = ["cn" , "cc"]
df = df.drop_duplicates(['cn'])

#Company industry (ci) scrapper using duck duck go result_snippet routine
i = 0
df["ci"] = ""
cn_i = ""


#Take the first webpage that is not an add and scrap the result_snippet
while i<len(df): 
    
    time.sleep((random.random()*randint(3,6))) #sleep in between connections to minimize footprint
    
    #Search wikipedia first
    cn_i = df.iloc[i,0]
    cn_i = cn_i.split("-")[0] #For PUMP 
    cn_i = cn_i.split()
    cn_i = list_scrub (banned_words, cn_i)
    cn_i = "_".join(cn_i)
    cn_i = cn_i.lower()
    
    print(str (i)+ "| Search term : " + cn_i) #Counter to see where any error comes from
    
    url = "https://en.wikipedia.org/wiki/"+cn_i
    r = session.get(url)
    soup = BeautifulSoup (r.text , 'html.parser') #Using request to turn the r into an HTML and immediatly parsing it w/ beautiful soup
    ci = soup.find_all('p')[0:4]
    
    if len(ci) > 2 : #Wikipedia is full
        res_str = ""        
        for w in ci:
            res_str = res_str+str(w.text)
            
        df.iloc[i,2] = res_str
        print ("WIKIPEDIA --> " + str(res_str))
    
    else: #Wikipedia is False so Duck Duck Go
        
        cn_i = df.iloc[i,0] 
        cn_i = cn_i.split()
        cn_i = list_scrub (banned_words, cn_i)
        cn_i = "+".join(cn_i)
        url = "https://duckduckgo.com/lite?q=%22"+cn_i+"%22" # create Duck Duck Go search url from company name

        r = session.get(url)#Scrap online database, get keywords and copy into df
        ci = r.html.find(".result-snippet", first = True)
    
        if ci is None: #No data error loop || First look at another search engine(Mojeek) then spit out an error
        
            url = "https://www.mojeek.com/search?q="+cn_i #Mojeek URL creation
            r = session.get(url)
            ci = r.html.find(".s", first = True)
            
            if ci is None:    
                df.iloc[i,2] = "n/a"
                print ("|-> n/a error <-|")
            
            else : #Add to DF from MOJEEK
                ci = ci.text
                df.iloc[i,2] = ci
                print ("MOJEEK --> " + str(ci))
        
        else : #Add to DF from DUck DUCK GO 
            ci = ci.text
            df.iloc[i,2] = ci
            print ("DUCK DUCK GO --> " + str(ci))
        
    print("--------")
    i = i + 1
    
print ("Finished internet searches")
#END of Company industry (ci) scrapper using duck duck go result_snippet routine

#Keyword to industry [NACE] routine
nace_input_name = "Dict.csv"

path = str(sys.path[0]) + "\\" + nace_input_name
df_n = pd.read_csv(path, header = 0)
i = 0

df['NACE'] = ""
df['Confidence rating'] = ""

nace_col = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s']
nace_name = ['Forestry','Minning' , 'Manufacturing' , 'Energy' , 'Water supply', 'Construction', 'Wholesale and retail', 'Transportation and storage' , 'Accomodation and food',
                  'Information','Finance','Real Estate','Technical and science','Administration','Public','Education','Health','Art and entertainment','Services']
    
while i < len(df):     #company indentation
    kt = df.iloc[i,2]  #Key term is taken from result_snippet
    count_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #re init the count list
    
    if kt is np.nan:  #Error loop if no key term entered in previous step
        i = i+1
        i2 = 1
        kt = ["0"]
        
    else:  # transorm key term into list of word to be looked up individually
        kt = df.iloc[i,2]
        kt = kt.lower()
        kt = kt.split()
        kt = list_scrub(banned_chars, kt)
        kt.append(df.iloc[i,0].lower().split())    #Add the name of the company to the key-term being compared to the wieghted NACE list
        
        i2 = 0 
    
    while i2 < len(kt): # Key term in list indentation
        i3 = 0
    
        while i3 < len(nace_col) : #NACE search dic colu;ns indentation
            dic_str = df_n[nace_col[i3]].str.cat(sep=' ') #keyword DF to one string for exact word matching
            
            if re.search(r'\b' + str(kt[i2]) + r'\W' , dic_str): #exact string search
                count_list[i3] = count_list[i3] + string_count(dic_str, str(kt[i2])) #Add to count_list every time a word matches, the weight of the word is how many time it is in the nace list
            
            i3 = i3+1
        #print ("Key term: "+str(kt[i2])) #Used to check if the keyword to Dic to list system is working
        #print(count_list)
        i2 = i2+1
        
    for position, count in enumerate(count_list): #counts wich category as the most match and adds the NACE accordingly 
        if count is max(count_list):
            df.iloc[i,3] = nace_name[position] # Add to the DF the Nace on that company's line
            #Fix error division error
            accuracy = max(count_list)/len(kt)+1 #Accuracy reading is % of words that fit in the selected category vs all the word in kt
            df.iloc[i,4] = accuracy  
        
    if df.iloc[i,3] == '': #If no Nace show up, let user know
        df.iloc[i,3] = "n/a"
        print (str(df.iloc[i,0]) + "|-> n/a error <-|")
        
    print(str(df.iloc[i,0])+ " --> " + str(df.iloc[i,3] + " |Accuracy = ") + str(accuracy))
    
    i = i+1 #Move to next company

print("Finished NACE scoring")
#End of Keyword to industry [NACE] routine

#Output saving routine
p = sys.path #Save output in the same folder where the Python script is saved
p = p[0]
post = "C2I_results_" + str(date.today()) + ".csv"
save = p+"\\"+post

df.to_csv(save)

print ("output saved in "+ str(save))
