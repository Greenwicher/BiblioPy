#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
			Liu Weizhi (http://greenwicher.github.io/)
   Copyright (C) 2014
   All rights reserved.
   BSD license.
"""

# usage: parser.py -i DIR -o DIR [-v]
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
def Wos_parser(in_dir,out_dir,verbose):

  ## INITIALIZATION
  if verbose: print "..Analysing files %s/*.txt" % (in_dir)

  srccomp = "%s/*.txt" % in_dir
  srclst = glob.glob(srccomp)
  id = int(-1)
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

  kompt_refs = 0
  kompt_corrupt_refs = 0
  ref_index = dict()
  ref_id = int(-1)

  ## TREAT DATA

  for src in srclst:
	  pl = Utils.ArticleList()
	  pl.read_file(src)
	  if verbose: 
		  print "..processing %d articles in file %s" % (len(pl.articles), src)
	  if (len(pl.articles) > 0):
		  for article in pl.articles:
			  id = id + 1			  
			  #article 
			  foo = article.AU.split('; ')
			  firstAU = foo[0].replace(',','')
			  f_articles.write("%d\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (id,firstAU,article.PY,article.J9,article.VL,article.BP,article.DI,article.PT,article.DT,article.TC,article.TI,article.UT,article.DE,article.ID,article.IS,article.AB))
			  #authors
			  if(article.AU != ""): 
				  foo = article.AU.split('; ')
				  for i in range(len(foo)):
					  foo[i] = foo[i].replace(',','')
					  aux1 = foo[i].rfind(' ')
					  aux2 = len(foo[i])
					  foobar = foo[i].lower().capitalize()
					  if aux1 > 0: 
						  s1 = foobar[aux1:aux2]
						  s2 = s1.upper() 
						  foobar = foobar.replace(s1,s2)
					  aux = foobar.find('-')
					  if aux > 0: 
						  bar1 = foobar[aux:aux+2]
						  bar2 = '-' + foobar[aux+1].upper()
						  foobar = foobar.replace(bar1,bar2)
					  aux = foobar.find(' ')
					  if aux > 0: 
						  bar1 = foobar[aux:aux+2]
						  bar2 = ' ' + foobar[aux+1].upper()
						  foobar = foobar.replace(bar1,bar2)
					  f_authors.write("%d\t%d\t%s\n" % (id,i,foobar))
			  #keywords
			  if(article.DE != ""):
				  foo = article.DE.split('; ')
				  for i in range(len(foo)):
					  f_keywords.write("%d\tAK\t%s\n" % (id,foo[i].upper()))
			  if(article.ID != ""):
				  foo = article.ID.split('; ')
				  for i in range(len(foo)):
					  f_keywords.write("%d\tIK\t%s\n" % (id,foo[i].upper()))
			  #subjects
			  if(article.WC != ""):
				  foo = article.WC.split('; ')
				  for i in range(len(foo)):
					  f_subjects.write("%d\t%s\n" % (id,foo[i]))
			  #references
			  if(article.CR != ""):
				   foo = article.CR.split('; ')
				   for i in range(len(foo)):
					   ref=Utils.Ref()
					   ref.parse_ref(foo[i])
					   kompt_refs += 1 
					   ref_str = ref.firstAU + ',' + str(ref.year) + ',' + ref.journal + ',' + str(ref.volume) + ',' + str(ref.page)
					   if ref_str not in ref_index:
							ref_id = ref_id + 1
							ref_index[ref_str] = ref_id
					   if(ref.year > 0): 
						   f_refs.write("%d\t%d\t%s\t%d\t%s\t%s\t%s\t%s\n" % (id,ref_index[ref_str],ref.firstAU,ref.year,ref.journal,ref.volume,ref.page,ref.doi))
					   if(ref.year == 0): kompt_corrupt_refs += 1  
			  #countries / institutions
			  if(article.C1 != ""):
				  adresse = article.C1
				  aux1 = adresse.find('[')
				  aux2 = adresse.find(']')
				  while (aux1 < aux2):
					  aux = adresse[aux1:aux2+2]
					  adresse = adresse.replace(aux,'')
					  aux1 = adresse.find('[')
					  aux2 = adresse.find(']')
				  foo = adresse.split('; ')
				  for i in range(len(foo)):
					  foo[i] = foo[i].replace(', ',',')
					  bar = foo[i].split(',') 
					  ll = len(bar)
					  for j in range(ll - 2):
						  f_institutions.write("%d\t%d\t%s\n" % (id,i,bar[j]))
					  country = bar[ll-1]
					  lll=len(bar[ll-1])
					  if (country[lll-3:lll] == 'USA' or country[0:3] == 'AL ' or country[0:3] == 'AK ' or country[0:3] == 'AZ ' or country[0:3] == 'AR ' or country[0:3] == 'CA ' or country[0:3] == 'NC ' or country[0:3] == 'SC ' or country[0:3] == 'CO ' or country[0:3] == 'CT ' or country[0:3] == 'ND ' or country[0:3] == 'SD ' or country[0:3] == 'DE ' or country[0:3] == 'FL ' or country[0:3] == 'GA ' or country[0:3] == 'HI ' or country[0:3] == 'ID ' or country[0:3] == 'IL ' or country[0:3] == 'IN ' or country[0:3] == 'IA ' or country[0:3] == 'KS ' or country[0:3] == 'KY ' or country[0:3] == 'LA ' or country[0:3] == 'ME ' or country[0:3] == 'MD ' or country[0:3] == 'MA ' or country[0:3] == 'MI ' or country[0:3] == 'MN ' or country[0:3] == 'MS ' or country[0:3] == 'MO ' or country[0:3] == 'MT ' or country[0:3] == 'NE ' or country[0:3] == 'NV ' or country[0:3] == 'NH ' or country[0:3] == 'NJ ' or country[0:3] == 'NM ' or country[0:3] == 'NY ' or country[0:3] == 'OH ' or country[0:3] == 'OK ' or country[0:3] == 'or ' or country[0:3] == 'PA ' or country[0:3] == 'RI ' or country[0:3] == 'TN ' or country[0:3] == 'TX ' or country[0:3] == 'UT ' or country[0:3] == 'VT ' or country[0:3] == 'VA ' or country[0:3] == 'WV ' or country[0:3] == 'WA ' or country[0:3] == 'WI ' or country[0:3] == 'WY ' or country[0:3] == 'DC '): country = 'USA'
					  f_countries.write("%d\t%d\t%s\n" % (id,i,country))




  ## END

  if verbose: print("..%d inadequate refs out of %d (%f%%) have been rejected by this parsing process (no publication year, unpublished, ...) ") % (kompt_corrupt_refs, kompt_refs, (100.0 * kompt_corrupt_refs) / kompt_refs)

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
# usage: parser.py [-h] [--version] -i DIR -o DIR [-v]
# 
# optional arguments:
#   -h, --help			show this help message and exit
#   --version			 show program's version number and exit
#   -o DIR, --output_dir DIR
#						 output directory name
#   -i DIR, --input_dir DIR
#						 input directory name
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

  Wos_parser(args.in_dir[0],args.out_dir[0],args.verbose)

  return


	
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
	main()

## ##################################################
## ##################################################
## ##################################################

