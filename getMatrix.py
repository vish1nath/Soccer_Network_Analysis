
import pandas as pd
import collections
import copy
import math
#import networkx as nx

df = pd.DataFrame.from_csv('./ned-esp.txt', sep='\t')

#print df

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
  if int(row['Passer']) in allPlayers:
    allPlayers.get(int(row['Passer']))[int(row['Rec'])] += 1
  else:
    temp = collections.defaultdict(int)
    temp[int(row['Rec'])] += 1
    allPlayers[int(row['Passer'])] = temp

#print allPlayers
#print playersMap

def pagerank(prob,players,pageRank):
  for player in players:
    if player in playersMap:
      #calculate pagerank of player
      total = 0
      for p in playersMap:
        if p in allPlayers and p != player:
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
  for p in playersMap:
    if p in passesFromPlayer and p != player:
      if passesFromPlayer[p] != 0:
        totalFrom += (1.0 / passesFromPlayer[p])
  
  totalTo = 0
  for p in playersMap:
    if p in allPlayers and p != player:
      passesToPlayer = allPlayers[p]
      if player in passesToPlayer:
        if passesToPlayer[player] != 0:
          totalTo += (1.0 / passesToPlayer[player])
        
  return (10 / (w * totalFrom + (1.0 - w) * totalTo))
  
print '---------------------'
print 'Closeness'
for player in allPlayers:
  if player in playersMap:
    print str(playersMap[player]) + ' ' + str(closeness(player,0.5))
    
pageRank = {}
for a in allPlayers:
  if a in playersMap:
    pageRank[a] = 1
    
prob = 0.5
for i in range(1,11):
  pageRank = pagerank(prob,allPlayers,pageRank)
  
print '---------------------'
print 'Page Rank'
#print pageRank

for p in pageRank:
  print playersMap[p] + ' ' + str(pageRank[p])
  

passStrings = []
passString = []
for index, row in df.iterrows():
  if int(row['Passer']) > 0:
    if len(passString) == 0:
      passString.append(int(row['Passer']))
    if int(row['Rec']) > 0:
      passString.append(int(row['Rec']))
    else:
      passStrings.append(passString)
      passString = []
      
#print passStrings

def mapTemp(passString):
  betweenCounts = {}
  for i in range(len(passString)):
    for j in range(i+2,len(passString)):
      if passString[j] == passString[i]:
        break
      for k in range(i+1,j-1):
        if passString[k] in betweenCounts:
          betweenCounts[passString[k]][str(passString[i])+'-'+str(passString[j])] += 1
        else:
          tempDict = collections.defaultdict(int)
          tempDict[str(passString[i])+'-'+str(passString[j])] = 1
          betweenCounts[passString[k]] = tempDict
  return betweenCounts

#print mapTemp(passStrings[0])
finalBetweenCounts = {}
for passString in passStrings:
  betweenCounts = mapTemp(passString)
  for player in betweenCounts:
    if player in finalBetweenCounts:
      for key in betweenCounts[player]:
        finalBetweenCounts[player][key] += betweenCounts[player][key]
    else:
      tempDict = copy.deepcopy(betweenCounts[player])
      finalBetweenCounts[player] = tempDict
      
#print finalBetweenCounts

def betweenness(player):
  numerator = 0
  denominator = 0
  betweenValue = 0
  if player in finalBetweenCounts:
    betweenCounts = finalBetweenCounts[player]
    for path in betweenCounts:
      numerator = betweenCounts[path]
      for p in finalBetweenCounts:
        tempBetweenCounts = finalBetweenCounts[p]
        denominator += tempBetweenCounts[path]
      betweenValue += (numerator * 1.0) / denominator
  return betweenValue
  
print '---------------------'
print 'Betweenness'
for player in finalBetweenCounts:
  print playersMap[player] + ' ' + str(round(betweenness(player),3))
  
def getTriangleData(passString):
  betweenCounts = {}
  for i in range(len(passString) - 2):
    j = i + 2
    k = i + 1
    if passString[k] in betweenCounts and passString[k] != passString[j] and passString[k] != passString[i]:
      betweenCounts[passString[k]][str(passString[i])+'-'+str(passString[j])] += 1
    elif passString[k] != passString[j] and passString[k] != passString[i]:
      tempDict = collections.defaultdict(int)
      tempDict[str(passString[i])+'-'+str(passString[j])] = 1
      betweenCounts[passString[k]] = tempDict
  return betweenCounts

triangleData = {}
for passString in passStrings:
  betweenCounts = getTriangleData(passString)
  for player in betweenCounts:
    if player in triangleData:
      for key in betweenCounts[player]:
        triangleData[player][key] += betweenCounts[player][key]
    else:
      tempDict = copy.deepcopy(betweenCounts[player])
      triangleData[player] = tempDict
      
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
 
#print '---------------------'
#print 'Triangle data'     
#print triangleData

#print '---------------------'
#print 'Between counts'      
#print finalBetweenCounts

print '---------------------'
print 'Clustering Coefficients'
for p in allPlayers:
  if p in playersMap:
    print playersMap[p] + ' ' + str(getClusteringCoeff(p,allPlayers))
    
closeNessWeight = 0.1
betweenNessWeight = 0.25
pageRankWeight = 0.25
clusterWeight = 0.4

print '---------------------'
print 'Total Score'
score = {}
for p in allPlayers:
  if p in playersMap:
    score[p] = closeNessWeight * closeness(p,0.5) + betweenNessWeight * betweenness(p)
    + pageRankWeight * pageRank[p] + clusterWeight * getClusteringCoeff(p,allPlayers)
    print playersMap[p] + ' ' + str(score[p])
    
'''for p in allPlayers:
  if p in playersMap:
    G.add_node(p)
    passes = allPlayers[p]
    for recipient in passes:
      G.add_edge(p,recipient,weight=passes[recipient])
      
nx.draw(G)'''
