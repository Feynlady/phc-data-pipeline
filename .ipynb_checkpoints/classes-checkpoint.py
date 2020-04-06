import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from methods import combine
from methods import pre
from methods import fs
from methods import feda
from methods import drp
from inspect import getmembers
import time

    
class tuning:
    def __init__(self, space, iterations=100, scoring = 'r2', cv=3, jobs = -2):
        self.space = space
        self.iterations = iterations
        self.scoring = scoring
        self.cv = cv
        self.jobs = jobs
        
class drug:
    
    def __init__(self, name, ge, dr):
        self.name = name
        self.ge = pd.concat(ge, sort = False)
        self.dr = pd.concat(dr, sort = False)
        self.data = pd.DataFrame()
        
    def pre(self, p = 0.01, t=4):
        self.data = pre(self.ge, p, t)
        del self.ge
        
    def combine(self, metric='AUC_IC50'):
        data = {}
        self.metric = metric
        if not self.data.empty:
            ge = self.data
        else:
            ge = self.ge
        
        for ele in ge.index.levels[0]:
            data[ele] = combine(ge.loc[ele], self.dr.loc[ele], self.name, metric=metric)
        
        del self.dr
        if 'ge' in self.__dict__:
            del self.ge
    
        self.data = pd.concat(data, sort = False).fillna(0)
    
    def split(self, test=None):
        X_train, X_test, y_train, y_test = train_test_split(self.data.drop(self.metric, axis=1), self.data[self.metric], stratify = self.data.index.get_level_values(0), test_size = test)
        
        self.X = {'train': X_train.index, 'test': X_test.index}
        self.y = {'train': y_train.index, 'test': y_test.index}
    
    def get(self, data, split):
        if data == 'X':
            return self.data.loc[self.X[split]].drop(self.metric, axis = 1)
        elif data =='y':
            return self.data.loc[self.y[split]][self.metric]
        
        
    def fs(self, model, n=0, tuning=None):
        X_train, X_test, var = fs(model, self.get('X', 'train'), self.get('X', 'test'), self.get('y', 'train'), n=n, tuning=tuning) 
        train_index = self.data.loc[self.X['train']].keys()
        test_index = self.data.loc[self.X['test']].keys()
        self.X['fs_train'] = pd.DataFrame(X_train, index = train_index)
        self.X['fs_test'] = pd.DataFrame(X_test, index = test_index)
    
    def feda(self):
        train_domains = []
        test_domains = []
        train = 'train'
        test = 'test'
        
        if 'fs_train' in self.X.keys():
            train = 'fs_'+train
            test = 'fs_'+test
        
        X_train = self.X[train]
        X_test = self.X[test]
        
        for i in self.data.index.levels[0]:
            if i in self.data.index:
                train_domains.append(X_train.loc[i].to_numpy())
                test_domains.append(X_test.loc[i].to_numpy())
            
            
        self.X[train] = feda(train_domains)
        self.X[test] = feda(test_domains)
        
    def train(self, model, tuning=None):
        train = 'train'
        if 'fs_train' in self.X.keys():
            train = 'fs_'+train
        
        self.model = drp(model, self.X[train], self.y['train'], tuning=tuning)
        
    def predict(self, X = pd.DataFrame(), y = pd.DataFrame(), metrics = None):
        if X.empty and 'fs_test' in self.X.keys():
            X = self.X['fs_test']
        elif 'fs_test' not in self.X.keys():
            X = self.X['test']
        ypred = self.model.predict(X)
        self.y['predicted'] = ypred
        return ypred
    
    def metrics(self, arr: list) -> dict:
        if 'predicted' not in self.y.keys():
            self.predict()
        scores = {}
        for metric in arr:
            scores[metric.__name__] = metric(self.y['test'], self.y['predicted'])
        self.scores = scores
        return scores
    
    def to_json(self):

        attributes = {k:v for (k, v) in getmembers(self) if not k.startswith('__') and not callable(v)}
        for k,v in attributes.items():
            print(k)
            print(type(v))
            
            
            
    
        
class tuning:
    def __init__(self, space, iterations=100, scoring = 'r2', cv=3, jobs = -2):
        self.space = space
        self.iterations = iterations
        self.scoring = scoring
        self.cv = cv
        self.jobs = jobs 
        
