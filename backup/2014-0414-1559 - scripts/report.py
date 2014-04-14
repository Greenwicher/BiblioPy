#! /usr/bin/env python
""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
            Liu Weizhi (http://greenwicher.github.io/)
   Copyright (C) 2014
   All rights reserved.
   BSD license.
"""
import os
import glob
from subprocess import call
import CCUtils

def community_characteristics(in_dir,out_dir,type,ccthr,thr,ref_journal_flag,G,level,partition,list_nodes,art_table,verbose,label={}):
    ##############################
	## Main COMMUNITIES CARACTERISTICS
	if verbose and type=="main": print "..Computing Main Communities Caracteristics"
	if verbose and type!="main": print "..Computing Sub Community %s Characteristics" % (type)

	#.. ini
	if type=="main":
		filename = os.path.join(out_dir, "Report/CCcomm_ID_Cards(ccthr=%d, thr=%d, ref_journal_flag=%s).tex" % (ccthr, thr, ref_journal_flag))
	else:
		filename = os.path.join(out_dir, "Report/Community%s - %s.tex" % (type, label[int(type)]))
	f_out = open(filename,"w")
	f_out.write("\documentclass[a4paper,11pt]{report}\n\usepackage[english]{babel}\n\usepackage[latin1]{inputenc}\n\usepackage{amsfonts,amssymb,amsmath}\n\usepackage{pdflscape}\n\usepackage{color}\n\n\\addtolength{\evensidemargin}{-60pt}\n\\addtolength{\oddsidemargin}{-60pt}\n\\addtolength{\\textheight}{80pt}\n\n\\title{{\\bf Communities ID Cards}}\n\date{\\begin{flushleft}This document gather the ``ID Cards'' of the CC communities found within your database.\\\\\n The CC network was built by keeping a link between articles sharing at least %d references. The communities characterized here correspond to the ones found in the level %d (in the sense of the Louvain algo) which gathers more than %d articles.\\\\\n These ID cards displays the most frequent keywords, subject categories, journals of publication, institution, countries, authors, references and reference journals of the articles of each community. The significance of an item $\sigma = \sqrt{N} (f - p) / \sqrt{p(1-p)}$ [where $N$ is the number of articles within the community and $f$ and $p$ are the proportion of articles respectively within the community and within the database displaying that item ] is also given (for example $\sigma > 5$ is really highly significant).\\\\\n\\vspace{1cm}\n\copyright Sebastian Grauwin, Liu Weizhi - (2014) \end{flushleft}}\n\n\\begin{document}\n\\begin{landscape}\n\maketitle\n" % (ccthr, level, thr))


	#.. quantitative
	comm_innerw = dict(); comm_size = dict(); 
	for com in list_nodes:
		size = len(list_nodes[com])
		W = 0;
		for id1 in list_nodes[com]:
			for id2 in list_nodes[com]:
				if id2 > id1 and id2 in G.edge[id1]: 
					W += G.edge[id1][id2]['weight']
		if size!=1 and size!=0:
			W *= 2.0 / (size * (size -1))
		if W!=0: 
			comm_innerw[com] = 1.0 / W
		else:
			comm_innerw[com] = -9999
		comm_size[com] = size
	Lcomm_size = comm_size.items()
	Lcomm_size.sort(cmpval)

	#.. frequency / significance of keywords, etc...
	comm_label = dict();
	(stuffK, stuffS, stuffJ, stuffA, stuffI, stuffC, stuffR, stuffRJ) = CCUtils.comm_tables(in_dir,partition,art_table,thr,verbose)
	
	#.. output tables
	for elm in Lcomm_size:
		if elm[1] > thr:
			com = elm[0]
			#K
			if com in stuffK:
				if len(stuffK[com]) > 0 : comm_label[com] = stuffK[com][0][0].replace('/', '-').replace('\\', '-')
				else: comm_label[com] = 'XXXX'
				f_out.write("\clearpage\n\n\\begin{table}[!ht]\n\caption{The community %d - ``%s'' contains $N = %d$ articles. Its average internal link weight is $<\omega_{in}> \simeq 1/%d$ }\n\\textcolor{white}{aa}\\\\\n{\scriptsize\\begin{tabular}{|l r r|}\n\hline\nKeyword & f(\\%%) & $\sigma$\\\\\n\hline\n" % (com, comm_label[com], comm_size[com], comm_innerw[com] ) )
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
				f_out.write("\clearpage\n\n\\begin{table}[!ht]\n\caption{The community %d - ``?'' contains $N = %d$ articles. Its average internal link weight is $<\omega_{in}> \simeq 1/%d$ }\n\\textcolor{white}{aa}\\\\\n{\scriptsize\\begin{tabular}{|l r r|}\n\hline\nKeyword & f(\\%%) & $\sigma$\\\\\n\hline\n" % (com, comm_size[com], comm_innerw[com] ) )
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
	if verbose and type=="main": print "..Main Community Done!\n"
	if verbose and type!="main": print "..Community %s Done!\n" % (type)
	return (comm_label)
	
def latex(in_dir, verbose):
	os.chdir(in_dir)
	print os.getcwd()
	srccomp = "*.tex"
	srclst = glob.glob(srccomp)
	for src in srclst:
		call(['pdflatex', src])
		os.remove(src.replace('.tex', '')+'.aux')
		os.remove(src.replace('.tex', '')+'.log')
		if verbose:
			print "%s has been trafomed into pdf fles!" % (src)
	
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
