from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.parse
import re

class urlmanager(object):
    def __init__(self):
        self.newurls = set()
        self.oldurls = set()

    def add_newurl(self, url):
        if url is None:
            return
        if url not in self.newurls and url not in self.oldurls:
            self.newurls.add(url)

    def has_newurl(self):
        return len(self.newurls) != 0

    def add_newurls(self, urls):
        if urls is None:
            return
        if urls not in self.newurls and urls not in self.oldurls:
            for url in urls:
                self.add_newurl(url)

    def get_newurl(self):
        new_url = self.newurls.pop()
        self.oldurls.add(new_url)
        return new_url

class htmldownloader():
    def download(self, url):
        if url is None:
            return
        res = urlopen(url)

        if res.getcode() != 200:
            return
        return res.read()

class htmlparser():
    def parse(self, url, htmlcont):
        if url is None or htmlcont is None:
            return
        soup = BeautifulSoup(htmlcont, 'html.parser', from_encoding='utf-8')
        new_urls = self._get_newurls(url, soup)
        new_data = self._get_newdata(url, soup)
        return new_urls, new_data

    def _get_newurls(self, url, soup):
        links = soup.find_all('a', href=re.compile(r'/item/\w+'))
        new_urls = set()
        for link in links:
            new_url = link['href']
            new_fullurl = urllib.parse.urljoin(url, new_url)
            new_urls.add(new_fullurl)
        return new_urls

    def _get_newdata(self, url, soup):
        res_data = {}
        res_data['link'] = url
        title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find('h1')
        res_data['title'] = title_node.get_text()
        summary_node = soup.find('div', class_='lemma-summary')
        res_data['summary'] = summary_node.get_text()
        return res_data

class htmloutputer():
    def __init__(self):
        self.datas = []

    def collectdata(self, data):
        if data is None:
            return
        self.datas.append(data)

    def outputhtml(self):
        fout = open('output.html', 'w', encoding='utf-8')
        fout.write('<html>')
        fout.write("<head><meta http-equiv=\"content-type\" content=\"text/html;charset=utf-8\"</head>>")
        fout.write('<body>')
        fout.write('<table>')

        for data in self.datas:
            fout.write('<tr>')
            fout.write('<td>%s</td>' % data['link'])
            fout.write('<td>%s</td>' % data['title'])
            fout.write('<td>%s</td>' % data['summary'])
            fout.write("</tr>")


        fout.write('</table>')
        fout.write("</body>")
        fout.write("</html>")
        fout.close()

class spider_main():
    def __init__(self):
        self.url = urlmanager()
        self.downloader = htmldownloader()
        self.parser = htmlparser()
        self.outputer = htmloutputer()

    def craw(self, root_url):
        count = 1
        self.url.add_newurl(root_url)
        while self.url.has_newurl():
            try:
                newurl = self.url.get_newurl()
                print('craw %d : %s' % (count, newurl))
                htmlcont = self.downloader.download(newurl)
                newurls, newdata = self.parser.parse(newurl, htmlcont)
                self.url.add_newurls(newurls)
                self.outputer.collectdata(newdata)

                if count == 100:
                    break
                count += 1
            except:
                print ('craw failed')


        self.outputer.outputhtml()
root_url = 'http://baike.baidu.com/item/Python'
obj_spider = spider_main()
obj_spider.craw(root_url)