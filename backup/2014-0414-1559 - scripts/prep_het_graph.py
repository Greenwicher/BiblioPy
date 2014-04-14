#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
   Copyright (C) 2012
   All rights reserved.
   BSD license.
"""

# usage: prep_het_graph.py -i DIR -o DIR [-d INT] [-v]
# 

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
def prep_het_graph(in_dir,out_dir,dyn_window,verbose):

  ## INPUT DATA
  src1  = os.path.join(in_dir, "articles.dat") 
  src2  = os.path.join(in_dir, "authors.dat")
  src3  = os.path.join(in_dir, "keywords.dat")
  src4  = os.path.join(in_dir, "subjects.dat")
  src5  = os.path.join(in_dir, "references.dat")
  src6  = os.path.join(in_dir, "countries.dat")
  src7  = os.path.join(in_dir, "institutions.dat")
  src8  = os.path.join(in_dir, "labos.dat")

  ## CREATE HETEROGENEOUS TABLE
  if verbose: print "..create heterogeneous table"
 
  het_table = dict();
  Y_table = dict();
  Ymin=2100;Ymax=1500

  pl = Utils.Article()
  pl.read_file(src1)  
  nb_art = len(pl.articles) # store the number of articles within database
  for l in pl.articles:
      if (l.year > 1900 and l.year < 2100): 
          Y_table[l.id] = l.year # store the publication year of each article
          if(l.year > Ymax): Ymax=l.year
          if(l.year < Ymin): Ymin=l.year
          if ('Y',l.year) in het_table: het_table[('Y',l.year)].append( l.id )
          else: het_table[('Y',l.year)] = [l.id]
          if ('J',l.journal) in het_table: het_table[('J',l.journal)].append( l.id )
          else: het_table[('J',l.journal)] = [l.id]

  pl = Utils.Author()
  pl.read_file(src2)  
  for l in pl.authors:
      if ('A',l.author) in het_table: 
          if (l.id not in het_table[('A',l.author)]): het_table[('A',l.author)].append( l.id )
      else: het_table[('A',l.author)] = [l.id]

  pl = Utils.Keyword()
  pl.read_file(src3)  
  for l in pl.keywords:
      if (l.ktype == 'IK'):
          if ('K',l.keyword) in het_table: 
              if (l.id not in het_table[('K',l.keyword)]): het_table[('K',l.keyword)].append( l.id )
          else: het_table[('K',l.keyword)] = [l.id]

  pl = Utils.Subject()
  pl.read_file(src4)  
  for l in pl.subjects:
      if ('S',l.subject) in het_table: 
          if (l.id not in het_table[('S',l.subject)]): het_table[('S',l.subject)].append( l.id )
      else: het_table[('S',l.subject)] = [l.id]
  
  pl = Utils.Ref()
  pl.read_file(src5)  
  for l in pl.refs:
      foo = l.firstAU + ', ' + str(l.year) + ', ' + l.journal + ', ' + l.volume + ', ' + l.page 
      if ('R',foo) in het_table: het_table[('R',foo)].append( l.id )
      else: het_table[('R',foo)] = [l.id]
      if ('RJ',l.journal) in het_table: het_table[('RJ',l.journal)].append( l.id )
      else: het_table[('RJ',l.journal)] = [l.id]

  pl = Utils.Institution()
  pl.read_file(src7)  
  for l in pl.institutions:
      if ('I',l.institution) not in het_table: het_table[('I',l.institution)] = [] 
      if l.id not in het_table[('I',l.institution)]: het_table[('I',l.institution)].append( l.id )

  pl = Utils.Country()
  pl.read_file(src6)  
  for l in pl.countries:
      if ('C',l.country) not in het_table: het_table[('C',l.country)] = []; 
      if l.id not in het_table[('C',l.country)]: het_table[('C',l.country)].append( l.id )

  pl = Utils.Labo()
  pl.read_file(src8)  
  for l in pl.labos:
      if ('L',l.labo) not in het_table: het_table[('L',l.labo)] = []; 
      if l.id not in het_table[('L',l.labo)]: het_table[('L',l.labo)].append( l.id )

  ## DETERMINE THRESHOLDS 
  ## ...initialize
  Y_list = []; J_list = []; A_list = []; K_list = []; S_list = []; R_list = []; RJ_list = []; I_list = []; C_list = []; L_list = [];
  for (t,x) in het_table:
      if(t == 'Y'): Y_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'J'): J_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'A'): A_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'K'): K_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'S'): S_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'R'): R_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'RJ'): RJ_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'I'): I_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'C'): C_list.append( (x,len(het_table[(t,x)])) )
      if(t == 'L'): L_list.append( (x,len(het_table[(t,x)])) )

  xxY = []; yyY = []
  for elm in Y_list:
      xxY.append( elm[0] )
      yyY.append( elm[1] )
  xx = numpy.zeros(nb_art+1, dtype=numpy.ndarray)
  for i in range(nb_art+1): xx[i]=i
  xrj = numpy.zeros(len(R_list) + 1, dtype=numpy.ndarray)
  for i in range(len(R_list)+1): xrj[i]=i
  yyJ = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in J_list: yyJ[v] += 1 
  yyA = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in A_list: yyA[v] += 1 
  yyK = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in K_list: yyK[v] += 1 
  yyS = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in S_list: yyS[v] += 1 
  yyR = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in R_list: yyR[v] += 1 
  yyRJ = numpy.zeros(len(R_list) + 1, dtype=numpy.ndarray)
  for (x,v) in RJ_list: yyRJ[v] += 1 
  yyI = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in I_list: yyI[v] += 1  
  yyC = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in C_list: yyC[v] += 1   
  yyL = numpy.zeros(nb_art + 1, dtype=numpy.ndarray)
  for (x,v) in L_list: yyL[v] += 1  

  ## ... confirm
  vA = vY = vC = 5; vJ = vK = vS = vI = 10; vR = 20; vRJ = 50; 
#  vA = 5; vK = 10; vY = vC = vJ = vS = vI = vR = 5000; vRJ = 20000;
  confirm = 'n'
  while confirm != 'y':
      confirm_threshold(vA,vY,vC,vJ,vK,vS,vI,vR,vRJ,len(A_list),len(xxY),len(C_list),len(J_list),len(K_list),len(S_list),len(I_list),len(R_list),len(RJ_list),yyA,yyY,yyC,yyJ,yyK,yyS,yyI,yyR,yyRJ,nb_art)
      confirm = raw_input("Confirm (y/n): ")
      if confirm == 'n':
          vA  = input("threshold for authors, used at least ? times:")
          vY  = input("threshold for publication years, used at least ? times:")
          vJ  = input("threshold for journals, used at least ? times:")
          vK  = input("threshold for keywords, used at least ? times:")
          vS  = input("threshold for subjects, used at least ? times:")
          vI  = input("threshold for institutions, used at least ? times:")
          vC  = input("threshold for countries, used at least ? times:")
          vR  = input("threshold for refs, used at least ? times:")
          vRJ = input("threshold for refs journals, used at least ? times:")


  ## ... selecting relevant data thanks to the thresholds
  het_table2 = dict()
  for (t,x) in het_table:
      l = len(het_table[(t,x)])
      if (t == 'Y') and l >= vY: het_table2[(t,x)] = het_table[(t,x)] 
      if (t == 'J') and l >= vJ: het_table2[(t,x)] = het_table[(t,x)]
      if (t == 'A') and l >= vA: het_table2[(t,x)] = het_table[(t,x)] 
      if (t == 'K') and l >= vK: het_table2[(t,x)] = het_table[(t,x)] 
      if (t == 'S') and l >= vS: het_table2[(t,x)] = het_table[(t,x)] 
      if (t == 'R') and l >= vR: het_table2[(t,x)] = het_table[(t,x)]
      if (t == 'RJ') and l >= vRJ: het_table2[(t,x)] = het_table[(t,x)]
      if (t == 'I') and l >= vI: het_table2[(t,x)] = het_table[(t,x)]
      if (t == 'C') and l >= vC: het_table2[(t,x)] = het_table[(t,x)] 
      if (t == 'L') and l >= 1: het_table2[(t,x)] = het_table[(t,x)] 
  ##
  confirm = 'n'; l_thr=1
  while confirm != 'y':
      print "We keep links between nodes co-used at least %d times" % (l_thr)
      confirm = raw_input("Confirm (y/n): ")
      if confirm == 'n':
          l_thr  = input("threshold for links -- nodes should be co-used at least ? times:")

  ## PREP GEPHI STATIC HETEROGENEOUS NETWORK FILE 
  if(dyn_window == 0):
      if verbose: print "\nPreparing the gdf file"

      ## ... ini
      dst = os.path.join(out_dir, "het_static.gdf")
      f_gephi = open(dst,'w')
 
      ## ... prep nodes
      if verbose: print "Nodes..........."

      color_nodes = {'Y': '255,255,0', 'J': '150,0,150', 'A': '20,50,255', 'K': '255,0,255', 'S': '50,0,150', 'R': '255,0,0', 'RJ': '255,97,0', 'I': '0,255,0', 'C': '0,255,255', 'L': '0,180,0'}

      id_table = dict()
      i = 0
      f_gephi.write("nodedef>name VARCHAR,label VARCHAR,type VARCHAR,width DOUBLE,height DOUBLE,size DOUBLE,color VARCHAR\n")
      for (t,x) in het_table2:
          id_table[i] = (t,x)
          l = len(het_table2[(t,x)])
          f_gephi.write("%d,'%s',%s,%f,%f,%d,'%s'\n" % (i, x, t, math.sqrt(l),math.sqrt(l),l, color_nodes[t]) )  
          i += 1
      i_range = i

      ## ... prep edges
      if verbose: print "Edges..........."

      e = len(het_table2) * len(het_table2) / 2; ee = 0; p=5 
      f_gephi.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE,nb_comm DOUBLE")
      if verbose: print "0%"
      for i in range(i_range):
          for j in range(i_range):
              if(i < j):
                  elm_i=id_table[i]; elm_j=id_table[j]
                  ee += 1
                  li=len(het_table2[elm_i]);lj=len(het_table2[elm_j])
                  nb_comm=0 
                  for u in het_table2[elm_i]:
                      if u in het_table2[elm_j]: nb_comm += 1       
                  if nb_comm >= l_thr: f_gephi.write("\n%d,%d,%f,%d" % (i, j, nb_comm/math.sqrt(li*lj), nb_comm) ) 
                  if (ee > (1.0 * e * p) / 100) and verbose: print "%d%%" % (p); p +=5
      if verbose: print "100%"

      ## ... end
      f_gephi.close() 


  ## PREP GEPHI DYNAMIC HETEROGENEOUS NETWORK FILE 
  if(dyn_window > 0):
      if verbose: print "\nPreparing the gexf file"

      ## ... ini
      dst = os.path.join(out_dir, "het_dyn.gexf")
      f_gephi = open(dst,'w')
      f_gephi.write("<gexf xmlns=\"http://www.gexf.net/1.1draft\"\n       xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n       xsi:schemaLocation=\"http://www.gexf.net/1.1draft\n                             http://www.gexf.net/1.1draft/gexf.xsd\"\n      version=\"1.1\">\n  <graph mode=\"dynamic\" defaultedgetype=\"undirected\" timeformat = \"date\" start=\"%d-01-01\" end=\"%d-12-31\">\n\t\t<attributes class=\"node\" mode=\"dynamic\">\n\t\t  <attribute id=\"type\" title=\"type\" type=\"STRING\"/>\n\t\t  <attribute id=\"times_used\" title=\"times_used\" type=\"FLOAT\"/>\n\t\t</attributes>\n\t\t<attributes class=\"edge\" mode=\"dynamic\">\n\t\t  <attribute id=\"weight\" title=\"weight\" type=\"FLOAT\"/>\n\t\t  <attribute id=\"NbComm\" title=\"NbComm\" type=\"FLOAT\"/>\n\t\t</attributes>\n\n" % (Ymin,Ymax))

 
      ## ... prep nodes
      if verbose: print "Nodes..........."
      id_table = dict()
      het_table3 = dict()
      i = 0
      f_gephi.write("\t<nodes>\n")

      for (t,x) in het_table2:
          id_table[i] = (t,x)
          w=str(x).replace('&','-')
          foo = [] 
          # place in list 'foo' some info about the node (t,x) 
          y = Ymin
          while (y <= Ymax):
              l=0
              for u in het_table2[(t,x)]:
                  if( Y_table[u] >= y and Y_table[u] < y + dyn_window): 
                      l += 1
                      if (i,y) in het_table3: het_table3[(i,y)].append( u )
                      else: het_table3[(i,y)] = [u]
              if(l>0): foo.append( (y,l) )
              y += dyn_window 
          #end while 
          #translate the info within list 'foo' into gexf format
          f_gephi.write("\t<node id=\"%d\" label=\"%s\" >\n\t\t<attvalues>\n\t\t\t<attvalue for=\"type\" value=\"%s\"/>\n" % (i, w, t))
          for (y,l) in foo:
              f_gephi.write("\t\t\t<attvalue for=\"times_used\" value=\"%d\" start=\"%d-01-01\" end=\"%d-12-31\"/>\n" % (l, y, y + dyn_window -1))
          f_gephi.write("\t\t</attvalues>\n\t\t<spells>\n")
          for (y,l) in foo:
              f_gephi.write("\t\t\t<spell start=\"%d-01-01\" end=\"%d-12-31\"/>\n" % (y, y + dyn_window -1) )  
          f_gephi.write("\t\t</spells>\n\t</node>\n")  
          i += 1
      #end for    
      i_range = i
      f_gephi.write("\t</nodes>\n")


      ## ... prep edges
      if verbose: print "Edges..........."
      e = i_range * i_range / 2; ee = 0; p=5 
      f_gephi.write("\t<edges>\n")
      if verbose: print "0%"
      for i in range(i_range):
          for j in range(i_range):
              if(i < j):
                  ee += 1
                  y=Ymin
                  aux=0
                  foo=[]
                  while (y <= Ymax):
                      li=lj=0
                      if ((i,y) in het_table3) and ((j,y) in het_table3): li=len(het_table3[(i,y)]); lj=len(het_table3[(j,y)])
                      if(li * lj) > 0:
                          nb_comm=0
                          for u in het_table3[(i,y)]:
                              if u in het_table3[(j,y)]: nb_comm += 1    
                          if nb_comm >= l_thr: 
                              if aux == 0: 
                                  f_gephi.write("\t<edge source=\"%d\" target=\"%d\">\n\t\t<attvalues>\n" % (i,j))
                                  aux = 1
                              foo.append( y )    
                              f_gephi.write("\t\t\t<attvalue for=\"weight\" value=\"%f\" start=\"%d-01-01\" end=\"%d-12-31\"/>\n\t\t\t<attvalue for=\"NbComm\" value=\"%d\" start=\"%d-01-01\" end=\"%d-12-31\"/>\n" % ((1.0 * nb_comm)/math.sqrt(li*lj), y, y + dyn_window - 1, nb_comm, y, y + dyn_window - 1))
                      y += dyn_window   
                  #end while
                  if aux == 1: 
                      f_gephi.write("\t\t</attvalues>\n\t\t<spells>\n") 
                      for y in foo:
                          f_gephi.write("\t\t\t<spell start=\"%d-01-01\" end=\"%d-12-31\"/>\n" % (y, y + dyn_window -1) )  
                      f_gephi.write("\t\t</spells>\n\t</edge>\n")  

                  if (ee > (1.0 * e * p) / 100) and verbose: print "%d%%" % (p); p +=5
              #end edge
      if verbose: print "100%"

      f_gephi.write("\t</edges>\n")

      ## ... end
      f_gephi.write("  </graph>\n</gexf>")
      f_gephi.close() 


  ## END
  return

## ##################################################
## ##################################################
## ##################################################

def confirm_threshold(vA,vY,vC,vJ,vK,vS,vI,vR,vRJ,lA,lY,lC,lJ,lK,lS,lI,lR,lRJ,yyA,yyY,yyC,yyJ,yyK,yyS,yyI,yyR,yyRJ,nb_art):

  auxY = auxA = auxJ = auxK = auxS = auxI = auxR = auxRJ = auxC = 0

  for v in range(lY): 
      if(yyY[v] >= vY): auxY += 1
  v = vA
  while v <= nb_art: auxA += yyA[v]; v += 1
  v = vJ 
  while v <= nb_art: auxJ += yyJ[v]; v += 1
  v = vK 
  while v <= nb_art: auxK += yyK[v]; v += 1
  v = vS 
  while v <= nb_art: auxS += yyS[v]; v += 1
  v = vI 
  while v <= nb_art: auxI += yyI[v]; v += 1
  v = vC
  while v <= nb_art: auxC += yyC[v]; v += 1
  v = vR
  while v <= nb_art: auxR += yyR[v]; v += 1
  v = vRJ 
  while v <= lR: auxRJ += yyRJ[v]; v += 1

  
  print "\n THRESHOLDS proposed: keep items of each type used at least ...x... times (this ensures faster computing and lighter gexf output files. Keep in mind that additionnal filtering can also be performed later with GEPHI):\n Authors used in at least ...%d... articles\n ==> %d authors out of %d\n Publication Years used in at least ...%d... articles \n ==> %d PY out of %d\n Journals used in at least ...%d... articles \n ==> %d journals out of %d\n Keywords used in at least ...%d... articles \n ==> %d keywords out of %d\n Subjects used in at least ...%d... articles \n ==> %d subjects out of %d\n Institutions used in at least ...%d... articles \n ==> %d institutions out of %d\n Countries used in at least ...%d... articles \n ==> %d countries out of %d\n Refs used in at least ...%d... articles \n ==> %d refs out of %d\n Refs Journals used in at least ...%d... references \n ==> %d RJ out of %d" % (vA,auxA,lA,vY,auxY,lY,vJ,auxJ,lJ,vK,auxK,lK,vS,auxS,lS,vI,auxI,lI,vC,auxC,lC,vR,auxR,lR,vRJ,auxRJ,lRJ)

## ##################################################
## ##################################################
## ##################################################

def main():
# usage: prep_het_graph.py [-h] [--version] -i DIR -o DIR [-d INT] [-v]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   --version             show program's version number and exit
#   -i DIR, --input_dir DIR input directory name
#   -o DIR, --output_dir DIR input directory name
#   -r 
  # Parse line options.
  # Try to have always the same input options
  parser = argparse.ArgumentParser(description = 'parser')

  parser.add_argument('--version', action='version', version='%(prog)s 1.1')
  
  parser.add_argument("-i", "--input_dir", nargs=1, required=True,
          action = "store", dest="in_dir",
          help="input directory name",
          metavar='DIR')

  parser.add_argument("-o", "--output_dir", nargs=1, required=True,
          action = "store", dest="out_dir",
          help="output directory name",
          metavar='DIR')

  parser.add_argument("-d", "--dyn_window", nargs=1, type=int,
          action = "store", dest="dyn_window",
          default = [0], help="dyn_window",
          metavar='INT')
          
  parser.add_argument("-v", "--verbose",
          action = "store_true", dest="verbose",
          default = False,
          help="verbose mode [default %(default)s]")

  #Analysis of input parameters
  args = parser.parse_args()
  
  if (not os.path.exists(args.in_dir[0])):
      print "Error: Input directory does not exist: ", args.in_dir[0]
      exit()

  if (not os.path.exists(args.out_dir[0])):
      print "Error: Output directory does not exist: ", args.out_dir[0]
      exit()
  ##      

  prep_het_graph(args.in_dir[0],args.out_dir[0],args.dyn_window[0],args.verbose)

  return


    
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
    main()

## ##################################################
## ##################################################
## ##################################################
