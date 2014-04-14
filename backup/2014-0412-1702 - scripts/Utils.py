#! /usr/bin/env python

""" 
   Author : Sebastian Grauwin (http://www.sebastian-grauwin.com/)
			Liu Weizhi (http://greenwicher.github.io/)
   Copyright (C) 2014
   All rights reserved.
   BSD license.
"""

import os
import sys
import glob
import numpy
import argparse

## ##################################################
## ##################################################
## ##################################################

class Wosline:
	
	def __init__(self):
		self.PT = "" ## Publication Type (J=Journal; B=Book; S=Series)
		self.AU = "" ## Authors
		self.BA = "" ## Book Authors
		self.BE = "" ## Book Editor
		self.GP = "" ## Book Group Authors
		self.AF = "" ## Author Full Name
		self.CA = "" ## Group Authors
		self.TI = "" ## Document Title
		self.SO = "" ## Publication Name
		self.SE = "" ## Book Series Title
		self.LA = "" ## Language
		self.DT = "" ## Document Type
		self.CT = "" ## Conference Title 
		self.CY = "" ## Conference Date 
		self.CL = "" ## Conference Location 
		self.SP = "" ## Conference Sponsors 
		self.FO = "" ## Funding Organization
		self.DE = "" ## Author Keywords
		self.ID = "" ## Keywords Plus
		self.AB = "" ## Abstract
		self.C1 = "" ## Author Address
		self.RP = "" ## Reprint Address
		self.EM = "" ## E-mail Address
		self.FU = "" ## Funding Agency and Grant Number
		self.FX = "" ## Funding Text
		self.CR = "" ## Cited References
		self.NR = "" ## Cited Reference Count
		self.TC = "" ## Times Cited
		self.Z9 = "" ## 
		self.PU = "" ## Publisher
		self.PI = "" ## Publisher City
		self.PA = "" ## Publisher Address
		self.SN = "" ## ISSN
		self.BN = "" ## ISBN
		self.J9 = "" ## 29-Character Source Abbreviation
		self.JI = "" ## ISO Source Abbreviation
		self.PD = "" ## Publication Date
		self.PY = 0 ## Year Published
		self.VL = "" ## Volume
		self.IS = "" ## Issue
		self.PN = "" ## Part Number
		self.SU = "" ## Supplement
		self.SI = "" ## Special Issue
		self.BP = "" ## Beginning Page
		self.EP = "" ## Ending Page
		self.AR = "" ## Article Number
		self.DI = "" ## Digital Object Identifier (DOI)
		self.D2 = "" ## 
		self.PG = "" ## Page Count
		self.P2 = "" ## 
		self.WC = "" ## Web of Science Category
		self.SC = "" ## Subject Category
		self.GA = "" ## Document Delivery Number
		self.UT = "" ## Unique Article Identifier

	def parse_line(self, line, defCols, numCols):
		"""
		parse a line of the WoS txt output file  
		"""
		s = line.split("\t")
		if len(s)==numCols:
			if(s[defCols['PT']]=='J'): self.PT = 'Journal' ## Publication Type (J=Journal; B=Book; S=Series)
			if(s[defCols['PT']]=='B'): self.PT = 'Book' 
			if(s[defCols['PT']]=='S'): self.PT = 'Series' 
			self.AU = s[defCols['AU']] ## Authors
			self.TI = s[defCols['TI']] ## Document Title
			self.SO = s[defCols['SO']] ## Publication Name
			self.DT = s[defCols['DT']] ## Document Type
			self.DE = s[defCols['PT']] ## Author Keywords
			self.ID = s[defCols['ID']] ## Keywords Plus
			self.C1 = s[defCols['C1']] ## Author Address
			self.CR = s[defCols['CR']] ## Cited References
			self.TC = s[defCols['TC']] ## Times Cited
			self.J9 = s[defCols['J9']] ## 29-Character Source Abbreviation
			self.PD = s[defCols['PD']] ## Publication Date
			if s[defCols['PY']].isdigit(): self.PY = int(s[defCols['PY']])
			else:			   self.PY = 0  ## Year Published
			self.VL = s[defCols['VL']] ## Volume
			self.IS = s[defCols['IS']] ## Issue
			self.BP = s[defCols['BP']] ## Beginning Page
			self.WC = s[defCols['WC']] ## Web of Science Category
			self.UT = s[defCols['UT']] ## Unique Article Identifier

