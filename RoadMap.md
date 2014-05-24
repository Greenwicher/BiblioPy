> BiblioPy for Scientific Bibliometrics 

> Liu Weizhi copyright (2014)

## BiblioPy 1#  2014-04-14  17:34:00
<font color=blue>
**【已完成】：**

<ol>
    <li>co-citation network建立
    <li>co-citation network一级聚类以及二级聚类，以及相应gephi文件输出
    <li>community characteristic tex报告输出
    <li>各个community的research base以及research front文件输出
    <li>co-citation network二级聚类community characteristics tex报告输出
    <li>tex自动编译为pdf
</ol>
</font>

## BiblioPy 2#  
<font color=blue>
**【已完成】：**

<ol>
    <li>co-citation nodes的centrality(degree, closeness, betweenness)计算
</ol>
</font>

## BiblioPy 3#  2014-05-02 12:58:00
<font color=blue>
**【已完成】：**

<ol>
	<li>【2014-05-02】keywords中依据tf-idf指标排序，并修正了原来keywords在整个database的比例p的计算，现在的database是指filtered co-citation network所引申出的包含重复的document集合;并生成了tf-idf的dat file，以供人工处理相似关键词但分开统计的情况

</ol>
</font>

## BiblioPy 4#  2014-05-02 12:58:00
<font color=blue>
**【已完成】：**

<ol>
	<li>【2014-05-02】subGraph中的plot精细化表达（node颜色代表Sub Community ID, size代表被引用次数，edge的粗细代表相似度）
	<li>【2014-05-04】Bug Fixes - Gephi文件中输出了未超过阈值的边，已解决
	<li>【2014-05-04】Gephi/ResearchBase中journal不规范现象的解决，统一显示为该journal的缩写词（如JOM、MSOM、POM）
</ol>
</font>

## BiblioPy 5#  2014-05-18 22:38:00
<font color=blue>
**【已完成】：**

<ol>
	<li>【2014-05-08】基于keywords共现的TextRank算法实现，给出Main/Sub Keywords Graph以及每个节点的pagerank值
	<li>【2014-05-08】TextRank中Gephi gdf file提示unknown node id bug解决
	<li>【2014-05-13】给定期刊目录中reference数量（不包括重复）输出
	<li>【2014-05-18】Bug Fixes - Utils.py, first_distrib.py中关于Wosline对象的strip方法使用错误(空白项所对应的'\t'将被删掉)
	<li>【2014-05-18】M&SOM(1999-2005)文献纪录从INFORMS网站数据爬取完成，详情见crawler.py
	<li>【2014-05-18】intellectual base的report关键词通过加权pagerank值进行排序
</ol>
</font>

## BiblioPy 6#  
<font color=blue>
**【已完成】：**

<ol>
	<li>【2014-05-24】intellectual base之间的中介文章识别，pivotal papers matrix

</ol>
</font>