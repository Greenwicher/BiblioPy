#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
   Copyright (C) 2012
   All rights reserved.
   BSD license.
   .... If you are using these scripts, please cite our "Scientometrics" paper:
   .... S Grauwin, P Jensen, Mapping Scientific Institutions. Scientometrics 89(3), 943-954 (2011)
"""

import os
import sys
import glob
import numpy
import argparse
import math
import Utils

## ##################################################
## ##################################################
## ##################################################
def comm_tables(in_dir,partition,thr,verbose):

  ## INPUT DATA
  src1  = os.path.join(in_dir, "articles.dat") 
  src2  = os.path.join(in_dir, "authors.dat")
  src3  = os.path.join(in_dir, "keywords.dat")
  src4  = os.path.join(in_dir, "subjects.dat")
  src5  = os.path.join(in_dir, "references.dat")
  src6  = os.path.join(in_dir, "countries.dat")
  src7  = os.path.join(in_dir, "institutions.dat")


  ## Communities sizes - we are mostly interested by articles within communities of size > thr
  comm_size = dict();
  for com in set(partition.values()) :
    list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
    comm_size[com] = len(list_nodes)

  ## TREAT DATA
  #######
  # initialize
  list_comm = [] ## list of communities of size > thr
  list_id = dict(); ## list of id -- articles within the BC network and within a community of size > thr
  for com in comm_size: 
    if comm_size[com] > thr: list_comm.append( com )
  for id_art in partition:
    com = partition[id_art]
    if comm_size[com] > thr: list_id[id_art] = ''

  #######
  # KEYWORDS
  if verbose: print "....most frequent keywords"
  art_wK = dict(); ## lists article with keywords
  probaK = dict(); ## records the freq of each keyword in the whole database
  freqK  = dict(); ## "" in each community of size > thr
  for com in list_comm: freqK[com] = dict();

  # read data
  pl = Utils.Keyword()
  pl.read_file(src3)  
  for l in pl.keywords:
    if (l.ktype == 'IK'):
      # list the articles with keywords
      if l.id not in art_wK: art_wK[l.id] = ''
      # record the number of occurrence of a given K
      if l.keyword not in probaK: probaK[l.keyword] = 0
      probaK[l.keyword] += 1
      # record the occurrence of a given K within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.keyword not in freqK[com]: freqK[com][l.keyword] = 0
        freqK[com][l.keyword] += 1

  # extract the 20 most frequent keywords within each community, normalize their frequencies and compute their significance
  stuffK = dict();
  NK = len(art_wK);
  if NK > 0:
    for com in freqK:
      cs = comm_size[com]
      stuffK[com] = dict()
      L = freqK[com].items()
      L.sort(cmpval)
      for i in range(min(20,len(L))):
        keyw = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaK[keyw] * 1.0 / NK 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffK[com][i] = [keyw, f*100, sigma]

  #######
  # SUBJECTS
  if verbose: print "....most frequent subjects"
  art_wS = dict(); ## lists article with subjects
  probaS = dict(); ## records the freq of each subject in the whole database
  freqS  = dict(); ## "" in each community of size > thr
  for com in list_comm: freqS[com] = dict();

  # read data
  pl = Utils.Subject()
  pl.read_file(src4)  
  for l in pl.subjects:
      # list the articles with subjects
      if l.id not in art_wS: art_wS[l.id] = ''
      # record the number of occurrence of a given S
      if l.subject not in probaS: probaS[l.subject] = 0
      probaS[l.subject] += 1
      # record the occurrence of a given S within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.subject not in freqS[com]: freqS[com][l.subject] = 0
        freqS[com][l.subject] += 1
  #
  # extract the 10 most frequent subjects within each community, normalize their frequencies and compute their significance
  stuffS = dict();
  NS = len(art_wS);
  if NS > 0:
    for com in freqS:
      cs = comm_size[com]
      stuffS[com] = dict()
      L = freqS[com].items()
      L.sort(cmpval)
      for i in range(min(10,len(L))):
        subj = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaS[subj] * 1.0 / NS 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffS[com][i] = [subj.replace('&','\\&'), f*100, sigma]

  #######
  # JOURNALS
  if verbose: print "....most frequent journals"
  art_wJ = dict(); ## lists article with journals
  probaJ = dict(); ## records the freq of each journal in the whole database
  freqJ  = dict(); ## "" in each community of size > thr
  for com in list_comm: freqJ[com] = dict();

  # read data
  #
  pl = Utils.Article()
  pl.read_file(src1)  
  for l in pl.articles:
      # list the articles with journals
      if l.id not in art_wJ: art_wJ[l.id] = ''
      # record the number of occurrence of a given J
      if l.journal not in probaJ: probaJ[l.journal] = 0
      probaJ[l.journal] += 1
      # record the occurrence of a given J within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.journal not in freqJ[com]: freqJ[com][l.journal] = 0
        freqJ[com][l.journal] += 1
  #
  # extract the 10 most frequent journals within each community, normalize their frequencies and compute their significance
  stuffJ = dict();
  NJ = len(art_wJ);
  if NJ > 0:
    for com in freqJ:
      cs = comm_size[com]
      stuffJ[com] = dict()
      L = freqJ[com].items()
      L.sort(cmpval)
      for i in range(min(10,len(L))):
        jour = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaJ[jour] * 1.0 / NJ 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffJ[com][i] = [jour.replace('&','\\&'), f*100, sigma]

  #######
  # AUTHORS
  if verbose: print "....most frequent authors"
  art_wA = dict(); ## lists article with authors
  probaA = dict(); ## records the freq of each author in the whole database
  freqA  = dict(); ## "" in each community of size > thr
  for com in list_comm: freqA[com] = dict();

  # read data
  pl = Utils.Author()
  pl.read_file(src2)  
  for l in pl.authors:
      # list the articles with authors
      if l.id not in art_wA: art_wA[l.id] = ''
      # record the number of occurrence of a given A
      if l.author not in probaA: probaA[l.author] = 0
      probaA[l.author] += 1
      # record the occurrence of a given A within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.author not in freqA[com]: freqA[com][l.author] = 0
        freqA[com][l.author] += 1
  #
  # extract the 10 most frequent authors within each community, normalize their frequencies and compute their significance
  stuffA = dict();
  NA = len(art_wA);
  if NA > 0:
    for com in freqA:
      cs = comm_size[com]
      stuffA[com] = dict()
      L = freqA[com].items()
      L.sort(cmpval)
      for i in range(min(10,len(L))):
        auth = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaA[auth] * 1.0 / NA 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffA[com][i] = [auth, f*100, sigma]

  #######
  # INSTITUTIONS
  if verbose: print "....most frequent institutions"
  art_wI = dict(); ## lists article with institutions
  probaI = dict(); ## records the freq of each institution in the whole database
  freqI  = dict(); ## "" in each community of size > thr
  ## the following dict() are used to ensure that we count each pair "article-institution" only once
  probaI_aux = dict(); ## records the freq of each institutions in the whole database
  freqI_aux  = dict(); ## "" in each community of size > thr
  for com in list_comm:  
    freqI[com] = dict()
    freqI_aux[com] = dict()

  # read data
  pl = Utils.Institution()
  pl.read_file(src7)  
  for l in pl.institutions:
      # list the articles with institutions
      if l.id not in art_wI: art_wI[l.id] = ''
      # record the number of occurrence of a given I
      if l.institution not in probaI: 
        probaI[l.institution] = 0; probaI_aux[l.institution] = []
      if l.id not in probaI_aux[l.institution]:
        probaI_aux[l.institution].append( l.id )
        probaI[l.institution] += 1
      # record the occurrence of a given I within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.institution not in freqI[com]: 
          freqI[com][l.institution] = 0; freqI_aux[com][l.institution] = [] 
        if l.id not in freqI_aux[com][l.institution]:
          freqI_aux[com][l.institution].append( l.id )
          freqI[com][l.institution] += 1
  #
  # extract the 20 most frequent institutions within each community, normalize their frequencies and compute their significance
  stuffI = dict();
  NI = len(art_wI);
  if NI > 0:
    for com in freqI:
      cs = comm_size[com]
      stuffI[com] = dict()
      L = freqI[com].items()
      L.sort(cmpval)
      for i in range(min(20,len(L))):
        inst = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaI[inst] * 1.0 / NI 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffI[com][i] = [inst.replace('&','\\&'), f*100, sigma]

  #######
  # COUNTRIES
  if verbose: print "....most frequent countries"
  art_wC = dict(); ## lists article with countries
  probaC = dict(); ## records the freq of each country in the whole database
  freqC  = dict(); ## "" in each community of size > thr
  ## the following dict() are used to ensure that we count each pair "article-country" only once
  probaC_aux = dict(); ## records the freq of each institutions in the whole database
  freqC_aux  = dict(); ## "" in each community of size > thr
  for com in list_comm:  
    freqC[com] = dict() 
    freqC_aux[com] = dict();

  # read data
  pl = Utils.Country()
  pl.read_file(src6)  
  for l in pl.countries:
      # list the articles with countries
      if l.id not in art_wC: art_wC[l.id] = ''
      # record the number of occurrence of a given C
      if l.country not in probaC: 
        probaC[l.country] = 0; probaC_aux[l.country] = []; 
      if l.id not in probaC_aux[l.country]:
        probaC_aux[l.country].append( l.id ); 
        probaC[l.country] += 1
      # record the occurrence of a given C within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.country not in freqC[com]: 
          freqC[com][l.country] = 0; freqC_aux[com][l.country] = [];
        if l.id not in freqC_aux[com][l.country]:
          freqC_aux[com][l.country].append( l.id ); 
          freqC[com][l.country] += 1

  # extract the 10 most frequent countries within each community, normalize their frequencies and compute their significance
  stuffC = dict();
  NC = len(art_wC);
  if NC > 0:
    for com in freqC:
      cs = comm_size[com]
      stuffC[com] = dict()
      L = freqC[com].items()
      L.sort(cmpval)
      for i in range(min(10,len(L))):
        coun = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaC[coun] * 1.0 / NC 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffC[com][i] = [coun.replace('&','\\&'), f*100, sigma]

  #######
  # REFERENCES
  if verbose: print "....most frequent references"
  art_wR = dict(); ## lists article with refs
  probaR = dict(); ## records the freq of each ref in the whole database
  freqR  = dict(); ## "" in each community of size > thr
  for com in list_comm: freqR[com] = dict()

  # read data
  pl = Utils.Ref()
  pl.read_file(src5)  
  for l in pl.refs:
      reference = l.firstAU + ", " + str(l.year) + ", " + l.journal + " (" + str(l.volume) + "), " + str(l.page)
      # list the articles with references
      if l.id not in art_wR: art_wR[l.id] = ''
      # record the number of occurrence of a given R
      if reference not in probaR: probaR[reference] = 0
      probaR[reference] += 1
      # record the occurrence of a given R within each community
      if l.id in list_id: 
        com = partition[l.id]
        if reference not in freqR[com]: freqR[com][reference] = 0
        freqR[com][reference] += 1
  #
  # extract the 25 most frequent refs within each community, normalize their frequencies and compute their significance
  stuffR = dict();
  NR = len(art_wR);
  if NR > 0:
    for com in freqR:
      cs = comm_size[com]
      stuffR[com] = dict()
      L = freqR[com].items()
      L.sort(cmpval)
      for i in range(min(25,len(L))):
        ref = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaR[ref] * 1.0 / NR 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffR[com][i] = [ref.replace('[','').replace(']','').replace('&','\\&'), f*100, sigma]

  #######
  # REFS JOURNALS
  if verbose: print "....most frequent refs journals"
  art_wRJ = dict(); ## lists article with refj
  probaRJ = dict(); ## records the freq of each refj in the whole database
  freqRJ  = dict(); ## "" in each community of size > thr
  ## the following dict() are used to ensure that we count each pair "article-refj" only once
  probaRJ_aux = dict(); ## records the freq of each institutions in the whole database
  freqRJ_aux  = dict(); ## "" in each community of size > thr
  for com in list_comm:  
    freqRJ[com] = dict()
    freqRJ_aux[com] = dict()

  # read data
  pl = Utils.Ref()
  pl.read_file(src5)  
  for l in pl.refs:
      # list the articles with ref journals
      if l.id not in art_wRJ: art_wRJ[l.id] = ''
      # record the number of occurrence of a given RJ
      if l.journal not in probaRJ: 
        probaRJ[l.journal] = 0; probaRJ_aux[l.journal] = dict()
      if l.id not in probaRJ_aux[l.journal]:
        probaRJ_aux[l.journal][l.id] = ''
        probaRJ[l.journal] += 1
      # record the occurrence of a given RJ within each community
      if l.id in list_id: 
        com = partition[l.id]
        if l.journal not in freqRJ[com]: 
          freqRJ[com][l.journal] = 0
          freqRJ_aux[com][l.journal] = dict()
        if l.id not in freqRJ_aux[com][l.journal]:
          freqRJ_aux[com][l.journal][l.id] = '' 
          freqRJ[com][l.journal] += 1
  #
  #
  # extract the 10 most frequent refj within each community, normalize their frequencies and compute their significance
  stuffRJ = dict();
  NRJ = len(art_wRJ);
  if NRJ > 0:
    for com in freqRJ:
      cs = comm_size[com]
      stuffRJ[com] = dict()
      L = freqRJ[com].items()
      L.sort(cmpval)
      for i in range(min(10,len(L))):
        refj = L[i][0]
        f = L[i][1] * 1.0 / cs 
        p = probaRJ[refj] * 1.0 / NRJ 
        if p < 1: sigma = math.sqrt(cs) * (f - p) * 1.0 / math.sqrt(p*(1-p)) 
        else: sigma = 0
        stuffRJ[com][i] = [refj.replace('&','\\&'), f*100, sigma]

  ## END

  return (stuffK, stuffS, stuffJ, stuffA, stuffI, stuffC, stuffR, stuffRJ)

  ##############################
  
  ## END
  return

def cmpval(x,y):
    if x[1]>y[1]:
        return -1
    elif x[1]==y[1]:
        return 0
    else:
        return 1

## ##################################################
## ##################################################


def main():
# usage: BC.py [-h] [--version] -i DIR -o DIR -p FILE [-v]
#
# optional arguments:
#   -i DIR, --input_dir DIR input directory name
#   -o DIR, --output_dir DIR input directory name
  # Parse line options.
  # Try to have always the same input options
  parser = argparse.ArgumentParser(description = 'parser')

  parser.add_argument('--version', action='version', version='%(prog)s 1.1')
  
  parser.add_argument("-i", "--input_dir", nargs=1, required=True,
          action = "store", dest="in_dir",
          help="input directory name",
          metavar='DIR')

  parser.add_argument("-o", "--output_dir", nargs=1, required=False,
          action = "store", dest="out_dir", 
          help="output directory name",
          metavar='DIR')
          
  parser.add_argument("-p", "--partition",
          action = "store", dest="partition")

  parser.add_argument("-thr", "--thr", nargs=1, type=int,
          action = "store", dest="thr", default=[10],
          help="",
          metavar='thr')

  parser.add_argument("-v", "--verbose",
          action = "store_true", dest="verbose",
          default = False,
          help="verbose mode [default %(default)s]")

  #Analysis of input parameters
  args = parser.parse_args()
  
  if (not os.path.exists(args.in_dir[0])):
      print "Error: Input directory does not exist: ", args.in_dir[0]
      exit()

  if (not os.path.exists(args.partition[0])):
      print "Error: Input partition does not exist: ", args.partition[0]
      exit()

  if (not os.path.exists(args.out_dir[0])):
      print "Error: Output directory does not exist: ", args.out_dir[0]
      exit()

  ##

  partition = dict();      

  f_in = open(args.partition,'r')
  for line in f_in.readlines():
    foo = line.stript().split('\t')
    if len(foo) == 2:
      partition[int(foo[0])] = int(foo[1])
  f_in.close()
  
  ##
  comm_tables(args.in_dir[0],partition,thr,args.verbose)

  return


    
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
    main()

## ##################################################
## ##################################################
## ##################################################
