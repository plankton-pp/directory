# -- step 1
# update Ex_fiberloss_id
# insert into dataframe
# update date fame
# -- step 2
#find a_calcSpanLoss ,a_calcSpanLoss  Ex_fiberloss_record

import requests
from bs4 import BeautifulSoup
import json
import urllib3
from stat import S_ISDIR as isdir
import tarfile
import pprint
from multiprocessing import Pool,freeze_support

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from functools import partial
import pandas as pd
import datetime
from time import sleep

import db


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


def init_Ex_fiberloss_id():
    global Ex_fiberloss_id

def find_fbl(id,session,domain,ServerIP,dict_con_name):
    # init
    MaxfiberLength=-99
    a_calcSpanLoss=49.99
    z_calcSpanLoss=49.99

    count=0
    while(True):
        try:
            _url=f"{ServerIP}:8443/oms1350/data/npr/physicalConns/{id}/fiberCharacteristic"
            _res = session.get(_url, verify=False)
            _data=_res.json()
            conection_name=dict_con_name[id]
            for item in _data:
                if float(item['fiberLength'])>=MaxfiberLength:
                    MaxfiberLength=item['fiberLength']

                if ((item['fromLabel'] in conection_name) and (item['toLabel'] in conection_name) ):
                    a_calcSpanLoss=item['calcSpanLoss']
                    a_design=item['minSpanLoss']
                    a_from_label=item['fromLabel']
                    a_to_label=item['toLabel']
                    if(item['calcSpanLoss']=='NIL'):
                        a_calcSpanLoss=49.99

                else:
                    z_calcSpanLoss=item['calcSpanLoss']
                    z_design=item['minSpanLoss']
                    z_from_label=item['fromLabel']
                    z_to_label=item['toLabel']
                    if(item['calcSpanLoss']=='NIL'):
                        z_calcSpanLoss=49.99   

            return domain,id,MaxfiberLength,a_calcSpanLoss,z_calcSpanLoss,a_design,z_design,a_from_label,a_to_label,z_from_label,z_to_label
        except :
            if count>=10:
                return [id]
            sleep(20)
            pass
        

def main(ip,domain):
    # init
    global Ex_fiberloss_id
    global Ex_fiberloss_record
    domain=domain.lower()


    #--------------------------------------------------------------
    #--------------------login session step 1----------------------
    
    ServerIP=f'https://{ip}'
    url = f"{ServerIP}:8443/oms1350/data/npr/nodes"
    payload={}
    headers = {}
    session=requests.Session()
    session.trust_env = False
    #session.headers.update(headers)
    res = session.get(url, verify=False)
    # print(res.text)
    soup = BeautifulSoup(res.text, "html.parser")
    dt = soup.find("div",id='execution')
    #print(dt['value'])


 #--------------------login session step 2----------------------

    username='osphachar' # my username
    password='@qCA99NV693u'   # my password
    execution=dt['value']
    geolocation=''
    url=f"{ServerIP}/cas/login?username={username}&password={password}&execution={execution}&_eventId=submit&geolocation={geolocation}"
    headers = {
      'Content-Type': 'application/json'
    }
    session.headers.update(headers)
    res = session.post(url, verify=False)


    #-------------------------  get data   -----------------------
    # all physicalConns on domain

    url_pmdata=f'{ServerIP}:8443/oms1350/data/npr/physicalConns/'
    res = session.get(url_pmdata, verify=False)
    data=res.json()
    global id_fiber
    id_fiber={}
    for i in data:
        if 'LINEIN' in  i['guiLabel']:
            id=i['id']
            id_fiber[id]=i['guiLabel']

    # print(len(id_fiber))
    # print(id_fiber.keys())

    for i in id_fiber:
        Ex_fiberloss_id=Ex_fiberloss_id.append({
            'fiber_id':len(Ex_fiberloss_id)+1,
            'domain':domain,            
            'physicalconns':i,
            'conn_name':id_fiber[i],
            },ignore_index=True)


    for i in id_fiber:
        if id_fiber[i] in Ex_fiberloss_id.conn_name.tolist():
            Ex_fiberloss_id.loc[Ex_fiberloss_id['conn_name']==id_fiber[i],'physicalconns']=i
        
        else:
            Ex_fiberloss_id=Ex_fiberloss_id.append({
                'fiber_id':len(Ex_fiberloss_id)+1,
                'domain':domain,            
                'physicalconns':i,
                'conn_name':id_fiber[i],
                },ignore_index=True)
                

    for i in id_fiber:
        if i in Ex_fiberloss_id[Ex_fiberloss_id['domain']==domain]['physicalconns'].tolist():
            Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns']==i) & (Ex_fiberloss_id['domain']==domain) , 'conn_name']=id_fiber[i]
        
        else:
            try:
                fiber_id=len(Ex_fiberloss_id)+1
            except:
                fiber_id=1
            Ex_fiberloss_id=Ex_fiberloss_id.append({
                'fiber_id':fiber_id,
                'domain':domain,            
                'physicalconns':i,
                'conn_name':id_fiber[i],
                },ignore_index=True)





    with Pool(processes=5) as pool:
        results = pool.map(partial(find_fbl, session=session,domain=domain,ServerIP=ServerIP,dict_con_name=id_fiber), list(id_fiber.keys()))   
        # results = pool.map(partial(find_fbl, session=session,domain=domain,ServerIP=ServerIP,dict_con_name=id_fiber), list([693]))

    print(results)
    
    for e_conid in results:
        print(e_conid)
    results=list(filter(None, results))


    for e_conid in results:
        if type(e_conid) != tuple:
            print("ERROR physicalconns :",e_conid)
            continue
        domain=e_conid[0]
        physicalconns=e_conid[1]
        MaxfiberLength=e_conid[2]
        a_calcSpanLoss=e_conid[3]
        z_calcSpanLoss=e_conid[4]
        a_design=e_conid[5]
        z_design=e_conid[6]
        a_from_label=e_conid[7]
        a_to_label=e_conid[8]
        z_from_label=e_conid[9]
        z_to_label=e_conid[10]

        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'fiber_length' ] = MaxfiberLength
        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'a_design' ] = a_design
        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'z_design' ] = z_design
        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'a_from_label' ] = a_from_label
        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'a_to_label' ] = a_to_label
        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'z_from_label' ] = z_from_label
        Ex_fiberloss_id.loc[(Ex_fiberloss_id['physicalconns'] == physicalconns) & (Ex_fiberloss_id['domain'] == domain) , 'z_to_label' ] = z_to_label
        try:
            record_id=len(Ex_fiberloss_id)+1
        except:
            record_id=1
        Ex_fiberloss_record=Ex_fiberloss_record.append({
        'record_id': record_id,
        'domain': domain,
        'physicalconns': physicalconns,
        'date': datetime.date.today(),
        'a_calc_spanloss': a_calcSpanLoss,
        'z_calc_spanloss': z_calcSpanLoss
        },ignore_index=True)

    session.close()

