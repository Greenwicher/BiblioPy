#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
			Liu Weizhi (http://greenwicher.github.io/)
   Copyright (C) 2014
   All rights reserved.
   BSD license.
"""

# usage: first_distrib.py -i DIR [-v]
# 

import os
import sys
import glob
import numpy
import argparse
import matplotlib.pyplot as plt
import Utils

## ##################################################
## ##################################################
## ##################################################
def first_distrib(in_dir,verbose):

  ## INITIALIZATION

  src1  = os.path.join(in_dir, "articles.dat") 
  src2  = os.path.join(in_dir, "authors.dat")
  src3  = os.path.join(in_dir, "keywords.dat")
  src4  = os.path.join(in_dir, "subjects.dat")
  src5  = os.path.join(in_dir, "references.dat")
  src6  = os.path.join(in_dir, "countries.dat")
  src7  = os.path.join(in_dir, "institutions.dat")

  dst1  = os.path.join(in_dir, "proba_years.dat")
  f_years = open(dst1,'w')
  dst1b  = os.path.join(in_dir, "proba_journals.dat")
  f_journals = open(dst1b,'w')
  dst2  = os.path.join(in_dir, "proba_authors.dat")
  f_authors = open(dst2,'w')
  dst3  = os.path.join(in_dir, "proba_keywords.dat")
  f_keywords = open(dst3,'w')
  dst4  = os.path.join(in_dir, "proba_subjects.dat")
  f_subjects = open(dst4,'w')
  dst5  = os.path.join(in_dir, "proba_references.dat")
  f_refs = open(dst5,'w')
  dst5b  = os.path.join(in_dir, "proba_refJournals.dat")
  f_jrefs = open(dst5b,'w')
  dst6  = os.path.join(in_dir, "proba_countries.dat")
  f_countries = open(dst6,'w')
  dst7  = os.path.join(in_dir, "proba_institutions.dat")
  f_institutions = open(dst7,'w')




  ## CREATE HETEROGENEOUS TABLE
  if verbose: print "..creating tables"
 
  het_table = dict();
  Y_table = dict();


  pl = Utils.Article()
  pl.read_file(src1)  
  nb_art = len(pl.articles) # store the number of articles within database
  for l in pl.articles:
      if (l.year > 1900 and l.year < 2100): 
          Y_table[l.id] = l.year # store the publication year of each article
          if ('Y',l.year) in het_table: het_table[('Y',l.year)].append( l.id )
          else: het_table[('Y',l.year)] = [l.id]
          if ('J',l.journal) in het_table: het_table[('J',l.journal)].append( l.id )
          else: het_table[('J',l.journal)] = [l.id]

  pl = Utils.Author()
  pl.read_file(src2)  
  for l in pl.authors:
      if ('A',l.author) in het_table: het_table[('A',l.author)].append( l.id )
      else: het_table[('A',l.author)] = [l.id]

  pl = Utils.Keyword()
  pl.read_file(src3)  
  for l in pl.keywords:
      if (l.ktype == 'AK'): # changed from IK to AK
          if ('K',l.keyword) in het_table: het_table[('K',l.keyword)].append( l.id )
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

  ## OUTPUT PROBA TABLES
  if verbose: print "..nb_art = %d" % (nb_art) 
  if verbose: print "..output 'proba_*.dat' tables"

  #create and sort lists
  Y_list = []
  J_list = []
  A_list = []
  K_list = []
  S_list = []
  R_list = []
  RJ_list = []
  I_list = []
  C_list = []
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
  Y_list.sort(cmpval0)
  J_list.sort(cmpval)
  A_list.sort(cmpval)
  K_list.sort(cmpval)
  S_list.sort(cmpval)
  R_list.sort(cmpval)
  RJ_list.sort(cmpval)
  I_list.sort(cmpval)
  C_list.sort(cmpval)
  #output
  for (x,v) in Y_list:
      f_years.write("%d\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in J_list:
      f_journals.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in A_list:
      f_authors.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in K_list:
      f_keywords.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in S_list:
      f_subjects.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in R_list:
      f_refs.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in RJ_list:
      f_jrefs.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in I_list:
      f_institutions.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))
  for (x,v) in C_list:
      f_countries.write("%s\t%d\t%1.4f\n" % (x,v,1.0*v/nb_art))

  ## close the created files
  f_years.close()
  f_journals.close()
  f_authors.close()
  f_keywords.close()
  f_subjects.close()
  f_refs.close()
  f_jrefs.close()
  f_countries.close()
  f_institutions.close()


  ## PLOT DISTRIB
  if verbose: print "..plot distrib"

  xxY = []
  yyY = []
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


  fig = plt.figure()
  fig.subplots_adjust(wspace=0.3,hspace=0.5)
  fig.suptitle('Total number of Articles: %d, Journals: %d, Authors: %d, Keywords: %d, Subjects: %d,\n Refs: %d, Refs Journals: %d, Institutions: %d, Countries: %d' % (nb_art, len(J_list), len(A_list), len(K_list), len(S_list), len(R_list), len(RJ_list), len(I_list), len(C_list)))

  im1 = fig.add_subplot(221)
# plt.xlabel('')
  plt.ylabel('# of articles')
  plt.plot(xxY,yyY,'o-')
# im1.set_title("# of articles / publication year")
  im1.grid(True)

  im2 = fig.add_subplot(222)
  plt.xlabel('times_used')
  plt.ylabel('% of items')
  plt.loglog(xx,yyJ*1.0/len(J_list),'o',xx,yyI*1.0/len(I_list),'o',xx,yyK*1.0/len(K_list),'o',xx,yyR*1.0/len(R_list),'o')
  im2.legend(('Journals', 'Institutions', 'Keywords', 'Refs'), 'upper right', shadow=True, numpoints=1)
# im2.set_title("distributions ")
  im2.grid(True)

  im3 = fig.add_subplot(223)
  plt.xlabel('times_used')
  plt.ylabel('% of items')
  plt.loglog(xrj,yyRJ*1.0/len(RJ_list),'o',label='Refs Journals')
  im3.legend(loc='upper right', shadow=True, numpoints=1)
# im3.set_title("distributions ")
  im3.grid(True)

  im4 = fig.add_subplot(224)
  plt.xlabel('times_used')
  plt.ylabel('% of items')
  plt.loglog(xx,yyA*1.0/len(A_list),'o',xx,yyS*1.0/len(S_list),'o',xx,yyC*1.0/len(C_list),'o')
  im4.legend(('Authors', 'Subjects', 'Countries'), 'upper right', shadow=True, numpoints=1)
# im4.set_title("distributions ")
  im4.grid(True)
    
  plt.show()

  ## END
  return

## ##################################################
## ##################################################
## ##################################################
def cmpval0(x,y):
    if x[0]>y[0]:
        return -1
    elif x[0]==y[0]:
        return 0
    else:
        return 1

def cmpval(x,y):
    if x[1]>y[1]:
        return -1
    elif x[1]==y[1]:
        return 0
    else:
        return 1

## ##################################################

def main():
# usage: first_distrib.py [-h] [--version] -i DIR [-v]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   --version             show program's version number and exit
#   -i DIR, --input_dir DIR input directory name
#   -r 
  # Parse line options.
  # Try to have always the same input options
  parser = argparse.ArgumentParser(description = 'parser')

  parser.add_argument('--version', action='version', version='%(prog)s 1.1')
  
  parser.add_argument("-i", "--input_dir", nargs=1, required=True,
          action = "store", dest="in_dir",
          help="input directory name",
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

  ##      

  first_distrib(args.in_dir[0],args.verbose)

  return


    
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
    main()

## ##################################################
## ##################################################
## ##################################################
