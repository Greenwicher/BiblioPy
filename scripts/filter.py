#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
   Copyright (C) 2012
   All rights reserved.
   BSD license.
   .... If you are using these scripts, please cite our "Scientometrics" paper:
   .... S Grauwin, P Jensen, Mapping Scientific Institutions. Scientometrics 89(3), 943-954 (2011)
"""

# usage: filter.py -i DIR -o DIR -y1 INT -y2 INT [-v]
# 
# this script filters "parsed data", extracts the data corresponding to articles published between years y1 and y2 and put them in an output directory 
#

import os
import sys
import glob
import numpy
import argparse
import Utils

## ##################################################
## ##################################################
## ##################################################
def data_filter(in_dir,out_dir,ymin,ymax,verbose):

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

  selection = []

  pl = Utils.Article()
  pl.read_file(src1)  
  nb_art = len(pl.articles)


  ## SELECT ID
  if verbose:
      print "selecting articles to keep "

  if (ymin > 1500 or ymax < 2100):
      pl = Utils.Article()
      pl.read_file(src1)
      for art in pl.articles:
          if (art.year <= ymax) and (art.year >= ymin): selection.append( art.id )


  ## OUTPUT SELECTED DATA
  if verbose:
      print "creating output data"

  if len(selection) > 0:
      #article 
      if verbose: print "(1/7) filtering articles"
      pl = Utils.Article()
      pl.read_file(src1)
      for l in pl.articles:
          if l.id in selection: f_articles.write("%d\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (l.id,l.firstAU,l.year,l.journal,l.volume,l.page,l.doi,l.pubtype,l.doctype,l.times_cited,l.title,l.uniqueID))
      #authors
      if verbose: print "(2/7) filtering authors"
      pl = Utils.Author()
      pl.read_file(src2)
      for l in pl.authors:
          if l.id in selection: f_authors.write("%d\t%d\t%s\n" % (l.id,l.rank,l.author))
      #keywords
      if verbose: print "(3/7) filtering keywords"
      pl = Utils.Keyword()
      pl.read_file(src3)
      for l in pl.keywords:
          if l.id in selection: f_keywords.write("%d\t%s\t%s\n" % (l.id,l.ktype,l.keyword))
      #subjects
      if verbose: print "(4/7) filtering subjects"
      pl = Utils.Subject()
      pl.read_file(src4)
      for l in pl.subjects:
          if l.id in selection: f_subjects.write("%d\t%s\n" % (l.id,l.subject))
      #references
      if verbose: print "(5/7) filtering references"
      pl = Utils.Ref()
      pl.read_file(src5)
      for l in pl.refs:
          if l.id in selection: f_refs.write("%d\t%s\t%d\t%s\t%s\t%s\n" % (l.id,l.firstAU,l.year,l.journal,l.volume,l.page))
      #countries 
      if verbose: print "(6/7) filtering countries"
      pl = Utils.Country()
      pl.read_file(src6)
      for l in pl.countries:
          if l.id in selection: f_countries.write("%d\t%d\t%s\n" % (l.id,l.rank,l.country))
      #institutions
      if verbose: print "(7/7) filtering institutions"
      pl = Utils.Institution()
      pl.read_file(src7)
      for l in pl.institutions:
          if l.id in selection: f_institutions.write("%d\t%d\t%s\n" % (l.id,l.rank,l.institution))


  ## END

  if verbose: print("filtered %d articles out of %d (%f%%)") % (len(selection), nb_art, (100.0 * len(selection)) / nb_art)


  f_articles.close()
  f_authors.close()
  f_keywords.close()
  f_subjects.close()
  f_refs.close()
  f_countries.close()
  f_institutions.close()

  return

## ##################################################
## ##################################################
## ##################################################

def main():
# usage: filter.py -i DIR -o DIR -y1 INT -y2 INT [-v]
#
# optional arguments:
#   -o DIR, --output_dir DIR  output directory name
#   -i DIR, --input_dir DIR input directory name
#   -y1 INT, --y_min INT 
#   -y2 INT, --y_max_ INT 

  # Parse line options.
  # Try to have always the same input options
  parser = argparse.ArgumentParser(description = 'parser')

  parser.add_argument("-i", "--input_dir", nargs=1, required=True,
          action = "store", dest="in_dir",
          help="input directory name",
          metavar='DIR')
          
  parser.add_argument("-o", "--output_dir", nargs=1, required=True,
          action = "store", dest="out_dir",
          help="output directory name",
          metavar='DIR')

  parser.add_argument("-y1", "--ymin", nargs=1, type=int,
          action = "store", dest="ymin",
          default = [1500], help="ymin",
          metavar='INT')

  parser.add_argument("-y2", "--ymax", nargs=1, type=int,
          action = "store", dest="ymax",
          default = [2100], help="ymax",
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

  data_filter(args.in_dir[0],args.out_dir[0],args.ymin[0],args.ymax[0],args.verbose)

  return


    
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
    main()

## ##################################################
## ##################################################
## ##################################################

