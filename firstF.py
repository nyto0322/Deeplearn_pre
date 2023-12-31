import pandas as pd
from datetime import datetime,timedelta
import numpy as np 
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

format_pattern = '%Y-%m-%d-%H:%M:%S'

def timeDuplicated(df):
    df_dup = df.duplicated(df.columns.values[1])
    arrc = df_dup[df_dup.values == True].index.values
    for i in arrc:
        tempS = df.iloc[i-1].copy()
        for j in df.columns.values:   
            try:
                tempS[j] = (df.iloc[i-1][j]+df.iloc[i][j])/2.0
            except:
                pass
        df.iloc[i-1] = tempS
    dfD = df.drop(df.index[arrc])
    return dfD


def timeInsert(df):

    dL = np.array(df).tolist()
    dLC = dL.copy()

    preTime = datetime.strptime(dL[0][1], format_pattern)
    curTime = datetime.strptime(dL[0][1], format_pattern)
    interval = timedelta(seconds=1)

    net=0
    for i in range(0, len(dL)):

        preTime = curTime
        curTime = datetime.strptime(dL[i][1], format_pattern)

        insTime = preTime + interval
        while insTime < curTime:
            tempS = dL[0].copy()
            net=net+1
            precent = (insTime - preTime)/(curTime - preTime)
            tempS[1] = insTime.strftime("%Y-%m-%d-%H:%M:%S")
            for j in range(1,len(df.columns.values)):  

                try:
                    tempS[j] = (dL[i][j]-dL[i-1][j])*precent+dL[i-1][j]
                except:
                    pass
            dLC.insert(i+net-1,tempS)
            insTime += interval

    df = pd.DataFrame(dLC,columns=df.columns)

    return df






def rep_del_cat(data,name):
    # data = pd.read_csv('test_ori.csv')
    # data[data == '\\N'] = np.nan 
    # data[data == '8388610'] = np.nan 
    # data.to_csv("origNa111n"+'111') 



    
    data.replace("\\N",np.nan,inplace = True)
    data.replace("1677720",np.nan,inplace = True)
    data.replace("8388610",np.nan,inplace = True)
    data.replace(1677720,np.nan,inplace = True)
    data.replace(8388610,np.nan,inplace = True)
    data.replace(-1,np.nan,inplace = True)
    data.replace(-0.1,np.nan,inplace = True)

    data = data.loc[:, ~(data == 0).all(axis=0)]
    for i in data.loc[:, (data == 0).all(axis=0)].columns.values:
        del data[i]

    for i in data.columns:
        if data[i].isnull().all() == True:
            del data[i]

    data.astype('float64')
    for i in data.columns:
        try:
            if data[i].var() == 0:
                del data[i]
        except:
            pass



    for i in data.columns:
        if (data[i].isnull().sum())/data[i].shape[0] > 0.5:
            del data[i]


    for i in range(0, len(data.columns)):
        kr = False
        harr = data.iloc[:,i].tolist()
        
        index = -1
        for j in range(0, len(harr)):
            if str(harr[j]) == 'nan':
                if kr == False:
                    index = j
                    kr = True
            else:
                if kr == True:
                    if index != 0:
                        for k in range(index,j):
                            #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",k)
                            #print(harr[j],harr[index-1])
                            harr[k]=((float(harr[j])-float(harr[index-1]))/(j-index+1))*(k-index+1)+float(harr[index-1])


                    else:
                        for k in range(index,j):
                            harr[k]=harr[j]
                    kr = False
            if j == len(harr)-1 and kr == True:
                for k in range(index,j+1):
                    harr[k]=harr[index-1]           
        data.iloc[:,i] = pd.DataFrame(harr)
    
    res_heng = pd.concat([data.reset_index()
                        ,data.iloc[30:,data.columns.tolist().index('MAP')].reset_index()
                        ,data.iloc[60:,data.columns.tolist().index('MAP')].reset_index()
                        ,data.iloc[120:,data.columns.tolist().index('MAP')].reset_index()
                        ,data.iloc[300:,data.columns.tolist().index('MAP')].reset_index()
                        ,data.iloc[600:,data.columns.tolist().index('MAP')].reset_index()], axis=1)



    
    res_heng.astype('float64')
    res_heng = res_heng.loc[:, ~(res_heng == 0).all(axis=0)]
    for i in res_heng.columns:
        try:
            if float(res_heng[i]).var() == 0:
                res_heng.drop(i)
        except:
            pass
    #del data["Unnamed: 0"]
        


    try:
        del res_heng["index"]
    except:
        pass    
    try:
        del res_heng["Unnamed: 0.1"]
    except:
        pass    
    try:
        del res_heng["Unnamed: 0"]
    except:
        pass

    res_heng.to_csv("res/Id"+str(name)) 





