#! /usr/bin/env python
""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
			Liu Weizhi (http://greenwicher.github.io/)
   Copyright (C) 2014
   All rights reserved.
   BSD license.
"""

# usage: BC.py -i DIR -o DIR [-v]
# 

import os
import sys
import glob
import numpy
import argparse
import math
import Utils
import networkx as nx
import community, BCUtils

## ##################################################
## ##################################################
## ##################################################
def BC_network(in_dir,out_dir,verbose):

  ## INPUT DATA
  if verbose: print "..Initialize"

  src1  = os.path.join(in_dir, "articles.dat") 
  src5  = os.path.join(in_dir, "references.dat")

  Ymin = 2100; Ymax = 1900 # store the min and max publication year 
  nR = dict() # store the number of refs of the articles
  pl = Utils.Article()
  pl.read_file(src1)  
  nb_art = len(pl.articles) # store the number of articles within database
  for l in pl.articles:
	  nR[l.id] = 0
	  if (l.year > 1900 and l.year < 2100): 
		  if(l.year > Ymax): Ymax=l.year
		  if(l.year < Ymin): Ymin=l.year


  ## CREATE BC WEIGHT TABLE
  if verbose: print "..Create the 'Bibliographic Coupling' weight table"
 
  ref_table = dict() # store the id of articles using a given ref
  BC_table = dict() # store the number of common refs between pairs of articles

  if verbose: print "....loading refs table"
  pl = Utils.Ref()
  pl.read_file(src5)  
  for l in pl.refs:
	  foo = l.firstAU + ', ' + str(l.year) + ', ' + l.journal + ', ' + l.volume + ', ' + l.page 
	  if foo in ref_table: ref_table[foo].append( l.id )
	  else: ref_table[foo] = [l.id]
	  nR[l.id] += 1

  if verbose: print "....detecting common references"
  for foo in ref_table:
	if len(ref_table[foo]) > 1:
	  for i in ref_table[foo]:
		  for j in ref_table[foo]:
			  if i<j:
				  if i not in BC_table: BC_table[i] = dict()
				  if j not in BC_table[i]: BC_table[i][j] = 0
				  BC_table[i][j] += 1 

  """
  ## EXPORT BC WEIGHT TABLE
  if verbose: print "Output the BC_weight table"
  filename = os.path.join(in_dir, "BCweight.txt")
  f_BC = open(filename,'w')
  for i in BC_table:
	for j in BC_table[i]:
	  w_ij = (1.0 * BC_table[i][j]) / math.sqrt(nR[i] * nR[j])
	  #f_BC.write("%d\t%d\t%f\t%d\n" % (i, j, w_ij, BC_table[i][j]) )
	  if i > j: f_BC.write("%d %d %1.7f\n" % (i, j, w_ij) )
  f_BC.close()
  """

  # choose threshold
  confirm = 'n'; thr=1;
  
  while confirm != 'y':
	if thr == 1: print "Keep BC links between articles sharing at least %d reference" % (thr)
	else: print "Keep BC links between articles sharing at least %d references" % (thr)
	confirm = raw_input("Confirm (y/n): ")
	while confirm not in ['n','y']:
	  confirm = raw_input("...typing error!\n Confirm (y/n): ")
	if confirm == 'n':
	  thr = input("threshold for BC links -- articles should be share at least ? references:")

  bcthr = thr

  ##############################
  ## BC COMMUNITIES
  if verbose: print "..BC communities"
  #... define BC network
  if verbose: print "....define graph in networkx format"
  G=nx.Graph()
  for i in BC_table:
	for j in BC_table[i]:
	  if BC_table[i][j] >= thr:
		w_ij = (1.0 * BC_table[i][j]) / math.sqrt(nR[i] * nR[j])
		G.add_edge(i, j, weight=w_ij)

  #...
  if verbose: print "....computing communities with Louvain algo"
  dendogram = community.generate_dendogram(G, part_init=None)

  #... output infos
  print "....There are %d articles in the database" % (nb_art)
  print "....There are %d articles in the BC network\n......(ie sharing at least one reference with another article)" % (len(G.nodes()) )
  for level in range(len(dendogram)):
	part = community.partition_at_level(dendogram, level)
	mod = community.modularity(part, G)
	nb_comm = len(set(part.values()))
	size_sup10 = 0; size_sup100 = 0;  #communities_caracteristics(partition, thr, level)
	for com in set(part.values()) :
	  list_nodes = [nodes for nodes in part.keys() if part[nodes] == com]
	  if len(list_nodes) > 100: size_sup100 += 1
	  if len(list_nodes) > 10: size_sup10 += 1
	print "....level %d: %d communities [%d with size > 10, %d with size > 100], modularity Q=%1.6f" % (level, nb_comm, size_sup10, size_sup100, mod)


  ##############################
  ## WHICH EXTRACTION ?
  print "..BC communities extraction"
  #
  confirm = 'n'; level = len(dendogram) - 1; thr = 10
  while confirm != 'y':
	part = community.partition_at_level(dendogram, level)
	nb_comm = len(set(part.values()))
	size_sup_thr = 0; n_sup_thr = 0;
	for com in set(part.values()) :
	  list_nodes = [nodes for nodes in part.keys() if part[nodes] == com]
	  if len(list_nodes) > thr: 
		n_sup_thr += len(list_nodes)
		size_sup_thr += 1
	print "....Extraction of level %d BC communities with size > %d\n......(%d articles gathered in %d communities):" % (level, thr, n_sup_thr, size_sup_thr)
	confirm = raw_input("....do you confirm? (y/n): ")
	if confirm == 'n':
	  level  = input("......level you want to extract:")
	  thr  = input("......keep communities of size > to:")

  #... partition
  partition = community.partition_at_level(dendogram, level)
  list_nodes= dict();
  for com in set(partition.values()) :
	list_nodes[com] = [nodes for nodes in partition.keys() if partition[nodes] == com]

  ##############################
  ## COMMUNITIES CARACTERISTICS
  if verbose: print"..Computing communities caracteristics"
  #.. ini
  filename = os.path.join(out_dir, "BCcomm_ID_Cards(bcthr=%d, thr=%d).tex" % (bcthr, thr))
  f_out = open(filename,"w")
  f_out.write("\documentclass[a4paper,11pt]{report}\n\usepackage[english]{babel}\n\usepackage[latin1]{inputenc}\n\usepackage{amsfonts,amssymb,amsmath}\n\usepackage{pdflscape}\n\usepackage{color}\n\n\\addtolength{\evensidemargin}{-60pt}\n\\addtolength{\oddsidemargin}{-60pt}\n\\addtolength{\\textheight}{80pt}\n\n\\title{{\\bf Communities ID Cards}}\n\date{\\begin{flushleft}This document gather the ``ID Cards'' of the BC communities found within your database.\\\\\n The BC network was built by keeping a link between articles sharing at least %d references. The communities characterized here correspond to the ones found in the level %d (in the sense of the Louvain algo) which gathers more than %d articles.\\\\\n These ID cards displays the most frequent keywords, subject categories, journals of publication, institution, countries, authors, references and reference journals of the articles of each community. The significance of an item $\sigma = \sqrt{N} (f - p) / \sqrt{p(1-p)}$ [where $N$ is the number of articles within the community and $f$ and $p$ are the proportion of articles respectively within the community and within the database displaying that item ] is also given (for example $\sigma > 5$ is really highly significant).\\\\\n\\vspace{1cm}\n\copyright Sebastian Grauwin, Liu Weizhi - (2014) \end{flushleft}}\n\n\\begin{document}\n\\begin{landscape}\n\maketitle\n" % (bcthr, level, thr))


  #.. quantitative
  comm_innerw = dict(); comm_size = dict(); 
  for com in list_nodes:
	size = len(list_nodes[com])
	W = 0;
	for id1 in list_nodes[com]:
	  for id2 in list_nodes[com]:
		if id2 > id1 and id2 in G.edge[id1]: 
		  W += G.edge[id1][id2]['weight']
	W *= 2.0 / (size * (size -1))
	comm_innerw[com]= 1.0 / W
	comm_size[com] = size
  Lcomm_size = comm_size.items()
  Lcomm_size.sort(cmpval)

  #.. frequency / significance of keywords, etc...
  comm_label = dict();
  (stuffK, stuffS, stuffJ, stuffA, stuffI, stuffC, stuffR, stuffRJ) = BCUtils.comm_tables(in_dir,partition,thr,verbose)

  #.. output tables
  for elm in Lcomm_size:
	if elm[1] > thr:
	  com = elm[0]
	  #K
	  if com in stuffK:
		if len(stuffK[com]) > 0 : comm_label[com] = stuffK[com][0][0]
		else: comm_label[com] = 'XXXX'
		f_out.write("\clearpage\n\n\\begin{table}[!ht]\n\caption{The community ``%s'' contains $N = %d$ articles. Its average internal link weight is $<\omega_{in}> \simeq 1/%d$ }\n\\textcolor{white}{aa}\\\\\n{\scriptsize\\begin{tabular}{|l r r|}\n\hline\nKeyword & f(\\%%) & $\sigma$\\\\\n\hline\n" % (comm_label[com], comm_size[com], comm_innerw[com] ) )
		for i in range(len(stuffK[com])):
		  if len(stuffK[com][i][0]) < 30:
			f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffK[com][i][0], stuffK[com][i][1], stuffK[com][i][2]) )
		  else:
			aux = stuffK[com][i][0].rfind(' ')
			while aux > 30: 
			   aux = stuffK[com][i][0][0:aux].rfind(' ')
			f_out.write("%s &  & \\\\\n" % ( stuffK[com][i][0][0:aux] ) )
			f_out.write("$\quad$%s & %1.2f & %1.2f\\\\\n" % ( stuffK[com][i][0][aux:], stuffK[com][i][1], stuffK[com][i][2]) )
		for i in range(max(0,20-len(stuffK[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		f_out.write("\clearpage\n\n\\begin{table}[!ht]\n\caption{The community ``?'' contains $N = %d$ articles. Its average internal link weight is $<\omega_{in}> \simeq 1/%d$ }\n\\textcolor{white}{aa}\\\\\n{\scriptsize\\begin{tabular}{|l r r|}\n\hline\nKeyword & f(\\%%) & $\sigma$\\\\\n\hline\n" % (comm_size[com], comm_innerw[com] ) )
		for i in range(20):
		  f_out.write(" &  & \\\\\n")
	  #S
	  f_out.write("\hline\n\hline\nSubject & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffS:
		for i in range(len(stuffS[com])):
		  f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffS[com][i][0], stuffS[com][i][1], stuffS[com][i][2]) )
		for i in range(max(0,10-len(stuffS[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(10): f_out.write(" &  & \\\\\n")
	  #J
	  f_out.write("\hline\n\hline\nJournal & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffJ:
		for i in range(len(stuffJ[com])):
		  f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffJ[com][i][0], stuffJ[com][i][1], stuffJ[com][i][2]) )
		for i in range(max(0,10-len(stuffJ[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(10): f_out.write(" &  & \\\\\n")
	  f_out.write("\hline\n\end{tabular}\n}\n")
	  #f_out.write("\hline\n\end{tabular}\n}\n\end{table}\n\n")
	  #I
	  f_out.write("{\scriptsize\\begin{tabular}{|l r r|}\n\hline\nInstitution & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffI:
		for i in range(len(stuffI[com])):
		  if len(stuffI[com][i][0]) < 30:
			f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffI[com][i][0], stuffI[com][i][1], stuffI[com][i][2]) )
		  else:
			aux = stuffI[com][i][0].rfind(' ')
			while aux > 30: 
			   aux = stuffI[com][i][0][0:aux].rfind(' ')
			f_out.write("%s &  & \\\\\n" % ( stuffI[com][i][0][0:aux] ) )
			f_out.write("$\quad$%s & %1.2f & %1.2f\\\\\n" % ( stuffI[com][i][0][aux:], stuffI[com][i][1], stuffI[com][i][2]) )
		for i in range(max(0,20-len(stuffI[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(20): f_out.write(" &  & \\\\\n")
	  #C
	  f_out.write("\hline\n\hline\nCountry & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffC:
		for i in range(len(stuffC[com])):
		  f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffC[com][i][0], stuffC[com][i][1], stuffC[com][i][2]) )
		for i in range(max(0,10-len(stuffC[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(10): f_out.write(" &  & \\\\\n")
	  #A
	  f_out.write("\hline\n\hline\nAuthor & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffA:
		for i in range(len(stuffA[com])):
		  f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffA[com][i][0], stuffA[com][i][1], stuffA[com][i][2]) )
		for i in range(max(0,10-len(stuffA[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(10): f_out.write(" &  & \\\\\n")
	  f_out.write("\hline\n\end{tabular}\n}\n")
	  #R
	  f_out.write("{\scriptsize\\begin{tabular}{|l r r|}\n\hline\nReference & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffR:
		for i in range(len(stuffR[com])):
		  if len(stuffR[com][i][0]) < 50:
			f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffR[com][i][0], stuffR[com][i][1], stuffR[com][i][2]) )
		  elif len(stuffR[com][i][0]) < 90:
			aux = stuffR[com][i][0].rfind(' ')
			while aux > 50: 
			   aux = stuffR[com][i][0][0:aux].rfind(' ')
			f_out.write("%s &  & \\\\\n" % ( stuffR[com][i][0][0:aux] ) )
			f_out.write("$\quad$%s & %1.2f & %1.2f\\\\\n" % ( stuffR[com][i][0][aux:], stuffR[com][i][1], stuffR[com][i][2]) )
		  else:
			aux1 = stuffR[com][i][0].rfind(' ')
			while aux1 > 90: 
			   aux1 = stuffR[com][i][0][0:aux1].rfind(' ')
			aux2 = stuffR[com][i][0][0:aux1].rfind(' ')
			while aux2 > 50: 
			   aux2 = stuffR[com][i][0][0:aux2].rfind(' ')
			f_out.write("%s &  & \\\\\n" % ( stuffR[com][i][0][0:aux2] ) )
			f_out.write("$\quad$%s &  & \\\\\n" % ( stuffR[com][i][0][aux2:aux1] ) )
			f_out.write("$\quad$%s & %1.2f & %1.2f\\\\\n" % ( stuffR[com][i][0][aux1:], stuffR[com][i][1], stuffR[com][i][2]) )
		for i in range(max(0,25-len(stuffR[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(25): f_out.write(" &  & \\\\\n")
	  #RJ
	  f_out.write("\hline\n\hline\nRefJournal & f(\\%) & $\sigma$\\\\\n\hline\n")
	  if com in stuffRJ:
		for i in range(len(stuffRJ[com])):
		  if len(stuffRJ[com][i][0]) < 50:
			f_out.write("%s & %1.2f & %1.2f\\\\\n" % ( stuffRJ[com][i][0], stuffRJ[com][i][1], stuffRJ[com][i][2]) )
		  else:
			aux = stuffRJ[com][i][0].rfind(' ')
			while aux > 50: 
			   aux = stuffRJ[com][i][0][0:aux].rfind(' ')
			f_out.write("%s &  & \\\\\n" % ( stuffRJ[com][i][0][0:aux] ) )
			f_out.write("$\quad$%s &  & \\\\\n" % ( stuffRJ[com][i][0][aux:] ) )
		for i in range(max(0,10-len(stuffRJ[com]))):
		  f_out.write(" &  & \\\\\n")
	  else:
		for i in range(10): f_out.write(" &  & \\\\\n")
	  f_out.write("\hline\n\end{tabular}\n}\n\end{table}\n\n")

  #.. end
  f_out.write("\end{landscape}\n\n\end{document}\n")
  f_out.close()
  if verbose: print"..Communities caracteristics extracted in .tex 'IDCards' file"

  ##############################
  ## OUTPUT GEPHI FILES

  #... output gephi
  if verbose: print "..Preparing gephi gdf file for BC communities network"

  ## ... ini
  name = "BC_comm_level%d(bcthr=%d, thr=%d).gdf" % (level,bcthr,thr)
  dst = os.path.join(out_dir, name)
  f_gephi = open(dst,'w')
  ## ... prep nodes
  if verbose: print "....nodes"
  f_gephi.write("nodedef>name VARCHAR,label VARCHAR,size DOUBLE,inv_innerweight DOUBLE\n")
  for com in comm_size:
	if comm_size[com] > thr: f_gephi.write("%d,'%s',%d,%1.0f\n" % (com, comm_label[com], comm_size[com], comm_innerw[com]) )	
  ## ... prep edges
  if verbose: print "....edges"
  f_gephi.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE,logweight DOUBLE\n")
  for com1 in list_nodes:
	for com2 in list_nodes:
	  size1 = len(list_nodes[com1]); size2 = len(list_nodes[com2]);
	  if size1 > thr and size2 > thr and com1 > com2:
		W = 0;
		for id1 in list_nodes[com1]:
		  for id2 in list_nodes[com2]:
			if id2 in G.edge[id1]: 
			  W += G.edge[id1][id2]['weight']
		W *= 1000.0 / (size1 * size2)
		if W > 0.000001:
		  f_gephi.write("%d,%d,%1.9f,%1.2f\n" % (com1, com2, W, 6 + math.log(W)/math.log(10)) ) 
  ## ... end
  f_gephi.close() 
  if verbose: print"..Done!\n"


  ##
  ##

  ##... output the BC networks?  
  confirm = raw_input("..There are %d articles in the BC network.\n....do you want to create a gephi file with the BC networks at the articles level? (y/n): " % (len(G.nodes())) )
  if confirm == 'y':
	## ... ini
	name = "BCnetwork(bcthr=%d, thr=%d).gdf" % (bcthr, thr)
	dst = os.path.join(out_dir, name)
	f_gephi = open(dst,'w')
	## ... prep nodes
	if verbose: print "....nodes"
	f_gephi.write("nodedef>name VARCHAR,label VARCHAR,BCcom VARCHAR,firstAU VARCHAR,journal VARCHAR,year VARCHAR,nb_refs DOUBLE\n")
	pl = Utils.Article()
	pl.read_file(src1)  
	for l in pl.articles:
	  if l.id in partition:
	    BCcom = partition[l.id]
	    if comm_size[BCcom] > thr:  
		  foo = l.firstAU + ', ' + l.journal + ', ' + str(l.year)
		  f_gephi.write("%d,'%s',%s,%s,%s,%d,%d\n" % (l.id, foo, str(BCcom), l.firstAU, l.journal,l.year,nR[l.id]) )  
	## ... prep edges
	if verbose: print "....edges"
	f_gephi.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE,nb_comm_refs DOUBLE")
	for i in BC_table:
		for j in BC_table[i]:
			if (i<j) and (i in partition) and (j in partition):
				comi_size = comm_size[partition[i]]
				comj_size = comm_size[partition[j]]
				if (comi_size > thr) and (comj_size > thr):
					w_ij = (1.0 * BC_table[i][j]) / math.sqrt(nR[i] * nR[j])
					f_gephi.write("\n%d,%d,%f,%d" % (i, j, w_ij, BC_table[i][j])) 
	## ... end
	f_gephi.close()
  if verbose: print"..Done!\n"


  ## ###################################
  ## END
  return

## ##################################################

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
# usage: BC.py [-h] [--version] -i DIR -o DIR[-v]
#
# optional arguments:
#   -h, --help			show this help message and exit
#   --version			 show program's version number and exit
#   -i DIR, --input_dir DIR input directory name
#   -g 
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

  BC_network(args.in_dir[0],args.out_dir[0],args.verbose)

  return


	
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
	main()

## ##################################################
## ##################################################
## ##################################################
