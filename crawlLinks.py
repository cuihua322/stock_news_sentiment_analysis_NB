import os
import sys
import urllib
import urllib.request
from html.parser import HTMLParser
import io
import json
import time
import socket

class TextParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.StackTags = []
        self.Text = ''
        self.Recording = 0

    def handle_starttag(self, tag, attrs):
        if self.Recording:
            self.Recording += 1
            self.StackTags.append(tag)
            return

        if tag == 'div':
            for name, value in attrs:
                if name == 'id' and value == 'articlebody':
                    break
            else:
                return
            self.Recording = 1
            self.StackTags.append('div')

    def handle_endtag(self, tag):
        if self.Recording:
            self.Recording -= 1
            self.StackTags.pop()

    def handle_data(self, data):
        if self.Recording:
            if(self.StackTags[self.Recording-1] == 'script'):
                return
            self.Text = self.Text + data.strip()

class CrawlLinks:
    #def _headurl(self):
    #	return 'https://www.nasdaq.com/symbol/' + self.CompCode + '/news-headlines'

    def __init__(self, url):
        self.url = url
    
    def extract_headlines(self):
        with urllib.request.urlopen(self.url) as html:
            self.htmlhead = html.read().decode("utf8")
            #mystr = mybytes.decode("utf8")
            #return self.htmlhead
    def extract_title_links_time(self):
        urlprefix = '<a target="_self" href="'
        urlprefix_len = len(urlprefix)

        urlpostfix = '">'
        urlpostfix_len = len(urlpostfix)

        titlepostfix = '</a>'
        titlepostfix_len = len(titlepostfix)

        dateprefix = '<small>'
        dateprefix_len = len(dateprefix)

        datepostfix = '-'
        datepostfix_len = len(datepostfix)

        titles = []
        links = []
        dates = []
        bodys = []

        idx = 0
        while True:
            uidx = self.htmlhead.find(urlprefix, idx)
            if(uidx < 0):
                break
            u_idx = self.htmlhead.find(urlpostfix, uidx + urlprefix_len)
            if(u_idx < 0):
                break
            
            murl = self.htmlhead[uidx + urlprefix_len: u_idx]
            
            t_idx = self.htmlhead.find(titlepostfix, u_idx + urlpostfix_len)
            mtitle = self.htmlhead[u_idx + urlpostfix_len : t_idx]

            date_idx = self.htmlhead.find(dateprefix, t_idx + titlepostfix_len)
            date_post_idx = self.htmlhead.find(datepostfix, date_idx + dateprefix_len)
            
            mdate = self.htmlhead[date_idx + dateprefix_len : date_post_idx]
            print(mtitle.strip())
            print(murl.strip())
            print(mdate.strip())
            try:
                url =urllib.request.urlopen(murl)
                news = url.read().decode("utf8")
                parser = TextParser()
                parser.feed(news)

                titles.append(mtitle.strip())
                links.append(murl.strip())
                dates.append(mdate.strip())
                bodys.append(parser.Text.strip())
            except socket.error:
                continue
            except:
                time.sleep(3)
                continue
            idx = date_post_idx + datepostfix_len
            time.sleep(1)
            #break
        return titles, links, dates, bodys

"""
---requried ./input/stockPrices_raw.json
---requried ./input/stockSymbols.data

news_type:
    history
    today
"""
def get_news(date_type):

    with open("./input/stockPrices_raw.json","r") as load_f:
        price_json = json.load(load_f)

    tickers = []
    with open("./input/stockSymbols.data",'r') as fp:
        for stockSymbol in fp:
            tickers.append(stockSymbol.strip())


    MaxPage = 50
    urlprefix = "https://www.nasdaq.com/symbol/"
    urlpostfix = "/news-headlines?page="
    today_date = time.strftime('%Y/%m/%d',time.localtime(time.time()))    
   
    outfile = "history_news.data"
    if date_type == "today":
        outfile = "./data/News/"+time.strftime('%Y%m%d',time.localtime(time.time()))+"_news"
    fo = open(outfile, "w");

    for ticker in tickers:
        for page in range(MaxPage):
            page += 1
            url = urlprefix + ticker + urlpostfix + str(page);
            print(url)
            crawl = CrawlLinks(url)
            crawl.extract_headlines()
            titles, links, dates, bodys = crawl.extract_title_links_time()
            
            today_end_flag = 0
            if(len(links) == 0):
                break
            for i in range(0, len(links)):
                print(dates[i] +"--------------" + today_date)
                tmpdate = time.strftime("%Y/%m/%d", time.strptime(dates[i], "%m/%d/%Y %H:%M:%S %p"))
                if date_type == "today" and tmpdate != today_date:
                    today_end_flag = 1
                    break

                tmpdate = time.strftime("%Y-%m-%d", time.strptime(dates[i], "%m/%d/%Y %H:%M:%S %p"))
                openPrice = "NULL"
                closePrice = "NULL"
                if tmpdate in price_json[ticker]["open"]:
                    openPrice = price_json[ticker]["open"][tmpdate]
                if tmpdate in price_json[ticker]["close"]:
                    closePrice = price_json[ticker]["close"][tmpdate]
                
                fo.write(ticker+"\t"+dates[i]+"\t"+str(openPrice)+"\t"+str(closePrice)+"\t"+titles[i]+"\t"+links[i]+"\t"+bodys[i]+"\n")
            
            if today_end_flag == 1:
                break
            time.sleep(2)
    fo.close()






if __name__ == "__main__":
    if sys.argv[1] == 'today':
        get_news("today")
    if sys.argv[1] == 'history':
        get_news("history")
