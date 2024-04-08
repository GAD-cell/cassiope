import csv
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.ensemble import RandomForestRegressor
from math import*

def read_csv(fileName):
    data = pd.read_csv(fileName)
    del data['title']
    del data['arxiv_id']
    del data['corpusid']
    del data['venue']
    del data['font']
    citationcount=data["citationcount"]
    del data["citationcount"]
    return data,citationcount

def make_df(X,y):
    df1 = pd.DataFrame(data=X)
    df2=pd.DataFrame(data=y,columns=['citationcount'])
    df=pd.concat([df1,df2],axis=1)
    df.head(10)
    print(df)
    return df

def plot(x_name,y_name,data):
    x=data[x_name]
    y=data[y_name]
    plt.plot(x,y,"ob")

    plt.show()

def visualize_features(df):
    with plt.style.context(('fivethirtyeight')):
        for i,col in enumerate(df.columns[:-1]):
            plt.figure(figsize=(6,4))
            plt.grid(True)
            plt.xlabel('Feature:'+col,fontsize=12)
            plt.ylabel('Output: citationcount',fontsize=12)
            plt.hist(df[col],alpha=0.6,facecolor='g')
            plt.savefig("./figures/"+col)

def regression(X,y,df):
    #tree_model = tree.DecisionTreeRegressor(max_depth=10,random_state=None)
    #tree_model.fit(X,y)
    rf_model = RandomForestRegressor(max_depth=5, min_samples_split=5, n_estimators=500)
    rf_model.fit(X,y)
    #log10_imp=[log10(e) for e in rf_model.feature_importances_]
    print("Importance relative des features: ",rf_model.feature_importances_)
    plt.figure(figsize=(10,7))
    plt.grid(True)
    plt.yticks(range(13+1,1,-1),df.columns[:-1],fontsize=20)
    plt.xlabel("Importance relative des features",fontsize=15)
    plt.ylabel("Features\n",fontsize=20)
    plt.barh(range(13+1,1,-1),width=rf_model.feature_importances_,height=0.5)
    plt.show()
        


if __name__=="__main__":
    data,citationcount = read_csv("./STATS.csv")
    #plot('content_references','citationcount',data)
    df = make_df(data,citationcount)
    #visualize_features(df)
    regression(data,citationcount,df)