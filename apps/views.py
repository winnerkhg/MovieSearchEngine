import math
import num2words
import re
import os
import ast
import PyPDF2
from django.shortcuts import render, redirect
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from collections import Counter

porter_stemmer = PorterStemmer()

def word_tokenize_all(list1):
    punctuations = ['+',',','?','!','/','@','#','$','-','.',':','""', '(', ')', '<', '>', '--']
    tokens = []
    for lines in list1:
        all_words = word_tokenize(lines)
        all_words = [x.lower() for x in all_words]
        filtered_words = [word for word in all_words if word not in stopwords.words('english')+punctuations]
        stemmed_word = [porter_stemmer.stem(word) for word in filtered_words]
        add_numbers = [num2words.num2words(int(words)) if words.isnumeric() else words  for words in stemmed_word]
        tokens.append(add_numbers)
    return tokens

def tf(t,d):
    if d.count(t)==0:
        return 0
    else:
        return (1 + math.log(d.count(t)))

def idf(t,D):
	count_in_doucment = 0
	#print(len(D))
	for d in D:
		if t in d:
			count_in_doucment += 1
	return 0 if count_in_doucment == 0 else math.log(len(D)/float(count_in_doucment))

def cosineScore(listA,listB,op,docid):
	module_dir = os.path.dirname(__file__)
	file_path  = os.path.join(module_dir, 'cosRelevence.txt')
	lines = [line.rstrip('\n') for line in open(file_path)]
	if op == 'and':
		if len(set(listA).intersection(listB))==len(set(listA)):
			listA = set(listA)
			listB = set(listB)
			counterA = Counter(listA)
			counterB = Counter(listB)
			terms = set(counterA).union(counterB)
			dotprod = sum(counterA.get(k, 0) * counterB.get(k, 0) for k in terms)
			magA = math.sqrt(sum(counterA.get(k, 0)**2 for k in terms))
			magB = math.sqrt(sum(counterB.get(k, 0)**2 for k in terms))
			if(dotprod != 0):
				return ((dotprod / (magA * magB)) + math.log(int(lines[docid])))
			else:
				return 0
	else:
		listA = set(listA)
		listB = set(listB)
		counterA = Counter(listA)
		counterB = Counter(listB)
		terms = set(counterA).union(counterB)
		dotprod = sum(counterA.get(k, 0) * counterB.get(k, 0) for k in terms)
		magA = math.sqrt(sum(counterA.get(k, 0)**2 for k in terms))
		magB = math.sqrt(sum(counterB.get(k, 0)**2 for k in terms))
		if dotprod != 0:
			if lines[docid] == '':
				return 0
			else:
				return (dotprod / (magA * magB)) + math.log(int(lines[docid]))
		else:
			return 0

def score(q,docid, d, op_type,D):
	module_dir = os.path.dirname(__file__)
	file_path = os.path.join(module_dir, 'relevence.txt')
	lines = [line.rstrip('\n') for line in open(file_path)]
	if op_type=='and':
		if len(set(q).intersection(d)) == len(set(q)):
			ret = 0
			for t in q:
				ret += math.log(1+tf(t, d)) * idf(t,D)
			if ret != 0:
				if lines[docid] == '':
					return 0
				else:
					ret = ret + math.log(int(lines[docid]))
			return ret
		else:
			return 0
	else:
		ret = 0
		for t in q:
			ret += math.log(1+tf(t, d)) * idf(t,D)
		if ret != 0:
			if lines[docid] == '':
				return 0
			else:
				ret = ret + math.log(int(lines[docid]))
		return ret

def cosrelevence(request):
	if request.method == "POST":
		module_dir = os.path.dirname(__file__)
		file_path  = os.path.join(module_dir, 'cosRelevence.txt')
		lines      = [line.rstrip('\n') for line in open(file_path)]
		doc        = request.POST["id"]
		print(int(doc))
		print(lines[int(doc)])
		lines[int(doc)] = str(int(lines[int(doc)])+1)
		print(lines[int(doc)])
		file_path = os.path.join(module_dir, 'cosRelevence.txt')
		fp = open(file_path , 'w+')
		for i in range(0,999):
			fp.write(lines[i] + "\r\n")
		fp.close()
		file_path = os.path.join(module_dir, 'documentss')
		i=0
		for filename in os.listdir(file_path):
			if filename.endswith(".pdf"):
				if(i==int(doc)):
					f = (file_path +'/'+ filename)
					# lines = f.read()
					# lines = lines.replace(',', ' ')
					# string = lines
					# f.close()
					read_pdf = PyPDF2.PdfFileReader(f)
					page = read_pdf.getPage(0)
					page_content = page.extractText()
					lines = page_content.replace(',', ' ')
					string = lines
				i=i+1

		for i in range(0,len(string)):
			if string[i]=='u' and string[i+1]=='r' and string[i+2]=='l' :
				link = string[i+5:]

		string = string.replace(link,"")
	return render(request,'apps/Cossearchcontent.html',context={"content":string,"urllink":link})


