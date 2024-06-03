import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn import linear_model
import statsmodels.api as sm
from math import*
import seaborn as sns
import csv
import ast

from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error


def read_csv(fileName):
    data = pd.read_csv(fileName)
    del data['filename']
    del data['title']
    del data['arxiv_id']
    del data['corpusid']
    del data['venue']
    del data['font']
    del data["influentialcitationcount"]
    del data['year']
    del data['authors']
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

#estimation de l'importance relative de chacunes des features
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

#calcul du nomnbre de citations par topic pour évaluer leurs popularités
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

#calcul des modèles régressifs
def gen_regressor_model():


    data,citationcount = read_csv('/home/gad/Documents/cassiope/cassiope/util/paperStats/STATS.csv')
    data['citationcount']=citationcount

    data_sorted = data.sort_values(by='citationcount', ascending=False)

    n = floor(len(data['citationcount'])*0.1)
    data_sorted_top_n = data_sorted.head(n)
    statistiques = data_sorted_top_n.describe().transpose()  
    print(statistiques)


    features = data.columns.tolist()
    target = 'citationcount'  # Remplacer par le nom de votre variable cible


    regression_results = {}

    for feature in features:

        if feature != target:
            X = data[[feature]]
            y = data[target]
            

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            

            pipeline = Pipeline([
                ('poly', PolynomialFeatures()),
                ('model', LinearRegression())
            ])
            
            param_grid = [
                {
                    'poly__degree': [1],  # Linear
                    'model': [LinearRegression()]
                },
                {
                    'poly__degree': [2, 3],  # Polynomial
                    'model': [LinearRegression()]
                },
                {
                    'poly': [PolynomialFeatures(degree=1)],  # Gaussian Process Regressor
                    'model': [GaussianProcessRegressor()]
                }
            ]
            
            # test sur l'ensemble des modèles de régression
            grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='neg_mean_squared_error')
            grid_search.fit(X_train, y_train)
            
            # Meilleur modèle et prédictions
            best_model = grid_search.best_estimator_
            y_pred = best_model.predict(X_test)
            
            
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Stockage résultat
            regression_results[feature] = {
                'best_model': best_model,
                'rmse': rmse,
                'best_params': grid_search.best_params_
            }

    for feature, result in regression_results.items():
        print(f"Feature: {feature}")
        print(f"  Best Model: {result['best_model']}")
        print(f"  RMSE: {result['rmse']}")
        print(f"  Best Parameters: {result['best_params']}")
        print()


    return regression_results

#prediction par régression
def citationcount_predict():
    regression_results = gen_regressor_model()

    new_data = pd.read_csv('/home/gad/Documents/cassiope/cassiope/util/paperStats/STATS_1.csv')
    intermediate_predictions = pd.DataFrame()

    for feature, result in regression_results.items():
        best_model = result['best_model']
        

        X_new = new_data[[feature]]
        

        y_pred = best_model.predict(X_new)
        
        intermediate_predictions[feature] = y_pred


    final_predictions = intermediate_predictions.mean(axis=1)
    final_predictions=floor(float(final_predictions.item()))
    print('prediction :' +str(final_predictions))
    return final_predictions

#prédiction par foret aléatoire
def random_forest():
    data,citationcount = read_csv('/home/gad/Documents/cassiope/cassiope/util/paperStats/STATS.csv')
    data['citationcount']=citationcount

    X = data.drop(columns=['citationcount']) 
    y = data['citationcount']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialiser le modèle de forêt aléatoire
    random_forest = RandomForestRegressor(n_estimators=1000, random_state=42)  # Nombre d'arbres = 100
    random_forest.fit(X_train, y_train)
    y_pred = random_forest.predict(X_test)

    # Calculer l'erreur quadratique moyenne (RMSE)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    erreur_percent = (mae / y_test.mean()) * 100
    print("erreur",erreur_percent )
    print("RMSE:", rmse)

if __name__=="__main__":
    #data,citationcount = read_csv("../STATS.csv")
    #plot('content_references','citationcount',data)
    #df = make_df(data,citationcount)
    #visualize_features(df)
    
    #randomForest(data,citationcount,df)
    #linear_regression(data,citationcount)
    #correlation_matrix(df)
    
    gen_citationcount_per_topic()

    #gen_regressor_model()
    #citationcount_predict()
    #random_forest()