if __name__=="__main__":
    freeze_support()
    global Ex_fiberloss_id
    global Ex_fiberloss_record

    try:
        Ex_fiberloss_id = pd.read_sql_table('ex_fiberloss_id', db.engine)
    except:
        cols_id= ['fiber_id','domain','physicalconns','conn_name','a_design','z_design','fiber_length']
        Ex_fiberloss_id=pd.DataFrame(columns=cols_id)
    

    try:
        Ex_fiberloss_record = pd.read_sql_table('ex_fiberloss_record', db.engine)
    except:
        cols_record= ['record_id','domain','physicalconns','date','a_calc_spanloss','z_calc_spanloss']
        Ex_fiberloss_record=pd.DataFrame(columns=cols_record)

    while(True):
        try:
            main('10.13.51.8','upper')
            break
        except:
            sleep(60)
            pass
    
    while(True):
        try:
            main('172.29.176.8','lower')
            break
        except:
            sleep(60)
            pass

    Ex_fiberloss_id=Ex_fiberloss_id.drop_duplicates(['domain','physicalconns'],keep= 'first')
    Ex_fiberloss_record=Ex_fiberloss_record.drop_duplicates(['domain','physicalconns','date'],keep= 'last')    

    Ex_fiberloss_id.to_sql('ex_fiberloss_id', db.engine, if_exists='replace', index = False)
    Ex_fiberloss_record.to_sql('ex_fiberloss_record', db.engine, if_exists='replace', index = False)

    # RE DATE
    Ex_fiberloss_id = pd.read_sql_table('ex_fiberloss_id', db.engine)
    Ex_fiberloss_record = pd.read_sql_table('ex_fiberloss_record', db.engine)

    Ex_fiberloss_id=Ex_fiberloss_id.drop_duplicates(['domain','physicalconns'],keep= 'first')
    Ex_fiberloss_record=Ex_fiberloss_record.drop_duplicates(['domain','physicalconns','date'],keep= 'last')

    Ex_fiberloss_id.to_sql('ex_fiberloss_id', db.engine, if_exists='replace', index = False)
    Ex_fiberloss_record.to_sql('ex_fiberloss_record', db.engine, if_exists='replace', index = False)

    Ex_fiberloss_id.to_csv('ex_fiberloss_id.csv',index=False)
    Ex_fiberloss_id.to_csv('ex_fiberloss_record.csv',index=False)




    # Test output
    # print(Ex_fiberloss_id.info())
    # print(Ex_fiberloss_record.info())

    # mv ex_fiberloss_id.csv /mnt/ssd/dataset/_rawdata/td_core/Dwdm
    # mv ex_fiberloss_record.csv /mnt/ssd/dataset/_rawdata/td_core/Dwdm


    # new_df = Ex_fiberloss_id.merge(Ex_fiberloss_record,how='inner',on=['domain','physicalconns'])
    # print(new_df)
    # new_df.to_csv('example_merge.csv',index=False)
    # mv example_merge.csv /mnt/ssd/dataset/_rawdata/td_core/Dwdm