def relevence(request):
	if request.method == "POST":
		module_dir = os.path.dirname(__file__)
		file_path = os.path.join(module_dir, 'relevence.txt')
		lines = [line.rstrip('\n') for line in open(file_path)]
		doc = request.POST["id"]
		# print(int(doc))
		# print(lines[int(doc)])
		# lines[int(doc)] = str(int(lines[int(doc)])+1)
		# print(lines[int(doc)])
		# file_path = os.path.join(module_dir, 'relevence.txt')
		# fp = open(file_path , 'w+')
		# for i in range(0,999):
		# 	fp.write(lines[i] + "\r\n")
		# fp.close()

		file_path = os.path.join(module_dir, 'documentss')
		i=0
		for filename in os.listdir(file_path):
			if filename.endswith(".pdf"):
				if(i==int(doc)):
					f =(file_path +'/'+ filename)
					read_pdf = PyPDF2.PdfFileReader(f)
					page = read_pdf.getPage(0)
					page_content = page.extractText()
					lines = page_content.replace(',', ' ')
					string = lines
				i=i+1

		for i in range(0,len(string)):
			temp = ''
			if string[i]=='u' and string[i+1]=='r' and string[i+2]=='l' :
				temp += string[i+5:]

		string = string.replace(temp, "")
	return render(request,'apps/searchcontent.html',context={"content":string,"urllink":temp})

def preprocess(request):
	module_dir = os.path.dirname(__file__)
	file_path = os.path.join(module_dir, 'documentss')
	list1 = []
	for filename in os.listdir(file_path):
		if filename.endswith(".pdf"):
			f = (file_path +'/'+ filename)
			read_pdf = PyPDF2.PdfFileReader(f)
			page = read_pdf.getPage(0)
			page_content = page.extractText()
			lines = page_content.replace(',', ' ')
			list1.append(lines)

	D = word_tokenize_all(list1)
	print(len(D))
	file_path = os.path.join(module_dir, 'bag.txt')
	fp = open(file_path , 'w+')
	fp.write(str(D))
	fp.close()

	file_path = os.path.join(module_dir, 'cosRelevence.txt')
	fp = open(file_path , 'w+')
	for i in range(0,999):
		fp.write("1\r\n")
	fp.close()

	file_path = os.path.join(module_dir, 'relevence.txt')
	fp = open(file_path , 'w+')
	for i in range(0,999):
		fp.write("1\r\n")
	fp.close()

	return redirect("/index/")

def index(request):
	if request.method == "POST":
		#dictionary containing top k documents which matches the query term
		module_dir = os.path.dirname(__file__)
		file_path = os.path.join(module_dir, 'bag.txt')
		fp = open(file_path, 'r')
		D=fp.read()
		D = ast.literal_eval(D)
		fp.close()
		file_path = os.path.join(module_dir, 'documentss')
		list1 = []
		for filename in os.listdir(file_path):
			if filename.endswith(".pdf"):
				f = (file_path + '/' + filename)
				read_pdf = PyPDF2.PdfFileReader(f)
				page = read_pdf.getPage(0)
				page_content = page.extractText()
				lines = page_content.replace(',', ' ')
				list1.append(lines)

		scores={}
		query = request.POST["query"]
		original = query
		#checking if the query starts with double quotes(exact match)
		if query.startswith('"'):
			op='and'
		else:
			op='or'

		query=re.sub(r'[#+?!"/@$,]',' ',query)
		query=word_tokenize_all([query])

		i = 0
		for d in D:
			#calculating score for each document
			if request.POST["radio"] == "1":
				sc = score(query[0], i, d, op, D)
			elif request.POST["radio"] == "0":
				sc = cosineScore(query[0], d, op, i)
			#storing score in the dictionary only if the score > 0
			if sc != 0:
				scores[i] = sc
			i+=1

		result = []
		docId  = []
		if len(scores)==0:
			print('No Results found')
			result.append(['',-1,'No Results found'])
		else:
			#getting top 5 documents matching the query
			top_docs=sorted(scores, key=scores.get, reverse=True)[:]

			rank=1
			for id in top_docs:
				print("rank:",rank,'score',scores[id])
				print(list1[id].strip())
				temp = list1[id].strip()
				result.append([list1[id].strip(),id,temp[0:100]])
				print("-----------------------------------------------")
				rank+=1
		if request.POST["radio"] == "1":
			return render(request,'apps/searchresults.html', context= {"query":original,"num":len(scores), "results": result,"A":D, "results": result,"D":scores})

		elif request.POST["radio"] == "0":
			return render(request,'apps/Cossearchresults.html', context= {"query":original,"num":len(scores),"results": result})
	return render(request,'apps/home.html')
