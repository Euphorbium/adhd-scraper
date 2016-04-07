# -*- coding: utf-8 -*-
import unicodecsv
from lxml import html
from retrying import retry
import re


@retry(wait_random_min=5000, wait_random_max=10000)
def scrape_thread(thread):
    t=html.parse(thread)
    title = t.xpath('//div[@class="blog-post"]/h5/span/text()')[0]
    content = "\n".join(t.xpath('//div[@class="blog-post"]/p/text()'))
    group = t.xpath('//div[@id="main-col"]/div[@class="box"]/h4/text()')[0]
    poster = t.xpath('//span[@class="post-meta"]/a[1]/text()')[0]
    date = t.xpath('//span[@class="post-meta"]/a[2]')[0].tail[3:-10].strip()
    qid = re.findall('.*/(.*)/$', thread)[0]
    w.writerow([qid + '_top', qid, -1, title, poster, date, ' ', content, ' ', group])
    posters=set((poster,))
    for i, comment in enumerate(t.xpath('//div[@id="comments"]/div[@class="comment"]')):
        poster = comment.xpath('.//div[@class="comment-meta"]/a')[0].text
        date = comment.xpath('.//div[@class="comment-meta"]/a')[0].tail[3:].strip()
        content = '\n'.join(comment.xpath('.//div[@class="comment-text"]/p/text()'))
        inferred_replies = []
        for p in posters:
            if p in content:
                inferred_replies.append(p)
        posters.add(poster)
        w.writerow([qid+'_'+str(i), qid, i, title, poster, date, qid+'_top', content, ' '.join(inferred_replies), group])
        f.flush()


page = html.parse("http://connect.additudemag.com/groups/all_topics/")
f = open('add.csv', 'w')
w = unicodecsv.writer(f, encoding='utf-8', lineterminator='\n')
w.writerow(['uniqueID', 'qid', 'localID', 'title', 'poster', 'date', 'replyTo', 'content', 'infered_replies', 'group'],)
while page.xpath('//*[@class="paginate"]/a[last()]/text()')[0] == u"Last »":
    for thread in page.xpath('//div[@id="box"]/table//table//tr/td[1]/a'):
        print thread.attrib['href']
        scrape_thread(thread.attrib['href'])
    page = html.parse(page.xpath('//*[@class="paginate"]/strong/following-sibling::a[1]')[0].attrib['href'])

for thread in page.xpath('//div[@id="box"]/table//table//tr/td[1]/a'):
    print thread.attrib['href']
    scrape_thread(thread.attrib['href'])