## ##################################################

def defColumns(line):

  # initialize
  Cols = ['PT', 'AU', 'TI', 'SO', 'DT', 'DE', 'ID', 'C1', 'CR', 'TC', 'J9', 'PD', 'PY', 'VL', 'IS', 'BP', 'WC', 'UT'];
  defCols = dict();
  
  # match columns number in "line"
  foo = line.replace('\xef\xbb\xbf','').split('\t')
  for i in range(len(foo)):
	if foo[i] in Cols: 
	  defCols[foo[i]] = i
  numCols = len(foo)

  return (defCols, numCols)

## ##################################################

## ##################################################
## ##################################################
## ##################################################

class ArticleList:

	def __init__(self):
		self.articles	  = []	  # articles list
 
	def read_file(self,filename):

		articles_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			aux = 0
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
				  if (aux == 1): # do not take 1st line into account! 
					wline = Wosline()
					wline.parse_line(line, defCols, numCols)
					articles_list.append( wline )
				  if (aux == 0): # define columns thanks to 1st line
					(defCols, numCols) = defColumns( line )
					aux = 1			
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.articles   = articles_list
## ##################################################
## ##################################################
## ##################################################

class Article:

	def __init__(self):
		self.id		  = 0
		self.firstAU	 = ""	   
		self.year		= 0
		self.journal	 = ""
		self.volume	  = ""
		self.page		= ""
		self.doi		 = ""
		self.pubtype	 = ""
		self.doctype	 = ""
		self.times_cited = ""
		self.title	   = ""
		self.uniqueID	= ""
 
		self.articles	  = []	  # liste d'articles


	def read_file(self,filename):
		"""
		Lecture des articles
		"""
		articles_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			aux = 0
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					aline = Article()
					aline.id = int(s[0])
					if(len(s)>1): aline.firstAU = s[1]
					if(len(s)>2): aline.year = int(s[2]) 
					if(len(s)>3): aline.journal = s[3] 
					if(len(s)>4): aline.volume = s[4] 
					if(len(s)>5): aline.page = s[5] 
					if(len(s)>6): aline.doi  = s[6]
					if(len(s)>7): aline.pubtype = s[7]
					if(len(s)>8): aline.doctype = s[8]
					if(len(s)>9): aline.times_cited = s[9]
					if(len(s)>10): aline.title = s[10]
					if(len(s)>11): aline.uniqueID = s[11]
   
					articles_list.append( aline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.articles   = articles_list

## ##################################################
## ##################################################
## ##################################################

class Author:

	def __init__(self):
		self.id	 = 0
		self.rank   = 0	   
		self.author = ""
 
		self.authors  = []	  # liste 


	def read_file(self,filename):
		"""
		Lecture des articles
		"""
		alines_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					aline = Author()
					aline.id = int(s[0])
					aline.rank = int(s[1])
					aline.author = s[2]  
					alines_list.append( aline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.authors   = alines_list

## ##################################################
## ##################################################
## ##################################################

class Country:

	def __init__(self):
		self.id	 = 0
		self.rank   = 0	   
		self.country = ""
 
		self.countries  = []	  # liste 


	def read_file(self,filename):
		"""
		Lecture des articles
		"""
		clines_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					cline = Country()
					cline.id = int(s[0])
					cline.rank = int(s[1])
					cline.country = s[2].lower().capitalize()  
   
					clines_list.append( cline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.countries   = clines_list

## ##################################################
## ##################################################
## ##################################################

class Institution:

	def __init__(self):
		self.id	 = 0
		self.rank   = 0	   
		self.institution = ""
 
		self.institutions  = []	  # liste 


	def read_file(self,filename):
		"""
		Lecture des articles
		"""
		ilines_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					iline = Institution()
					if len(s)==3:
					  iline.id = int(s[0])
					  iline.rank = int(s[1])
					  iline.institution = s[2].upper()  
   
					  ilines_list.append( iline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.institutions   = ilines_list

## ##################################################
## ##################################################
## ##################################################

class Keyword:

	def __init__(self):
		self.id	  = 0
		self.ktype   = ""	   
		self.keyword = ""
 
		self.keywords  = []	  # liste 


	def read_file(self,filename):
		"""
		Lecture des articles
		"""
		klines_list = []
		try:
			# open
			if filename != 'st.lower().capitalize()din':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					kline = Keyword()
					kline.id = int(s[0])
					kline.ktype = s[1]
					kline.keyword = s[2].upper()  
   
					klines_list.append( kline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.keywords   = klines_list

## ##################################################
## ##################################################
## ##################################################

class Ref:

	def __init__(self):
		self.id	  = 0
		self.refid   = 0
		self.firstAU = ""	   
		self.year	= 0
		self.journal = ""
		self.volume  = 0
		self.page	= 0
		self.doi = ""		
		self.refs	  = []	  # liste de refs

	def parse_ref(self, ref):
		"""
		parse a ref of the WoS txt format  
		"""
		s = ref.split(', ')

		if(len(s)>0): 
			aux1 = s[0].rfind(' ')
			aux2 = len(s[0])
			foo = s[0].lower().capitalize()
			if aux1 > 0: 
				s1 = foo[aux1:aux2]
				s2 = s1.upper() 
				foo = foo.replace(s1,s2)
				foo = foo.replace('.','')
			self.firstAU = foo	   
		if(len(s)>1): 
			if s[1].isdigit(): self.year = int(s[1])
			else:			  self.year = 0
		if(len(s)>2): self.journal = s[2]
		if(len(s)>3): 
			if(s[3][0]=='V'): self.volume  = s[3].replace('V','')
		if(len(s)>3): 
			if(s[3][0]=='P'): self.page  = s[3].replace('P','')
		if(len(s)>4): 
			if(s[4][0]=='P'): self.page  = s[4].replace('P','')
		if(len(s)>5):
			if(s[5][0:4]=='DOI '): self.doi = s[5].replace('DOI ', '')
			else: self.doi = "NA"
		else: self.doi = "NA"			

	def read_file(self,filename):
		"""
		Lecture des refs
		"""
		refs_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					refline = Ref()
					refline.id = int(s[0])
					refline.refid = int(s[1])
					refline.firstAU = s[2]
					refline.year = int(s[3]) 
					refline.journal = s[4] 
					refline.volume = s[5] 
					refline.page = s[6] 
					refline.doi = s[7]					
   
					refs_list.append( refline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.refs   = refs_list

## ##################################################
## ##################################################
## ##################################################

class Subject:

	def __init__(self):
		self.id	  = 0
		self.subject = ""	   
 
		self.subjects  = []	  # liste 


	def read_file(self,filename):
		"""
		Lecture des articles
		"""
		slines_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					sline = Subject()
					sline.id = int(s[0])
					sline.subject = s[1] 
   
					slines_list.append( sline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "file does not exist"

		self.subjects   = slines_list

## ##################################################
## ##################################################
## ##################################################


class Labo:

	def __init__(self):
		self.id   = 0	  
		self.labo = ""
 
		self.labos  = []	  # liste 


	def read_file(self,filename):
		"""
		Lecture des labos
		"""
		llines_list = []
		try:
			# open
			if filename != 'stdin':
				fd = open(filename)
			else:
				fd = sys.stdin
			# read
			for line in fd.readlines():
				line = line.strip() # removes \n
				if (line != ""):
					s = line.split("\t")
					lline = Labo()
					if len(s)==2:
					  lline.id = int(s[0])
					  lline.labo = s[1]
   
					  llines_list.append( lline )
			# close  
			if filename != 'stdin':
				fd.close()
		except IOError:
			print "..labos.dat file does not exist"

		self.labos   = llines_list

## ##################################################
## ##################################################
## ##################################################
	
## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
	main()

## ##################################################
## ##################################################
## ##################################################

