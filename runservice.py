#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 03:22:16 2017

@author: geyi0530
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 02:26:05 2017

@author: geyi0530
"""

# encoding: UTF-8
import json
from os.path import join,dirname
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import PersonalityInsightsV3
from cassandra.cluster import Cluster
from json import *

DIRECTORY='/Users/apple/Documents/USTB/MITBigData/FinalPro/test_mp3/demo3.mp3'
DIRECTORY2='/Users/apple/Documents/USTB/MITBigData/FinalPro/profile.json'

##used to transform speech to text
#argument
#    directory -- path to file
#result
#   string -- json format answer, need further operation
def spe2tex(directory):
    speech_to_text = SpeechToTextV1(
                                    username='7a20510f-9402-456f-bc13-30caf57a2b56',
                                    password='iqRBHZjWIouq',
                                    x_watson_learning_opt_out=False
                                    )
    print 'spe2tex'
    with open(directory,'rb')as audio_file:
        return (json.dumps(speech_to_text.recognize(
                                                   audio_file,content_type='audio/mp3',timestamps=True,model='en-US_BroadbandModel',word_confidence=True
                                                   ),indent=2,encoding='UTF-8',ensure_ascii=False))
        
        
def res2string(res):
    sss=json.loads(res)
    final=''
    total=0
    count=0
    group=[]
    confG=[]
    for result in sss['results']:
        sentence=result['alternatives'][0]['transcript']
        confidence=result['alternatives'][0]['confidence']
        #print(sentence)
        #print(confidence)
        final+=sentence
        total+=confidence
        count+=1
        group.append(sentence)
        confG.append(confidence)
    avg=total/count
    #print final,avg
    f=open("sentence.txt", "w")
    f.write(final)      
    return final  #only return to that string (one passage)

def string2cha(text):
    text+='''
    ,
    content_type='text/plain',
    content_language=None,
    accept='application/json',
    accept_language=None,
    raw_scores=False,
    consumption_preferences=False,
    csv_headers=False
    '''
    f=open('profile.json','w')
    f.write(text)
    f.close()

def cha2result(directory2):
    print 'char2result'
    personality_insights = PersonalityInsightsV3(
                                                 version='2016-10-20',
                                                 username='39b8b2c3-4c89-4744-9b13-5a2c819e336a',
                                                 password='aqX0fmoCPtMA'
                                                 )  
    
    with open(directory2) as profile_json:
         profile = personality_insights.profile(
                                                profile_json.read(), content_type='text/plain',
                                                raw_scores=True, consumption_preferences=True)
    character_text=json.dumps(profile, indent=2)

    sss=json.loads(character_text)
    # print 'type of sss is:',type(sss)
    p_dict={}
    v_dict={}

    final='Personality:'
    # final
    # print 'type for sss.values is:',type(sss['values'])
    for result in sss['values']:
        # print 'type for result.name is:',type(result['name'])
        character1=result['name']
        percent1=result['percentile']
        final+="\n"+character1
        final+="\n"+str(percent1)

        v_dict.update({character1:percent1})

    final+="\n\n"+"Value:"

    for result in sss['personality']:
        character2=result['name']
        percent2=result['percentile']
        final+="\n"+character2
        final+="\n"+str(percent2)

        p_dict.update({character2:percent2})

    final_dict = {'Personality':p_dict,'Value':v_dict}
    return {'string':final,'dict':final_dict}

def fetchTop5(dic):
    tmp = sorted(dic.iteritems(), key=lambda d:d[1], reverse = True)
    result={}
    for k,v in enumerate(tmp):
        if k==5:
            break
        result.update({v[0]:dic[v[0]]})
    return result

def pretreatData(input):
    tmp = {}
    for t in input:
        tmp.update({t.encode('utf-8'):input[t]})
    return fetchTop5(tmp)

# data={'1':2,'2':3,'3':4}
# p= json.dumps(data)
# print p
# print 
# res=spe2tex(DIRECTORY)
# text=res2string(res)
# string2cha(text)  #update json
# final=cha2result(DIRECTORY2)

# p_dict = final['dict']['Personality']
# v_dict = final['dict']['Value']

# sess = Cluster(['127.0.0.1']).connect('IMG')
# sess.set_keyspace('final_pro')

# pre = sess.prepare("insert into user_test(name,eval_P,eval_V,score) VALUES('TEST3',?,?,0.8)")
# sess.execute(pre,[p_dict,v_dict])


# pre = sess.prepare("select *from user_test where name=?")
# rows = sess.execute(pre,["TEST3"])

# tmp_eval_v = rows[0].eval_v

# print pretreatData(tmp_eval_v)
# prepared = sess.prepare('SELECT NAME,tojson(eval_p),tojson(eval_v),score FROM user_test where name=?')
# rows = sess.execute(prepared,['Fan'])
# for user_row in rows:
#     print user_row
#     eval_p = user_row.system_tojson_eval_p
#     print type(eval_p)
#     score = user_row.score
# print json.dumps(eval_p)

