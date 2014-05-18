# -*- coding: utf-8 -*-
"""
Created on Thu May 15 10:53:01 2014

@author: Liu Weizhi
"""

import urllib    
import urllib2  
import cookielib
import re  
from BeautifulSoup import BeautifulSoup
import codecs

# set cookie
cookie = cookielib.CookieJar()    
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))  
            
domain = 'http://pubsonline.informs.org'
num_volume = 15
num_issue = 4
data = dict()


for v in range(9, num_volume+1):
    dst = 'e:/msom%d.txt' % (1999+v-1)
    f = open(dst, 'w') 
    f.write('PT\tAU\tBA\tBE\tGP\tAF\tBF\tCA\tTI\tSO\tSE\tBS\tLA\tDT\tCT\tCY\tCL\tSP\tHO\tDE\tID\tAB\tC1\tRP\tEM\tRI\tOI\tFU\tFX\tCR\tNR\tTC\tZ9\tPU\tPI\tPA\tSN\tBN\tJ9\tJI\tPD\tPY\tVL\tIS\tPN\tSU\tSI\tMA\tBP\tEP\tAR\tDI\tD2\tPG\tWC\tSC\tGA\tUT\n')
    data[v] = dict()
    for i in range(1, num_issue+1):
        try:
            issue = opener.open('http://pubsonline.informs.org/toc/msom/%d/%d' % (v,i))
            html = issue.read()
            print '..Volume %d, Issue %d found' % (v, i)
            paper_url = re.findall('<a class="ref nowrap" href="(/doi/abs/\S*)">', html)
            data[v][i] = dict()
            for paper in paper_url:
                print '%s********' % paper
                data[v][i][paper] = dict()
                abs_url = domain+paper
                # deal with the abstract webpage's data
                paper_abs = opener.open(abs_url)
                soup_abs = BeautifulSoup(paper_abs.read())
                # extract title
                soup_title = soup_abs.findAll('div', {'class':'publicationContentTitle'})
                try:
                    data[v][i][paper]['TI'] = re.findall('<div class="publicationContentTitle">\s*<h1>\s*(.*)\s*</h1>\s*</div>', str(soup_title))[0]
                except IndexError:
                    data[v][i][paper]['TI'] = ''
                # record data source
                data[v][i][paper]['SO'] = 'M&SOM-MANUFACTURING & SERVICE OPERATIONS MANAGEMENT'
                # extract authors and their address
                soup_author_address = soup_abs.findAll('div', {'class':'NLM_contrib'})
                data[v][i][paper]['AU'] = ''
                data[v][i][paper]['AF'] = ''
                data[v][i][paper]['C1'] = ''
                for foo in soup_author_address:
                    author = re.findall('<div class="NLM_contrib"><span><a class="entryAuthor" href="\S*">([\S\s]*)</a>.*</span></div>', str(foo))
                    try:
                        tmp = author[0]
                        if '. ' in tmp:
                            tmp = tmp.split('. ')
                            abbr = ''
                            for foo in [foo[0] for foo in tmp[0].split(' ')]:
                                abbr += foo
                            author_abbr = tmp[1] + ', ' + abbr
                            author = tmp[1] + ', ' + tmp[0]
                        else:
                            tmp = tmp.split(' ')
                            abbr = ''
                            for foo in [foo[0] for foo in tmp[0].split(' ')]:
                                abbr += foo
                            author_abbr = tmp[1] + ', ' + abbr
                            author = tmp[1] + ', ' + tmp[0]                            
                    except IndexError:
                        author = ''
                        author_abbr = ''
                    address = re.findall('<div class="NLM_contrib"><span><a class="entryAuthor" href="\S*">[\S\s]*</a>.*<br />([\S\s]*)</span></div>', str(foo))
                    try:
                        address = address[0]
                    except IndexError:
                        address = ''
                    # record literate data in abstract webpage
                    data[v][i][paper]['AU'] += author_abbr + '; '
                    data[v][i][paper]['AF'] += author + '; '
                    data[v][i][paper]['C1'] += address + '; '
                data[v][i][paper]['AU'] = data[v][i][paper]['AU'][0:(len(data[v][i][paper]['AU'])-2)]
                data[v][i][paper]['AF'] = data[v][i][paper]['AF'][0:(len(data[v][i][paper]['AF'])-2)]
                data[v][i][paper]['C1'] = data[v][i][paper]['C1'][0:(len(data[v][i][paper]['C1'])-2)]
                # extract author keywords
                soup_keywords_list = soup_abs.findAll('kwd-group')
                data[v][i][paper]['DE'] = ''
                if soup_keywords_list:
                    if('span' in str(soup_keywords_list)):
                        keywords_list = re.split('\s+;\s+', re.findall('<kwd-group .*><span.*>.*</span>(.*)</kwd-group>', str(soup_keywords_list))[0])                    
                    else:
                        keywords_list = re.split('\s*;\s+', re.findall('<kwd-group .*xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">(.*)</kwd-group>', str(soup_keywords_list))[0])     
                    
                    for foo in keywords_list:
                        data[v][i][paper]['DE'] += re.findall('<a .*>([\S\s]*)</a>', foo)[0] + '; '
                    data[v][i][paper]['DE'] = data[v][i][paper]['DE'][0:(len(data[v][i][paper]['DE'])-2)]                
                # extract abstract
                soup_abstract = soup_abs.findAll('div', {'class':'abstractSection'})
                data[v][i][paper]['AB'] = ''
                if soup_abstract:
                    abstract_list = re.split('</p>\s*', re.findall('<div class="abstractSection">([\S\s]*)</div>', str(soup_abstract))[0])
                    for foo in abstract_list:
                        if foo:
                            foo = foo.replace('<i>', '').replace('</i>', '')
                            try:
                                data[v][i][paper]['AB'] += re.findall('<p.*>([\S\s]*)', foo)[0] + '\n'
                            except IndexError:
                                continue
                data[v][i][paper]['AB'] = data[v][i][paper]['AB'].replace('\n', '')
                # record j9
                data[v][i][paper]['J9']  = 'M&SOM-MANUF SERV OP'
                # extract volume, issue, year, season, begining/ending page
                soup_paper_basic = soup_abs.findAll('div', {'class':'journalNavTitle'})
                season = {'Spring':'SPR', 'Summer':'SUM', 'Fall':'FAL', 'Winter':'Win'}
                for foo in season:
                    if foo in str(soup_paper_basic):
                        data[v][i][paper]['PD'] = season[foo]
                paper_basic = re.split('\D*', re.findall('<div class="journalNavTitle">\s*(.*)\s*</div>', str(soup_paper_basic))[0])
                data[v][i][paper]['VL'] = paper_basic[1]
                data[v][i][paper]['IS'] = paper_basic[2]
                data[v][i][paper]['PY'] = paper_basic[3]
                try:
                    data[v][i][paper]['BP'] = paper_basic[4]
                    data[v][i][paper]['EP'] = paper_basic[5]
                except IndexError:
                    data[v][i][paper]['BP'] = -9999
                    data[v][i][paper]['EP'] = -9999
                                
                # deal with the reference webpage's data
                ref_url = domain+paper.replace('abs', 'ref')
                try:
                    paper_ref = opener.open(ref_url)
                    soup_ref = BeautifulSoup(paper_ref.read())
                    # extract references list
                    references_list = soup_ref.findAll('td', {'valign':'top'})                    
                    data[v][i][paper]['CR'] = ''
                    for reference in references_list:
                        # extract firstAu of reference
                        try:
                            firstAU = re.split('\s*,\s*<a class="entryAuthor".*>',str(reference))[0]
                            ref_author_tuple = re.findall('<a class="entryAuthor".*>(.*)<span class="NLM_given-names">(.*)</span></a>', firstAU)[0]                           
                            ref_author = ref_author_tuple[0] + ref_author_tuple[1].replace('.', '').replace(' ', '')
                        except IndexError:
                            ref_author = ''           
                        # extract publicatioin year of reference
                        try:
                            ref_year = re.findall('<span class="NLM_year">(\d*)</span>', str(reference))[0]
                        except IndexError:
                            ref_year = -9999
                        # extract journal of reference
                        try:
                            ref_journal = re.findall('<i>(.*)</i>', str(reference))[0].upper()
                        except IndexError:
                            ref_journal = ''
                        # extract volume,page of reference
                        try:
                            ref_volume_page_tuple = re.findall('\(<span class="NLM_year">\d*</span>\)\s*(\d*)\s*<span class="NLM_fpage">\s*(\d*)\s*</span>\s*<span class="NLM_lpage">\s*(\d*)\s*</span>', str(reference))[0]
                            ref_volume = ref_volume_page_tuple[0]
                            ref_bpage = ref_volume_page_tuple[1]
                            ref_epage = ref_volume_page_tuple[2]
                        except IndexError:
                            ref_volume = ''
                            ref_bpage = ''
                            ref_epage = ''
                        # extract doi/title of reference
                        try:
                            ref_title = re.findall('<span.*>(.*)</span>', str(reference.findAll('span', {'class':'NLM_article-title'})[0]))[0]
                        except IndexError:
                            ref_title = ''
                        data[v][i][paper]['CR'] += ref_author + ', ' + str(ref_year) + ', ' + ref_journal + ', ' + 'V' + str(ref_volume) + ', ' + 'P' + str(ref_bpage) + ', ' + 'DOI ' + ref_title + '; '                       
                    data[v][i][paper]['CR'] = data[v][i][paper]['CR'][0:(len(data[v][i][paper]['CR'])-2)]
                    f.write('\t%s\t\t\t\t%s\t\t\t%s\t%s\t\t\t\t\t\t\t\t\t\t%s\t\t%s\t%s\t\t\t\t\t\t\t%s\t\t\t\t\t\t\t\t\t%s\t\t%s\t%s\t%s\t%s\t\t\t\t\t%s\t%s\t\t\t\t\t\t\t\t\t\n' % 
                            (data[v][i][paper]['AU'],data[v][i][paper]['AF'],data[v][i][paper]['TI'],data[v][i][paper]['SO'],data[v][i][paper]['DE'],data[v][i][paper]['AB'],data[v][i][paper]['C1'],
                             data[v][i][paper]['CR'],data[v][i][paper]['J9'],data[v][i][paper]['PD'],data[v][i][paper]['PY'],data[v][i][paper]['VL'],data[v][i][paper]['IS'],data[v][i][paper]['BP'],data[v][i][paper]['EP']))
                except urllib2.URLError:                
                    continue            
        except urllib2.HTTPError:
            print '..Volume %d, Issue %d not found' % (v, i)    
    f.close()


