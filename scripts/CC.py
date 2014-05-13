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
import Utils, CCUtils
import networkx as nx
import numpy as np
import community
import matplotlib.pyplot as plt
import report


def CC_network(in_dir, out_dir, verbose):
	
	## INPUT DATA
	if verbose: print "..Initialize"
	src1 = os.path.join(in_dir, "articles.dat")
	src5 = os.path.join(in_dir, "references.dat")
	
	# processing references' journal 
	ref_journal_dict = {'JOM':['J OPER MANA IN PRESS', 'J OPER MANAG', 'J OPER MANAG FORTHCO', 'J OPERATIONS MANAGE',
	                   'J OPERATIONS MANAGEM', 'J. Oper. Manag.', 'Journal of Operations Management', 'JOM'], 
					   'M&SOM':['M&SOM-MANUF SERV OP', 'MANUF SERV IN PRESS', 'MANUF SERV OPER MANA', 'MANUF SERV OPERAT MA',
					   'MANUF SERVICE OPERAT', 'Manufacturing & Service Operations Management', 'MANUFACTURING SERVIC', 'M&SOM'],
					   'POM': ['PROD OPER M IN PRESS', 'PROD OPER MANAG', 'PROD OPERAT MANAGEM', 'Production and Operations Management', 
					   'PRODUCTION OPER MANA', 'Production Oper. Management', 'PRODUCTION OPERATION', 'PRODUCTIONS OPERATIO', 'POM']}
	ref_journal_list = [v for k in ref_journal_dict for v in ref_journal_dict[k]]
	
	Ymin = 2100; Ymax = 1900
	pl = Utils.Article()
	pl.read_file(src1)
	nb_art = len(pl.articles)
	art_table = dict()
	for i in range(nb_art):
		art_table[i] = []
	doc_table = dict()
	id = 0
	for l in pl.articles:
		doc_table[id] = dict()
		doc_table[id]['firstAU'] = l.firstAU
		doc_table[id]['year'] = l.year 
		doc_table[id]['journal'] = l.journal
		doc_table[id]['citation'] = l.times_cited
		doc_table[id]['title'] = l.title
		doc_table[id]['de_keywords'] = l.de_keywords
		doc_table[id]['id_keywords'] = l.id_keywords
		doc_table[id]['abstract'] = l.abstract
		id = id + 1
		
	for l in pl.articles:
		if (l.year > 1900 and l.year < 2000):
			if(l.year > Ymax): Ymax = l.year
			if(l.year < Ymin): Ymin = l.year
			
	if verbose: print "..Create Co-citation Network weight table"
	
	if verbose: print "....loading refs table"
	pl = Utils.Ref()
	pl.read_file(src5)
	nb_total_refs = len(pl.refs)
	CC_table = dict()
	nA = dict()
	nA_given_journals = dict()
	ref_index = dict()
	for l in pl.refs:
		foo = l.firstAU + ', ' + str(l.year) + ', ' + l.journal + ', ' + l.volume + ', ' + l.page 
		if l.refid not in ref_index:
			ref_index[l.refid] = dict()
			ref_index[l.refid]['firstAU'] = l.firstAU
			ref_index[l.refid]['year'] = l.year
			# transform the references' journal to their standard abbreviation
			if l.journal in ref_journal_list:
				for foo in ref_journal_dict:
					if l.journal in ref_journal_dict[foo]:
						l.journal = foo
			ref_index[l.refid]['journal'] = l.journal
			ref_index[l.refid]['volume'] = l.volume
			ref_index[l.refid]['page'] = l.page
			ref_index[l.refid]['doi'] = l.doi
			ref_index[l.refid]['article'] = []
			ref_index[l.refid]['SubCommID'] = -1
			ref_index[l.refid]['modularity'] = -1
		ref_index[l.refid]['article'].append(l.id)
		art_table[l.id].append(l.refid)
		if l.refid not in nA: 
			nA[l.refid] = 1
			if l.journal in ref_journal_list:
				nA_given_journals[l.refid] = l
		else: nA[l.refid] += 1
	nb_refs = len(nA)
	nb_given_journals_refs = len(nA_given_journals)
	
	if verbose: print "....detect common articles"
	for foo in art_table:
		if(len(art_table[foo]) > 1):
			for i in art_table[foo]:
				for j in art_table[foo]:
					if(i<j):
						if i not in CC_table: CC_table[i] = dict()
						if j not in CC_table[i]: CC_table[i][j] = 0
						CC_table[i][j] += 1
		
	
	# choose threshold
	confirm = 'n'; ccthr=5;
  
	while confirm != 'y':
		if ccthr == 1: print "Keep BC links between articles sharing at least %d reference" % (ccthr)
		else: print "Keep BC links between articles sharing at least %d references" % (ccthr)
		confirm = raw_input("Confirm (y/n): ")
		while confirm not in ['n','y']:
			confirm = raw_input("...typing error!\n Confirm (y/n): ")
		if confirm == 'n':
			ccthr = input("threshold for BC links -- articles should be share at least ? references:")

	confirm = 'n'; 
	ref_journal_flag = False
	print "Do you want the journal of references belong to the list below?"
	for foo in ref_journal_list:
		print foo
	confirm = raw_input("Confirm (y/n): ")
	while confirm not in ['n', 'y']:
		confirm = raw_input("...typing error!\n Confirm (y/n): ")
	if confirm == 'y':
		ref_journal_flag = True
	
	
	##############################
	## BC COMMUNITIES
	if verbose: print "..CC communities"
	#... define BC network
	if verbose: print "....define graph in networkx format"
	G=nx.Graph()
	for i in CC_table:
		for j in CC_table[i]:
			if ((not ref_journal_flag) or (ref_journal_flag and ref_index[i]['journal'] in ref_journal_list and ref_index[j]['journal'] in ref_journal_list)) and (CC_table[i][j]>=ccthr):
				w_ij = (1.0 * CC_table[i][j]) / math.sqrt(nA[i] * nA[j])
				G.add_edge(i, j, weight=w_ij)
	
	#... calculate basic centrality for each node
	if verbose: print "..calculate basic centrality for each node"
	degree = nx.degree_centrality(G)
	closeness = nx.closeness_centrality(G)
	betweenness =  nx.betweenness_centrality(G)
	
	#...
	if verbose: print "....computing communities with Louvain algo"
	dendogram = community.generate_dendogram(G, part_init=None)

	#... output infos
	print "....There are %d references in the database (contain duplicates)" % (nb_total_refs)
	print "....There are %d references in the database (contain no duplicate)" % (nb_refs)
	print "....There are %d references in the given journals (contain no duplicate)" % (nb_given_journals_refs)
	print "....There are %d references in the CC network\n......(ie sharing at least %d article(s) with another reference)" % (len(G.nodes()), ccthr)
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
	print "..CC communities extraction"
	#
	confirm = 'n'; level = len(dendogram) - 1; thr = 0
	while confirm != 'y':
		part = community.partition_at_level(dendogram, level)
		nb_comm = len(set(part.values()))
		size_sup_thr = 0; n_sup_thr = 0;
		for com in set(part.values()) :
			list_nodes = [nodes for nodes in part.keys() if part[nodes] == com]
			if len(list_nodes) > thr: 
				n_sup_thr += len(list_nodes)
				size_sup_thr += 1
		print "....Extraction of level %d CC communities with size > %d\n......(%d articles gathered in %d communities):" % (level, thr, n_sup_thr, size_sup_thr)
		confirm = raw_input("....do you confirm? (y/n): ")
		if confirm == 'n':
			level  = input("......level you want to extract:")
			thr  = input("......keep communities of size > to:")
	# plot Co-citation after filtering (ccthr, ref_journal)
	nx.draw_spring(G)
	dst = os.path.join(out_dir, 'CC-Network(ccthr=%d, thr=%d, ref_journal_flag=%s).png' % (ccthr, thr, ref_journal_flag))
	plt.savefig(dst)
	plt.close('all')

	#... partition
	partition = community.partition_at_level(dendogram, level)
	list_nodes= dict();
	for com in set(partition.values()) :
		list_nodes[com] = [nodes for nodes in partition.keys() if partition[nodes] == com]

	
	#############################
	# sub-community partition
	subcomm = dict()
	for com in list_nodes:
		# plot SubGraph for each community
		if verbose: print "....plot SubGraph for community %d" % (com)
		subG = nx.subgraph(G, list_nodes[com])
		# partition
		if verbose: print "....sub clustering for community %d" % (com)
		part = community.best_partition(subG) 
		# plot SubGraph relationships network
		node_color = [part[v] for v in subG]
		node_size = [nA[v]*30 for v in subG]
		labels = dict()
		for refid in subG:
			foo = ref_index[refid]['firstAU'] + ', ' + ref_index[refid]['journal'] + ', ' + str(ref_index[refid]['year'])
			labels[refid] = foo
		width = []
		for e in subG.edges():
			i = e[0]
			j = e[1]
			if i>j:
				tmp = i
				i = j
				j = tmp
			w_ij = (1.0 * CC_table[i][j]) / math.sqrt(nA[i] * nA[j]) * 10
			width.append(w_ij)
		nx.draw_spring(subG, node_color=node_color, node_size=node_size, labels=labels, font_size=8)
		#nx.draw_spring(subG, node_color=node_color, node_size=node_size, width=width)
		dst = os.path.join(out_dir, 'SubGraph/Plot/SubGraph-%d.png' % (com))
		plt.savefig(dst)
		plt.close('all')
		# basic descriptive statistics
		comm_size = len(subG.nodes())
		nb_comm = len(set(part.values()))
		subcomm[com] = dict()
		subcomm[com]['nb_comm'] = nb_comm
		subcomm[com]['size'] = comm_size
		mod = community.modularity(part, subG)
		# record each node's sub community id
		for refid in part.keys():
			ref_index[refid]['SubCommID'] = part[refid]
			ref_index[refid]['modularity'] = mod
		if verbose: print "......comm_size:%d, nb_comm:%d, modularity:%1.6f" % (comm_size, nb_comm, mod)
		# output gephi files
		if verbose: print "......generate gephi files for sub-community %d" % (com)
		name = "SubGraph/Gephi/SubCCnetwork%d(ccthr=%d, thr=%d, ref_journal_flag=%s).gdf" % (com, ccthr, thr, ref_journal_flag)
		dst = os.path.join(out_dir, name)
		f_gephi = open(dst, 'w')
		# nodes
		f_gephi.write("nodedef>name VARCHAR,label VARCHAR,CCcom VARCHAR, Sub CCcom VARCHAR, Modularity VARCHAR, firstAU VARCHAR,journal VARCHAR,year VARCHAR,nb_arts DOUBLE,doi VARCHAR, volume VARCHAR, page VARCHAR\n") 		
		for refid in part.keys():
			foo = ref_index[refid]['firstAU'] + ', ' + ref_index[refid]['journal'] + ', ' + str(ref_index[refid]['year'])	
			f_gephi.write("%d,'%s',%s,%s,%1.6f,%s,%s,%d,%d,%s,%s,%s\n" % (refid, foo, str(com), str(ref_index[refid]['SubCommID']), ref_index[refid]['modularity'], ref_index[refid]['firstAU'], ref_index[refid]['journal'],ref_index[refid]['year'],nA[refid], ref_index[refid]['doi'], ref_index[refid]['volume'], ref_index[refid]['page'])) 
		# edges
		f_gephi.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE,nb_comm_refs DOUBLE\n")
		for i in part.keys():
			for j in part.keys():
				if(i<j):
					if i in CC_table:
						if j in CC_table[i]:
							if (CC_table[i][j]>=ccthr):
								w_ij = (1.0 * CC_table[i][j]) / math.sqrt(nA[i] * nA[j])
								f_gephi.write("%d,%d,%f,%d\n" % (i, j, w_ij, CC_table[i][j])) 
		# end
		f_gephi.close()

		
	#.. comm_size
	comm_size = dict(); 
	for com in list_nodes:
		size = len(list_nodes[com])
		comm_size[com] = size
		
	# sort community by its size
	comm_size = dict(); 
	for com in list_nodes:
		size = len(list_nodes[com])
		comm_size[com] = size
	Lcomm_size = comm_size.items()
	Lcomm_size.sort(cmpval)
	
	##############################
	# Research Base CSV files
	if verbose: print "..Research Base CSV files generating"
	filename = os.path.join(out_dir, "ResearchBase.dat")
	f_out = open(filename, "w")
	# header line
	f_out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ('CommunityID', 'SubCommunityID', 'Modularity', 'Topic', 'SubTopic', 'RefID', 'Volume', 'Page', 'Lable', 'Title', 'Keywords', 'firstAU', 'Journal', 'Year', 'Citation', 'DOI', 'Degree', 'Closeness', 'Betweenness'))
	for elm in Lcomm_size:
		com = elm[0]
		for ref in list_nodes[com]:
			foo = ref_index[ref]['firstAU'] + ', ' + ref_index[ref]['journal'] + ', ' + str(ref_index[ref]['year'])
			f_out.write("%s\t%s\t%1.6f\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%1.6f\t%1.6f\t%1.6f\n" % (str(com), str(ref_index[ref]['SubCommID']), ref_index[ref]['modularity'], '', '', str(ref), str(ref_index[ref]['volume']), str(ref_index[ref]['page']), foo, '', '', ref_index[ref]['firstAU'], ref_index[ref]['journal'], str(ref_index[ref]['year']), str(nA[ref]), ref_index[ref]['doi'], degree[ref], closeness[ref], betweenness[ref]))
	f_out.close()
	if verbose: print "..Done!\n"	
	
	
	
	##############################
	# Research Front CSV files
	if verbose: print "..Research Front CSV files generating"
	filename = os.path.join(out_dir, "ResearchFront.dat")
	f_out = open(filename, "w")
	# header line
	f_out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ('CommunityID', 'SubCommunityID', 'RefID', 'DocID', 'DocLable', 'Title', 'Year', 'Citation', 'DE-Keywords', 'ID-Keywords', 'Abstract'))
	for elm in Lcomm_size:
		com = elm[0]	
		for ref in list_nodes[com]:
			for doc in ref_index[ref]['article']:
				foo = doc_table[doc]['firstAU'] + ', ' + doc_table[doc]['journal'] + ', ' + str(doc_table[doc]['year']) 
				f_out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (str(com), str(ref_index[ref]['SubCommID']), str(ref), str(doc), foo, doc_table[doc]['title'], str(doc_table[doc]['year']), str(doc_table[doc]['citation']), doc_table[doc]['de_keywords'], doc_table[doc]['id_keywords'], doc_table[doc]['abstract']))
	f_out.close()
	if verbose: print "..Done!\n"
				
	
	#############################
	# OUTPUT GEPHI FILES

	#... output gephi
	# if verbose: print "..Preparing gephi gdf file for CC communities network"

	# ... ini
	# name = "CC_comm_level%d(ccthr=%d, thr=%d, ref_journal_flag=%s).gdf" % (level,ccthr,thr,ref_journal_flag)
	# dst = os.path.join(out_dir, name)
	# f_gephi = open(dst,'w')
	# ... prep nodes
	# if verbose: print "....nodes"
	# f_gephi.write("nodedef>name VARCHAR,label VARCHAR,size DOUBLE,inv_innerweight DOUBLE\n")
	

		
	# for com in comm_size:
		# if (comm_size[com] > thr) and (com in comm_label): f_gephi.write("%d,'%s',%d,%1.0f\n" % (com, comm_label[com], comm_size[com], comm_innerw[com]) )	
	# ... prep edges
	# if verbose: print "....edges"
	# f_gephi.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE,logweight DOUBLE\n")
	# for com1 in list_nodes:
		# for com2 in list_nodes:
			# size1 = len(list_nodes[com1]); size2 = len(list_nodes[com2]);
			# if size1 > thr and size2 > thr and com1 > com2:
				# W = 0;
				# for id1 in list_nodes[com1]:
					# for id2 in list_nodes[com2]:
						# if id2 in G.edge[id1]: 
							# W += G.edge[id1][id2]['weight']
				# W *= 1000.0 / (size1 * size2)
				# if W > 0.000001:
					# f_gephi.write("%d,%d,%1.9f,%1.2f\n" % (com1, com2, W, 6 + math.log(W)/math.log(10)) ) 
	# ... end
	# f_gephi.close() 
	# if verbose: print"..Done!\n"


	##
	##

	##... output the CC networks?  
	confirm = raw_input("..There are %d articles in the CC network.\n....do you want to create a gephi file with the CC networks at the articles level? (y/n): " % (len(G.nodes())) )
	if confirm == 'y':
		## ... ini
		name = "CCnetwork(ccthr=%d, thr=%d, ref_journal_flag=%s).gdf" % (ccthr, thr, ref_journal_flag)
		dst = os.path.join(out_dir, name)
		f_gephi = open(dst,'w')
		## ... prep nodes
		if verbose: print "....nodes"
		f_gephi.write("nodedef>name VARCHAR,label VARCHAR,CCcom VARCHAR, Sub CCcom VARCHAR, Modularity VARCHAR, firstAU VARCHAR,journal VARCHAR,year VARCHAR,nb_arts DOUBLE,doi VARCHAR, volume VARCHAR, page VARCHAR\n") 
		for refid in ref_index:
			if refid in partition: 
				CCcom = partition[refid]
				if comm_size[CCcom] > thr:
					foo = ref_index[refid]['firstAU'] + ', ' + ref_index[refid]['journal'] + ', ' + str(ref_index[refid]['year'])
					f_gephi.write("%d,'%s',%s,%s,%1.6f,%s,%s,%d,%d,%s,%s,%s\n" % (refid, foo, str(CCcom), str(ref_index[refid]['SubCommID']), ref_index[refid]['modularity'], ref_index[refid]['firstAU'], ref_index[refid]['journal'],ref_index[refid]['year'],nA[refid], ref_index[refid]['doi'], ref_index[refid]['volume'], ref_index[refid]['page'])) 
		## ... prep edges
		if verbose: print "....edges"
		f_gephi.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE,nb_comm_refs DOUBLE\n")
		for i in CC_table:
			for j in CC_table[i]:
				if (i<j) and (i in partition) and (j in partition) and (CC_table[i][j]>=ccthr):
					commi_size = comm_size[partition[i]]
					commj_size = comm_size[partition[j]]
					if (commi_size > thr) and (commj_size > thr):
						w_ij = (1.0 * CC_table[i][j]) / math.sqrt(nA[i] * nA[j])
						f_gephi.write("%d,%d,%f,%d\n" % (i, j, w_ij, CC_table[i][j])) 
		## ... end
		f_gephi.close()
		if verbose: print"..Done!\n"
		
	##############################
	# Main Community Characteristics file
	type = "main"
	confirm = raw_input("..Do you want to extract the characteristics for main communitise? \n Confirm (y/n):")
	if confirm =='y':
		label = report.community_characteristics(in_dir,out_dir,type,ccthr,thr,ref_journal_flag,G,level,partition,list_nodes,art_table,doc_table,ref_index,verbose)

	##############################
	# Sub Community Characteristics files	
	if verbose: print"..Sub Computing communities caracteristics"
	confirm = raw_input("..Do you want to extract the characteristics for sub communitise? \n Confirm (y/n):")
	if confirm =='y':
		sub_label = dict()
		for com in list_nodes:
			type = str(com)
			subG = nx.subgraph(G, list_nodes[com])
			level = len(community.generate_dendogram(subG)) - 1
			sub_partition = community.best_partition(subG) 
			sub_list_nodes = dict()
			for ref in sub_partition:
				sub_comm = sub_partition[ref]
				if sub_comm not in sub_list_nodes:
					sub_list_nodes[sub_comm] = []
				sub_list_nodes[sub_comm].append(ref)
			sub_label[com] = report.community_characteristics(in_dir,out_dir,type,ccthr,thr,ref_journal_flag,subG,level,sub_partition,sub_list_nodes,art_table,doc_table,ref_index,verbose,label)
	##############################
	# Community Characteristics PDF generation
	confirm = raw_input("..Do you want to generate the pdf files of characteristics for communitise? \n Confirm (y/n):")
	if confirm == 'y':
		report.latex(os.path.join(out_dir, "Report"), verbose)
		


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
# usage: CC.py [-h] [--version] -i DIR -o DIR[-v]
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

  CC_network(args.in_dir[0],args.out_dir[0],args.verbose)

  return


	
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
	main()

## ##################################################
## ##################################################
## ##################################################

