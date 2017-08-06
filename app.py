#coding:utf-8 
from flask import Flask,request,Response,make_response,render_template
from flask_cqlalchemy import CQLAlchemy
import pyspark
import os
import json
from cassandra.cluster import Cluster
from worC import evalAcc

from runservice import *

app = Flask(__name__)

@app.before_request
def before_request():
	global sess
	sess = Cluster(['127.0.0.1']).connect('IMG')
	sess.set_keyspace('final_pro')

#	upload self-introduction and process it into personality analysis
@app.route('/selfIntro',methods=['POST','GET'])
def selfIntro():
	f = request.files['file']
	name = request.form['filename'].split('.')[0]
	print name

	basic_path = './tmpMP3/'
	f.save(os.path.join(basic_path,request.form['filename']))

	path = basic_path + request.form['filename']
	profilePath = './profile.json'

	res=spe2tex(path)
	text=res2string(res)
	string2cha(text)
	final=cha2result(profilePath)

	final_dict = final['dict']
	final_string = final['string']

	p_dict = final_dict['Personality']
	v_dict = final_dict['Value']

	pre = sess.prepare("insert into user_test(name,eval_P,eval_V,score) VALUES(?,?,?,0.8)")
	sess.execute(pre,[name,p_dict,v_dict])
	
	return make_response(final_string)

#	process txt 
@app.route('/evalAcc',methods=['POST'])
def evalAccu():
	f = request.files['file']
	name = request.form['filename'].split('.')[0]
	print name

	basic_path = './tmpTXT/'
	f.save(os.path.join(basic_path,request.form['filename']))
	with open(basic_path+request.form['filename'],'r') as f:
		ans = f.read()

	score = evalAcc(ans)

	pre = sess.prepare("UPDATE user_test set score = ? where name = ?")
	sess.execute(pre,[score,name])

	return make_response('score:'+str(score)+'\n')

#	display personality
@app.route('/display/<name>/Personality',methods=['GET'])
def displayP(name):
	name = name
	option = "Personality"
	pre = sess.prepare("select *from user_test where name=?")
	rows = sess.execute(pre,[name])

	for t in rows:
		init_data = t.eval_p

	data = pretreatData(init_data)

	return render_template('display2.html',option=option,data=json.dumps(data))

#	display value
@app.route('/display/<name>/Value',methods=['GET'])
def displayV(name):
	name = name
	option = "Value"
	pre = sess.prepare("select *from user_test where name=?")
	rows = sess.execute(pre,[name])
	for t in rows:
		init_data = t.eval_v
	data = pretreatData(init_data)

	return render_template('display3.html',option=option,data=json.dumps(data))

#	select from database
@app.route('/select1/<name>',methods=['GET'])
def select1(name):
	name = name
	prepared = sess.prepare('SELECT *FROM user_test where name=?')
	rows = sess.execute(prepared,[name])

	for user_row in rows:
		eval_p = user_row.eval_p
		eval_v = user_row.eval_v
		score = user_row.score
		print eval_p
		print eval_p,eval_v,score

	return render_template('display.html',name=name,result=1,score=score,eval_p=eval_p,eval_v=eval_v)

#	select from datbase/curl
@app.route('/select2/<name>',methods=['GET'])
def select2(name):
	name = name
	prepared = sess.prepare('SELECT NAME,tojson(eval_p),tojson(eval_v),score FROM user_test where name=?')
	rows = sess.execute(prepared,[name])
	for user_row in rows:
		eval_p = user_row.system_tojson_eval_p
		eval_v = user_row.system_tojson_eval_v
		score = user_row.score
	print 'eval_p:',eval_p
	return make_response('NAME:'+str(name)+'\nEVAL_P:'+(eval_p)+'\nEVAL_V:'+(eval_v)+'\nSCORE:'+str(score)+'\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)