class Nyto(object): 
    def load(self,name):
        self.name = name
        

        f = Path('D:\\Project\\VSCode\\Python\\deeplearn\\train\\'+name+'\\'.strip())

        keyword = '*OHMEDA*'.strip()
        self.dataOHMEDA = pd.read_csv(list(f.rglob(keyword))[0])
        keyword = '*LIDCO*'.strip()
        self.dataLIDCO = pd.read_csv(list(f.rglob(keyword))[0])
        keyword = '*NONIN*'.strip()
        self.dataNONIN = pd.read_csv(list(f.rglob(keyword))[0])
        keyword = '*PHILIPS*'.strip()
        self.dataPHILIPS = pd.read_csv(list(f.rglob(keyword))[0])       



    def add(self):
        self.dataOHMEDA = timeDuplicated(self.dataOHMEDA)
        self.dataLIDCO = timeDuplicated(self.dataLIDCO)
        self.dataNONIN = timeDuplicated(self.dataNONIN)
        self.dataPHILIPS = timeDuplicated(self.dataPHILIPS)

        self.dataOHMEDA = timeInsert(self.dataOHMEDA)
        self.dataLIDCO = timeInsert(self.dataLIDCO)
        self.dataNONIN = timeInsert(self.dataNONIN)
        self.dataPHILIPS = timeInsert(self.dataPHILIPS)
        

        time1 = datetime.strptime(self.dataOHMEDA.iloc[0,1], format_pattern)
        time2 = datetime.strptime(self.dataLIDCO.iloc[0,1], format_pattern)
        time3 = datetime.strptime(self.dataNONIN.iloc[0,1], format_pattern)
        time4 = datetime.strptime(self.dataPHILIPS.iloc[0,1], format_pattern)
        self.timeHJM = max(time1,time2,time3,time4).strftime("%Y-%m-%d-%H:%M:%S")
        
        time1 = datetime.strptime(self.dataOHMEDA.iloc[len(self.dataOHMEDA)-1,1], format_pattern)
        time2 = datetime.strptime(self.dataLIDCO.iloc[len(self.dataLIDCO)-1,1], format_pattern)
        time3 = datetime.strptime(self.dataNONIN.iloc[len(self.dataNONIN)-1,1], format_pattern)
        time4 = datetime.strptime(self.dataPHILIPS.iloc[len(self.dataPHILIPS)-1,1], format_pattern)
        self.timeOWR = min(time1,time2,time3,time4).strftime("%Y-%m-%d-%H:%M:%S")

        self.dataOHMEDA = self.dataOHMEDA.iloc[self.dataOHMEDA[self.dataOHMEDA[self.dataOHMEDA.columns[1]] == self.timeHJM].index.values[0]
                                     :self.dataOHMEDA[self.dataOHMEDA[self.dataOHMEDA.columns[1]] == self.timeOWR].index.values[0],:]
        self.dataLIDCO = self.dataLIDCO.iloc[self.dataLIDCO[self.dataLIDCO[self.dataLIDCO.columns[1]] == self.timeHJM].index.values[0]
                                   :self.dataLIDCO[self.dataLIDCO[self.dataLIDCO.columns[1]] == self.timeOWR].index.values[0],:]
        self.dataNONIN = self.dataNONIN.iloc[self.dataNONIN[self.dataNONIN[self.dataNONIN.columns[1]] == self.timeHJM].index.values[0]
                                   :self.dataNONIN[self.dataNONIN[self.dataNONIN.columns[1]] == self.timeOWR].index.values[0],:]
        self.dataPHILIPS = self.dataPHILIPS.iloc[self.dataPHILIPS[self.dataPHILIPS[self.dataPHILIPS.columns[1]] == self.timeHJM].index.values[0]
                                       :self.dataPHILIPS[self.dataPHILIPS[self.dataPHILIPS.columns[1]] == self.timeOWR].index.values[0],:]



        res_heng = pd.concat([self.dataOHMEDA.reset_index(),self.dataLIDCO.reset_index(),self.dataNONIN.reset_index(),self.dataPHILIPS.reset_index()], axis=1)
        del res_heng["index"]
        del res_heng["id"]
        del res_heng["\\N"]
        #res_heng.to_csv("origId"+str(self.name)) 
        rep_del_cat(res_heng,self.name)
        





for i in range(1,19):
    print(i)
    nyto = Nyto()
    nyto.load(str(i))
    nyto.add()


data = pd.read_csv('res\Id'+str(1))
pub = data.columns

for i in range(1,19):
    data = pd.read_csv('res\Id'+str(i)+'.csv')
    del data['Unnamed: 0']
    pub = set(pub).intersection(set(data.columns))

    #data.to_csv("Id"+str(i)+'.csv')
for i in range(1,19):
    data = pd.read_csv('res\Id'+str(i)+'.csv')
    data = data[list(pub)]

    data.to_csv("finId"+str(i)+".csv")
    

