#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
   Copyright (C) 2012
   All rights reserved.
   BSD license.
"""

# usage: clean_institutions.py -i DIR -o DIR [-v]
# 

import os
import sys
import glob
import numpy
import argparse
import Utils
import inst_synonyms as ih

## ##################################################
## ##################################################
## ##################################################
def data_filter(in_dir,out_dir,verbose):

  ## INITIALIZATION

  src1  = os.path.join(in_dir, "articles.dat") 
  src2  = os.path.join(in_dir, "authors.dat")
  src3  = os.path.join(in_dir, "keywords.dat")
  src4  = os.path.join(in_dir, "subjects.dat")
  src5  = os.path.join(in_dir, "references.dat")
  src6  = os.path.join(in_dir, "countries.dat")
  src7  = os.path.join(in_dir, "institutions.dat")

  dst1  = os.path.join(out_dir, "articles.dat") 
  f_articles = open(dst1,'w')
  dst2  = os.path.join(out_dir, "authors.dat")
  f_authors = open(dst2,'w')
  dst3  = os.path.join(out_dir, "keywords.dat")
  f_keywords = open(dst3,'w')
  dst4  = os.path.join(out_dir, "subjects.dat")
  f_subjects = open(dst4,'w')
  dst5  = os.path.join(out_dir, "references.dat")
  f_refs = open(dst5,'w')
  dst6  = os.path.join(out_dir, "countries.dat")
  f_countries = open(dst6,'w')
  dst7  = os.path.join(out_dir, "institutions.dat")
  f_institutions = open(dst7,'w')
  dst8  = os.path.join(out_dir, "labos.dat")
  f_labos = open(dst8,'w')

  ##

  liste_labos = dict(); kompt_labos = dict();
  for labo in ih.list_labs:
    kompt_labos[labo] = dict()
    for l in ih.list_labs[labo]:
      lab = l.upper()
      kompt_labos[labo][lab]=0
      liste_labos[lab] = labo
  
  liste_autres_labos = dict();
  for labo in ih.other_institutions:
    for l in ih.other_institutions[labo]:
      liste_autres_labos[l.upper()] = labo

  ##

  pl = Utils.Article()
  pl.read_file(src1)  
  nb_art = len(pl.articles)

  ##

  labos_art =dict();

  ## OUTPUT SELECTED DATA
  if verbose: print "..creating output data"

  if 1==1:
      #article 
      if verbose: print "....copying articles"
      pl = Utils.Article()
      pl.read_file(src1)
      for l in pl.articles:
          f_articles.write("%d\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (l.id,l.firstAU,l.year,l.journal,l.volume,l.page,l.doi,l.pubtype,l.doctype,l.times_cited,l.title,l.uniqueID))
      #authors
      if verbose: print "....copying authors"
      pl = Utils.Author()
      pl.read_file(src2)
      for l in pl.authors:
          f_authors.write("%d\t%d\t%s\n" % (l.id,l.rank,l.author))
      #keywords
      if verbose: print "....copying keywords"
      pl = Utils.Keyword()
      pl.read_file(src3)
      for l in pl.keywords:
          f_keywords.write("%d\t%s\t%s\n" % (l.id,l.ktype,l.keyword))
      #subjects
      if verbose: print "....copying subjects"
      pl = Utils.Subject()
      pl.read_file(src4)
      for l in pl.subjects:
          f_subjects.write("%d\t%s\n" % (l.id,l.subject))
      #references
      if verbose: print "....copying references"
      pl = Utils.Ref()
      pl.read_file(src5)
      for l in pl.refs:
          f_refs.write("%d\t%s\t%d\t%s\t%s\t%s\n" % (l.id,l.firstAU,l.year,l.journal,l.volume,l.page))
      #countries 
      if verbose: print "....copying countries"
      pl = Utils.Country()
      pl.read_file(src6)
      for l in pl.countries:
          f_countries.write("%d\t%d\t%s\n" % (l.id,l.rank,l.country))
      #institutions
      if verbose: print "....cleaning institutions / extracting labs"
      pl = Utils.Institution()
      pl.read_file(src7)
      for l in pl.institutions:
        if l.institution in liste_labos:
          inst = liste_labos[l.institution]
          kompt_labos[inst][l.institution] += 1
          if l.id not in labos_art: labos_art[l.id]=[]
          if inst not in labos_art[l.id]: labos_art[l.id].append( inst ) 
        elif l.institution in liste_autres_labos:
          inst = liste_autres_labos[l.institution]
        else:
          inst = l.institution
        f_institutions.write("%d\t%d\t%s\n" % (l.id,l.rank,inst)) 
      #labos
      for art_id in labos_art:
        for inst in labos_art[art_id]:
          f_labos.write("%d\t%s\n" % (art_id, inst))


  ## output homonyms table

  f_hom = open("labos_homonyms.dat",'w')
  for labo in kompt_labos: 
    L_hom = kompt_labos[labo].items()
    L_hom.sort(cmpval)
    f_hom.write("%s\n--------\n" % (labo) )
    for elm in L_hom:
      f_hom.write("%s\t%d\n" % (elm[0],elm[1]) )
    f_hom.write("\n\n")
  f_hom.close()
 
  ## END
  if verbose: print "..Done!"

  f_articles.close()
  f_authors.close()
  f_keywords.close()
  f_subjects.close()
  f_refs.close()
  f_countries.close()
  f_institutions.close()
  f_labos.close()

  return

## #######################

def cmpval(x,y):
    if x[1]>y[1]:
        return -1
    elif x[1]==y[1]:
        return 0
    else:
        return 1

## ##################################################
## ##################################################
## ##################################################

def main():
# usage: filter.py [-h] [--version] -i DIR -o DIR [-v]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   --version             show program's version number and exit
#   -o DIR, --output_dir DIR  output directory name
#   -i DIR, --input_dir DIR input directory name

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

  data_filter(args.in_dir[0],args.out_dir[0],args.verbose)

  return


    
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
    main()

## ##################################################
## ##################################################
## ##################################################

