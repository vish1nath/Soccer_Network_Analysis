# -*- coding: utf-8 -*-

import pandas as pd
import collections
import copy
import math
#import networkx as nx

df = pd.DataFrame.from_csv('./arg-ger-2014.csv', sep=',')

print df

#G = nx.DiGraph()

playersMap = {1:'Iker Casillas', 2:'Raul Albiol', 3:'Gerard Pique',
4:'Carlos Marchena', 5:'Carlos Puyol', 6:'Andres Iniesta',
7:'David Villa', 8:'Xavi Hernandez', 9:'Fernando Torres',
10:'Cesc Fabregas', 11:'Joan Capdevila', 12:'Victor Valdes',
13:'Juan Mata', 14:'Xabi Alonso', 15:'Sergio Ramos',
16:'Sergio Busquets', 17:'Alvaro Arbeloa', 18:'Pedro Rodriguez',
19:'Fernando Llorente', 20:'Javi Martinez', 21:'David Silva',
22:'Jesus Navas', 23:'Jose Manuel Reina'}

allPlayers = {}

for index, row in df.iterrows():
  #print 'index ' + str(index)
  playerNum = int(index)
  allPlayers[playerNum] = {}
  for col in row.index.values:
    if col != '0':
      allPlayers[playerNum][int(col)] = int(row.ix[col])

print allPlayers
#print playersMap

def pagerank(prob,players,pageRank):
  for player in players:
    #calculate pagerank of player
    total = 0
    for p in players:
      if p != player:
        numerator = 0
        denominator = 0
        passesToPlayer = allPlayers[p]
        if player in passesToPlayer:
          numerator = passesToPlayer[player]
          for a in passesToPlayer:
            if a in playersMap:
              denominator += passesToPlayer[a]
          total += numerator * 1.0/denominator * pageRank[p]
    pageRank[player] = total
  return pageRank

def closeness(player,w):
  passesFromPlayer = allPlayers[player]
  totalFrom = 0
  for p in allPlayers:
    if p in passesFromPlayer and p != player:
      if passesFromPlayer[p] != 0:
        totalFrom += (1.0 / passesFromPlayer[p])
  
  totalTo = 0
  for p in allPlayers:
    if p != player:
      passesToPlayer = allPlayers[p]
      if player in passesToPlayer:
        if passesToPlayer[player] != 0:
          totalTo += (1.0 / passesToPlayer[player])
        
  return (10 / (w * totalFrom + (1.0 - w) * totalTo))
  
print '---------------------'
print 'Closeness'
for player in allPlayers:
  print str(round(closeness(player,0.5),3))
    
pageRank = {}
for a in allPlayers:
  pageRank[a] = 1
    
prob = 0.5
for i in range(1,11):
  pageRank = pagerank(prob,allPlayers,pageRank)
  
print '---------------------'
print 'Page Rank'
#print pageRank

for p in pageRank:
  print str(round(pageRank[p],3))
  
def getClusteringCoeff(player,data):
  outDegree = 0
  clusteringCoeff = 0
  if player in allPlayers:
    passesFromPlayer = allPlayers[player]
    for p1 in passesFromPlayer:
      if p1 != player:
        outDegree += passesFromPlayer[p1]
  for player1 in data:
    for player2 in data:
      if player1 != player and player2 != player:
        a = data[player1][player]
        b = data[player1][player2]
        c = data[player][player2]
        numerator = math.pow((a * b * c),(1/3.0))
        denominator = max(a,b,c)
        #numerator = (data[player2][str(player1)+'-'+str(player2)] * data[player][str(player2)+'-'+str(player1)] * data[player1][str(player2)+'-'+str(player)]) ** (1/3.0)
        #denominator = max(data[player2][str(player1)+'-'+str(player2)],data[player][str(player2)+'-'+str(player1)], data[player1][str(player2)+'-'+str(player)])
        #print 'a: ' + str(a) + ' b: ' + str(b) + ' c: ' + str(c) + ' Numerator: ' + str(numerator) + ' Denominator: ' + str(denominator)
        if denominator != 0:        
          clusteringCoeff += (numerator * 1.0 / denominator);
  #print 'coef ' + str(clusteringCoeff)
  #print 'outdegree ' + str(outDegree)
  #clusteringCoeff = clusteringCoeff/(outDegree * (outDegree - 1))
  clusteringCoeff = clusteringCoeff / 90.0
  return clusteringCoeff

print '---------------------'
print 'Clustering Coefficients'
for p in allPlayers:
  print str(round(getClusteringCoeff(p,allPlayers),3))
    
closeNessWeight = 0.2
pageRankWeight = 0.4
clusterWeight = 0.4

print '---------------------'
print 'Total Score'
score = {}
for p in allPlayers:
    score[p] = closeNessWeight * closeness(p,0.8)
    + pageRankWeight * pageRank[p] + clusterWeight * getClusteringCoeff(p,allPlayers)
    print str(round(score[p],3))
