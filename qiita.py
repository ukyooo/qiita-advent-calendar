#! /usr/bin/env python
# -*- coding:utf-8 -*-

''' Qiita Advent Calendar
'''

import os, sys, pprint, re, time, csv, json, math, copy
import urlparse
import requests
from bs4 import BeautifulSoup
# see: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# see: http://kondou.com/BS4/


class adventCalendar(object):
    '''
    '''
    interval = 1
    verbose = True
    year = 2017
    url_base = 'https://qiita.com'
    max_calendar_page = 100
    max_calendar_per_page = 20

    def __init__(self, year=None, interval=None, verbose=None):
        '''
        '''
        if year is not None:
            self.year = year

        if interval is not None:
            self.interval = interval

        if verbose is not None:
            self.verbose = verbose


    def __del__(self):
        '''
        '''
        pass


    def log(self, message, force=False):
        '''
        '''
        if force is not True and self.verbose is not True:
            return
        sys.stderr.write("LOG : %s\n" % (message))


    def getWeb(self, url):
        '''
        '''
        time.sleep(self.interval)
        soup = None
        try:
            session = requests.Session()
            response = session.get(url)
            # response = requests.get(url)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
        except:
            pass

        if response.status_code >= 400:
            self.log('Failure (response status code is %s) : get URL = %s' % (response.status_code, url), force=True)
            return None

        if soup is None:
            self.log('Failure : get URL = %s' % (url), force=True)
            return None

        self.log('Success : get URL = %s' % (url))
        return soup


    def getCalendar(self, code):
        ''' カレンダー情報 取得
        '''
        url = 'https://qiita.com/advent-calendar/%s/%s' % (self.year, code)
        soup = self.getWeb(url)
        result = []

        for row in soup.find_all('td', class_='adventCalendarCalendar_day'):
            # author = row.find('div', class_='adventCalendarCalendar_author').find('a')
            author = row.find('div', class_='adventCalendarCalendar_author')
            if author is None:
                # self.log('no author')
                continue

            author = author.find('a')
            if author is None:
                # self.log('no author')
                continue

            m = re.match('^/(.*)$', author.get('href'))
            if m is None:
                # self.log('no author name')
                continue
            user = m.group(1)

            comment = row.find('div', class_='adventCalendarCalendar_comment').find('a')
            if comment is None:
                # self.log('no comment')
                continue

            title = comment.text

            url = comment.get('href')
            url_parsed = urlparse.urlparse(url)

            if url_parsed.netloc in ['goo.gl', 't.co', 'bit.ly', 'is.gd', 'wp.me']:
                # 短縮 URL リダイレクト先 URL 取得
                url_redirected = None
                try:
                    response = requests.get(url, allow_redirects=True)
                    url_redirected = response.url
                except:
                    pass

                if url_redirected is None:
                    self.log('Failure : redirect URL = %s' % (url))
                    continue

                url = url_redirected
                url_parsed = urlparse.urlparse(url)

            # ドメインを反転させて格納
            netloc_list = url_parsed.netloc.split('.')
            netloc_list.reverse()
            netloc_list.append('')
            domain_reversed = '.'.join(netloc_list)

            # io.github.
            if re.match('^io\.github\.', domain_reversed) is not None:
                domain_reversed = 'io.github.'

            # com.tumblr.
            if re.match('^com\.tumblr\.', domain_reversed) is not None:
                domain_reversed = 'com.tumblr.'

            # com.wordpress.
            if re.match('^com\.wordpress\.', domain_reversed) is not None:
                domain_reversed = 'com.wordpress.'

            # jp.kc-cloud.
            if re.match('^jp\.kc-cloud\.', domain_reversed) is not None:
                domain_reversed = 'jp.kc-cloud.'

            # com.blogspot.
            if re.match('^com\.blogspot\.', domain_reversed) is not None:
                domain_reversed = 'com.blogspot.'
            if re.match('^ca\.blogspot\.', domain_reversed) is not None:
                domain_reversed = 'com.blogspot.'
            if re.match('^jp\.blogspot\.', domain_reversed) is not None:
                domain_reversed = 'com.blogspot.'

            # hatena.d.
            if re.match('^com\.hatenablog\.', domain_reversed) is not None:
                domain_reversed = 'hatena.d.'
            if re.match('^com\.hatenadiary\.', domain_reversed) is not None:
                domain_reversed = 'hatena.d.'
            if re.match('^jp\.hatenablog\.', domain_reversed) is not None:
                domain_reversed = 'hatena.d.'
            if re.match('^jp\.hatenadiary\.', domain_reversed) is not None:
                domain_reversed = 'hatena.d.'
            if re.match('^jp\.hateblo\.', domain_reversed) is not None:
                domain_reversed = 'hatena.d.'
            if re.match('^com\.hatena.d\.', domain_reversed) is not None:
                domain_reversed = 'hatena.d.'
            if domain_reversed == 'jp.ne.hatena.d.':
                domain_reversed = 'hatena.d.'
            if domain_reversed == 'jp.ne.hatena.blog.':
                domain_reversed = 'hatena.d.'

            # com.fc2.blog.
            if re.match('^com\.fc2.blog\.', domain_reversed) is not None:
                domain_reversed = 'com.fc2.blog.'
            if re.match('^com\.fc2.blog\d+\.', domain_reversed) is not None:
                domain_reversed = 'com.fc2.blog.'

            # com.medium.
            if domain_reversed == 'com.medium.':
                url = self.formatMediumURL(url)

            item = {
                'title':    title,
                'user':     user,
                'url':      url,
                'domain':   domain_reversed,
            }
            # yield item
            result.append(item)

        return result


    def findCalendarList(self, page):
        ''' page 指定 カレンダー 情報 取得
        '''
        url = 'https://qiita.com/advent-calendar/%s/calendars?page=%s' % (self.year, page)
        soup = self.getWeb(url)

        result = []
        for row in soup.find_all('td', class_='adventCalendarList_calendarTitle'):
            a = row.find_all('a').pop()
            name = a.text
            code = None
            m = re.match('^/advent-calendar/(\d+)/(.*)$', a.get('href'))
            if m is not None:
                code = m.group(2)
            result.append({
                'name': name,
                'code': code,
                'url':  '%s%s' % (self.url_base, a.get('href')),
            })

        return result


    def findCalendarListAll(self, with_item=False, with_count_hatena_bookmark=False):
        ''' 全 カレンダー 情報 取得
        '''
        result = []

        for page in range(1, self.max_calendar_page + 1):
            rows = self.findCalendarList(page)
            result.extend(rows)
            if len(rows) < self.max_calendar_per_page:
                self.log('page=%s' % (page))
                break

        if with_item is True:
            # 記事情報 付与
            for row in result:
                row['item'] = self.getCalendar(row['code'])

        if with_count_hatena_bookmark is True:
            # はてブ数 付与
            for row in result:
                row = self.setCountHatenaBookmarkOnCalendar(row)

        return result


    def countHatenaBookmark(self, params):
        ''' はてなブックマーク数 取得

            see: http://developer.hatena.ne.jp/ja/documents/bookmark/apis/getcount
        '''
        url = 'http://api.b.st-hatena.com/entry.counts'
        response = requests.get(url, params=params)
        return json.loads(response.content)


    def setCountHatenaBookmarkOnCalendar(self, row):
        ''' カレンダーと各記事の はてなブックマーク数 設定
        '''
        self.log('setCountHatenaBookmarkOnCalendar : code = %s' % (row['code']))

        # URL 抽出
        url_list = []
        url_list.append(row['url']) # カレンダー
        for item in row['item']:
            url_list.append(item['url']) # 記事

        # はてブ数
        result = self.countHatenaBookmark({'url': url_list})
        row['count'] = result[row['url']] # カレンダー
        for item in row['item']:
            item['count'] = result[item['url']] # 記事

        return row


    def formatMediumURL(self, url):
        ''' Medium URL 整形

        NOTE: はてなブックマーク が整形後の URL でカウントされている為

        https://medium.com/@nakanokyohei/%E5%AD%90%E4%BE%9B%E3%81%AB%E3%82%B9%E3%83%9E%E3%83%BC%E3%83%88%E3%83%95%E3%82%A9%E3%83%B3%E3%82%92%E4%B8%8E%E3%81%88%E3%81%9F%E8%A9%B1-8bc737220720
            -> https://medium.com/@nakanokyohei/8bc737220720

        https://medium.com/sotayamashita/glitch-github-%E3%81%A7%E7%B0%A1%E5%8D%98%E3%81%AB%E3%82%A2%E3%83%97%E3%83%AA%E3%82%92%E5%85%AC%E9%96%8B-b75af068ec46
            -> https://medium.com/sotayamashita/b75af068ec46

        # 独自ドメイン設定
        https://medium.com/p/8f11f33bfa96
            -> https://blog.kadoppe.com/%E5%AD%A6%E3%81%B3-%E3%81%AB%E3%83%95%E3%82%A9%E3%83%BC%E3%82%AB%E3%82%B9%E3%82%92%E3%81%82%E3%81%A6%E3%81%9F%E6%97%A5%E5%A0%B1%E3%81%AE%E3%82%88%E3%81%86%E3%81%AA%E3%82%82%E3%81%AE%E3%82%92%E5%8B%9D%E6%89%8B%E3%81%AB%E6%9B%B8%E3%81%84%E3%81%A6%E3%82%8B%E8%A9%B1-8f11f33bfa96
        '''
        # m = re.match('^https://medium.com/p/(\w+)$', url)
        m = re.match('^https://medium.com/p/([0-9a-f]+)$', url)
        if m is not None:
            # リダイレクタ
            response = requests.get(url, allow_redirects=True)
            # self.log('LOG : com.medium. : %s => %s' % (url, response.url))
            return response.url

        m = re.match('^https://medium.com/(@?[a-zA-Z0-9_\-\.]+)/([0-9a-f]+)$', url)
        if m is not None:
            # 変換不要
            # self.log('OK : com.medium. : url = %s' % (url))
            return url

        # m = re.match('^https://medium.com/(@?[-\.\w]+)/(.*)-(\w+)$', url)
        m = re.match('^https://medium.com/(@?[a-zA-Z0-9_\-\.]+)/(.*)-([0-9a-f]+)$', url)
        if m is None:
            self.log('NG : com.medium. : url = %s' % (url))
            raise Exception
        else:
            # self.log('OK : com.medium. : url = %s' % (url))
            url = 'https://medium.com/%s/%s' % (m.group(1), m.group(3))
            # self.log('OK : com.medium. : url = %s' % (url))

        return url

