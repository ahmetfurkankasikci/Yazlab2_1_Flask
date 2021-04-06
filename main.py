from flask import Flask,render_template,request,url_for,redirect
import requests
import re
from nltk.corpus import wordnet
from collections import Counter
from bs4 import BeautifulSoup
from numpy.linalg import norm
from numpy import dot



app=Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html') 

@app.route('/ana/<int:id>')
def firstTwopages(id):
   return render_template('first_second.html',id=id)

@app.route('/third')
def thirdPage():
   return render_template("third.html")

@app.route('/fourth')
def fourthPage():
   return render_template("fourth.html")


@app.route('/ana/<int:id>', methods=['POST', 'GET'])
def verilerial(id):
   if request.method == 'POST':
      link = request.form.get('link')
      ht = requests.get(link)
      if(id==1):
         return render_template('veri1.html',link=first(ht),id=id)
      if(id==2):
         return render_template('veri2_5.html',link=second(ht),id=id,synonyms=fifth(ht))

   return '404 Not Found Error' 

@app.route('/third', methods=['POST', 'GET'])
def verilerial3():
   if request.method == 'POST':
      link1=request.form.get('first_link')
      ht1 = requests.get(link1)
      words1=first(ht1)
      link2 = request.form.get('second_link')
      ht2 = requests.get(link2)
      words2=first(ht2)

      return render_template("veri3.html",score=third(words1,words2),keys1=second(ht1),keys2=controlKeyWords(ht1,ht2))

   return '404 Not Found Error'

@app.route('/fourth', methods=['POST', 'GET'])
def verilerial4():
   if request.method == 'POST':
      link1=request.form.get('first_link')
      link2=request.form.get('main_link')
      ht2 = requests.get(str(link2))
      texts = link1.split("\r")
      link_list = []
      for i in texts:
         link_list +=i.split("\n")

      link_list = list(filter(None, link_list))
      print(link_list)

      return render_template("veri4_5.html",scores=fourth(link_list,link2),link=second(ht2),synonyms=fifth(ht2))

   return '404 Not Found Error'
def addSublink(main_link):
   ht=requests.get(main_link)
   soup=BeautifulSoup(ht.text,'html.parser')
   sayi=0
   urls=[]

   for url in soup.find_all('a'):  
      
      try:
         yedek=str(url.get('href'))
         ht2=requests.get(yedek)
        
         print(ht2)
         if(yedek.startswith('https:')):
           
            urls.append(url.get('href'))
            sayi=sayi+1
            print(sayi)
         if sayi==5:
            break
      except:
         print("Site not found")

   return urls  


arr=["more","from","with","that","after","back","under","suspend","this","shots","halting","goes","begins","another","ever","given","about","subscribe","starts","subscribed"]      
def first(ht):
   soup = BeautifulSoup(ht.text, "html.parser")
   clean = re.sub(r"""
               [1234567890:.,-;@#?!&$]+  
               \ *           
               """,
               " ",          
               soup.text, flags=re.VERBOSE)
   
   regex=re.compile('[^a-zA-Z \s]')
   

   a=Counter(list(filter(None,regex.sub('',clean.lower()).split(" "))))
   b = []
   for i in a:
      b+=i.split("\n")
   sayac = Counter(list(filter(None, b)))
  
   return sayac

def second(ht):
   sayac=first(ht)
   sayi=0
   my_dict=dict()

   for k,v in sayac.most_common(len(sayac)):
    if(len(k)>3 and control(k)):
        sayi=sayi+1
        my_dict[k]=v

        if sayi==5:     
            break

   return my_dict 

def control(word):
   for i in arr:
      if(i==word):
         return False
   return True

   
def third(ht1,ht2):
   
   values1=list(ht1.values())
   values2=[]

   for a in ht1.keys():
      if a in ht2:
         values2.append(ht2[a])
      else:
         values2.append(0)   
   return dot(values1,values2)/(norm(values1)*norm(values2))*100
  

def controlKeyWords(ht1,ht2):
   my_dict1=second(ht1)
   words2=first(ht2)
   strC=""

   for k1,v1 in my_dict1.items():
     for k,v in words2.items():
        if(k1==k):
           strC=strC+str(k)+":"+str(v)+" "

   return strC        
         

def fourth(link_list,main_link):
   sub_links=addSublink(main_link)
   for i in sub_links:
      link_list.append(i) 
   scores =[]

   for i in range(0,len(link_list)):
      ht1 = requests.get(str(main_link))
      my_dict1=first(ht1)
      

      
      ht2 = requests.get(str(link_list[i]))
      words2=first(ht2)
     
      
      cos_sim=third(my_dict1,words2)
     
      son = [cos_sim,str(main_link)+" - "+str(link_list[i])+" Tekrar Edenler:"+controlKeyWords(ht1,ht2)]
      scores.append(son)
   scores.sort(reverse=True)
   
   return scores
      
def fifth(ht):
   keywords=second(ht)
   es=""
   ana=first(ht)
   for k in keywords.keys():
      yedek=findSynonyms(k)
      es=es+controlSynonyms(yedek,ana)
      

   return es

def controlSynonyms(yedek,ana):
   alaka="Kelime:"
   for s in yedek:
      if(controlWordList(s,ana)):
         alaka=alaka+s+" "

   alaka=alaka+"-- ,"      

   return alaka


def controlWordList(word,link):
   for k in link.keys():
      if(word==str(k)):
         return True
   return False 

def findSynonyms(keyword) :
    synonyms = []
    for synset in wordnet.synsets(keyword):
        for lemma in synset.lemmas():
           if(lemma.name()!=keyword):
               synonyms.append(lemma.name())

    return set(synonyms)

if __name__=="__main__":
    app.run()