from pyspark import SparkContext, SparkConf
from pyspark import *
import os,shutil


def evalAcc(ansUploaded):
	count=""
	ans="AAAAA"

	for i in range(5):
		if ansUploaded[i]==ans[i]:
			count+="1 "
	print 'count:',count
	print ansUploaded
	with open("./word.txt",'w') as f:
		f.write(count)

	score = int(wordCount()["1"])*1.0/len(ans)
	return score


def wordCount():
	outputFile="./word2"
	inputFile="./word.txt"
	dic = {}
	if os.path.isdir(outputFile):
		shutil.rmtree(outputFile)
	try:
		sc.stop()
	except:
		pass
	sc = SparkContext('local', 'wordcount')
	text_file = sc.textFile(inputFile)
	counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a+b)
	counts.saveAsTextFile(outputFile)

	sc.stop()

	with open('./word2/part-00000','r') as f:
		t = f.read()

	rows = t.split('\n')
	for row in rows:
		if len(row)==0:
			break
		word = row.split('\'')[1]
		count = row.split(', ')[-1].split(')')[0]
		dic.update({word:count})
	return dic
# dic=wordCount()
# print dic


# with open('./word.txt','r') as f:
# 	print f.read()
# print evalAcc("ABCAA")