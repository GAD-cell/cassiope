import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.ensemble import RandomForestRegressor
from sklearn import linear_model
import statsmodels.api as sm
from math import*
import seaborn as sns


def read_csv(fileName):
    data = pd.read_csv(fileName)
    total_rows = len(data)  # Compter le nombre total de lignes avant filtrage
    del data['title']
    del data['arxiv_id']
    del data['corpusid']
    del data['venue']
    del data['font']
    del data["influentialcitationcount"]
    del data['year']
    citationcount=data["citationcount"]
    citationcount=citationcount[(data['sections'] >= 3) & (data['subsections'] >= 1)]
    del data["citationcount"]
    # Filtrer les lignes selon les critères spécifiés
    data = data[(data['sections'] >= 3) & (data['subsections'] >= 1)]
    retained_rows = len(data)  # Compter le nombre de lignes après filtrage

    # Afficher le nombre de lignes retenues par rapport au nombre total de lignes
    print(f"Nombre de lignes retenues: {retained_rows} sur {total_rows} lignes au total")
    return data,citationcount


def create_features(data):
    # Creating the new features as per the user's request
    data['referencecount_per_page'] = data['referencecount'] / data['pages']
    data['figures_tables_per_page'] = (data['figures'] + data['tables']) / data['pages']
    data['equations_per_page'] = data['equations'] / data['pages']
    data['subsections_per_page'] = data['subsections'] / data['pages']

    # Select the new features and the target variable
    features = data[['referencecount_per_page', 'figures_tables_per_page',
                     'equations_per_page', 'subsections_per_page']]
    return features
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
    rf_model = RandomForestRegressor(max_depth=5, min_samples_split=20, n_estimators=500,criterion="squared_error")
    rf_model.fit(X,y)
    print("Importance relative des features pour le nombre de citations : ",rf_model.feature_importances_)
    plt.figure(figsize=(20,6))
    plt.grid(True)
    plt.yticks(range(len(df.columns[:-1])), df.columns[:-1], fontsize=10)
    plt.xlabel("Importance relative des features pour le nombre de citations",fontsize=15)
    plt.ylabel("Features\n",fontsize=15)
    plt.barh(range(len(df.columns[:-1])), width=rf_model.feature_importances_, height=0.5)
    plt.show()
        
def linear_regression(X,y):
    # Ajuster le modèle de régression linéaire
    X = sm.add_constant(X)  # Ajouter une constante pour l'interception
    model = sm.OLS(y, X)
    results = model.fit()
    print(results.summary())

def correlation_matrix(df):
    plt.figure(figsize = (15,15))
    sns.heatmap(df.corr(method="pearson"), cmap = 'coolwarm',vmin=-1,vmax=1,center=0)
    plt.show()


if __name__=="__main__":
    data,citationcount = read_csv("../STATS.csv")
    #plot('content_references','citationcount',data)
    features = create_features(data)
    df = make_df(features,citationcount)
    #visualize_features(df)
    #randomForest(features,citationcount,df)
    #linear_regression(features,citationcount)
    correlation_matrix(df)
