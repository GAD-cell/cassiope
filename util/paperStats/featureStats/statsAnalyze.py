import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.ensemble import RandomForestRegressor
from sklearn import linear_model
import statsmodels.api as sm
from math import*
import seaborn as sns
import csv
import ast

def read_csv(fileName):
    data = pd.read_csv(fileName)
    del data['title']
    del data['arxiv_id']
    del data['corpusid']
    del data['venue']
    del data['font']
    del data["influentialcitationcount"]
    del data['year']
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

def randomForest(X,y,df):
    #tree_model = tree.DecisionTreeRegressor(max_depth=10,random_state=None)
    #tree_model.fit(X,y)
    rf_model = RandomForestRegressor(max_depth=5, min_samples_split=20, n_estimators=500,criterion="squared_error")
    rf_model.fit(X,y)
    #log10_imp=[log10(e) for e in rf_model.feature_importances_]
    print("Importance relative des features: ",rf_model.feature_importances_)
    plt.figure(figsize=(10,7))
    plt.grid(True)
    plt.yticks(range(11+1,1,-1),df.columns[:-1],fontsize=20)
    plt.xlabel("Importance relative des features",fontsize=15)
    plt.ylabel("Features\n",fontsize=20)
    plt.barh(range(11+1,1,-1),width=rf_model.feature_importances_,height=0.5)
    plt.show()
        
def linear_regression(X,y):
    del X["paragraphs"]
    del X["subsections"]
    del X["subsubsections"]
    del X["words"]
    del X["figures"]
    model = sm.OLS(y, X)
    results = model.fit()
    print(results.summary())

def correlation_matrix(df):
    plt.figure(figsize = (10,8))
    sns.heatmap(df.corr(method="pearson"), cmap = 'coolwarm',vmin=-1,vmax=1,center=0)
    plt.show()

def gen_citationcount_per_topic():
    bertopic_df=pd.read_csv('/home/gad/Documents/cassiope/cassiope/util/topicModeling/bertopic/BERTopic_modified.csv')
    stat_df = pd.read_csv('/home/gad/Documents/cassiope/cassiope/util/paperStats/STATS.csv')
    citationcount_per_topic = []
    bertopic_df["Representative_Docs"]=bertopic_df["Representative_Docs"].apply(ast.literal_eval)
    for docs in bertopic_df["Representative_Docs"]:
        count=0
        for i in range(3):
            for filename in stat_df["filename"]:
                if docs[i]==filename:
                    row = stat_df[stat_df['filename'] == filename]
                    count += int(row["citationcount"].values[0])
        citationcount_per_topic.append(count)
    bertopic_df["citationcount"]=citationcount_per_topic
    bertopic_df.to_csv('/home/gad/Documents/cassiope/cassiope/util/paperStats/STATS_topic.csv', index=False)
    return citationcount_per_topic

if __name__=="__main__":
    #data,citationcount = read_csv("../STATS.csv")
    #plot('content_references','citationcount',data)
    #df = make_df(data,citationcount)
    #visualize_features(df)
    #randomForest(data,citationcount,df)
    #linear_regression(data,citationcount)
    #correlation_matrix(df)
    gen_citationcount_per_topic()