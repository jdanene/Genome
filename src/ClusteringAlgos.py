from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.spatial.distance import cdist
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import pairwise_distances
from ExtractData import ExtractData
from BagofWords import BagOfWords
import os, sys
from sklearn.metrics import silhouette_score
from scipy.sparse import csr_matrix
import pickle


class PCA:
    '''Place holder for PCA'''
    def __init__(self):
        pass


class ElbowMethod(object):
    """
    The optimal number of clusters can be defined as follow:

    Step 1: Compute clustering algorithm (e.g., k-means clustering) for different values of k. For instance, by varying k from 1 to 10 clusters
    Step 2: For each k, calculate the total within-cluster sum of square (wss)
    Step 3: Plot the curve of wss according to the number of clusters k.
    Step 4: The location of a bend (knee) in the plot is generally considered as an indicator of the appropriate number of clusters.

    Parameters:

    start (int): the starting k of the iteration

    end (int) = the ending k of the iteration 

    steps (int) : number of  steps to take each iteration

    kmodels (dict<k,KMeans>) = dict of sklearn cluster objects with key corresponding to cluster number. 

    distortions ([list-of numbers]): The numbers are the kmeans distortions from the cases.

    note (str) : Note to put on the name of saved img file

    graph_note (str) : Note to put on title of graph
    """
    def __init__(self, DATA, end = 10,steps = 5, start = 5, note= "",graph_note=""):
        super(ElbowMethod, self).__init__()
        self.end = end
        self.kmodels = dict()
        self.BASE_PATH  = DATA.BASE_PATH
        self.start = start
        self.steps = steps
        self.distortions = []
        self.file_note = note
        self.graph_note = graph_note
        self.silhouette_scores = []

    def plot_distortion(self, distortion_list, file_note,K,graph_note):
        self.savefig = os.path.join(self.BASE_PATH,"figures",file_note+"_km.png")
        # Plot the elbow 
        plt.plot(K, distortion_list, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Distortion')
        plt.title(graph_note)
        plt.savefig(self.savefig, bbox_inches='tight')
        plt.show()


    def run(self, X_data_matrix):
        # collect k-means clustering over different cluster sizes. 
        K = range(self.start,self.end,self.steps)
        for k in K:
            kmeanModel = KMeans(n_clusters=k, init = 'k-means++').fit(X_data_matrix)
            kmeanModel.fit(X_data_matrix)
            label = kmeanModel.labels_
            #Sum of square between each point and its nearest cluster
            self.distortions.append(kmeanModel.inertia_)
            self.kmodels[k]= kmeanModel
            self.silhouette_scores.append(silhouette_score(X_data_matrix, label, metric='euclidean'))
            print("k-mean perc finish: ","{:.0%}".format(k/self.end),"\r",end=" ", flush=True)
        
        #Graph data
        self.plot_distortion(self.distortions, self.file_note, K, "Elbow Method: "+self.graph_note)
        self.plot_distortion(self.silhouette_scores,"silo"+self.file_note, K, "Silhouette Method: "+self.graph_note)
        #Save data to pickle
        pickle.dump(self.kmodels, open(os.path.join(self.BASE_PATH,"data",self.file_note+"_kmean.pkl"), 'wb'))









