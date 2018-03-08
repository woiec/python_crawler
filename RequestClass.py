
# ======================================
# 爬虫类
# @date:2017/3/9
# @方淞 @WeChat:wnfangsong
# ======================================

import urllib.request, urllib.parse, urllib.error
import datetime
import random
import zlib
import http.cookiejar
import os
import time

class Request:

    url = '' # 请求的URL
    repeat_post_number = 2  # 抓取失败时重试的次数
    post_data = None  # 请求需要发送的参数数组
    web_code = ''  # 抓取后的网站源码
    cookie = '' # 请求的COOKIE
    is_cookie = False # 是否需要请求COOKIE
    is_save_cookie = False # 第二次请求时是否保存新的COOKIE
    header = {} # 请求的头部
    run_log = [] # 运行的日志
    run_result = True # 当前运行的状态

    '''
    记录运行日志
    :param bool result
    :param string message
    :return void
    '''
    def _log(self, result, message):
        self.run_result = result
        now = datetime.datetime.now()
        message = now.strftime('%H:%M:%S') + ' ' + message
        print(message)

    '''
    抓取
    :return void
    '''
    def _grab(self):

        # 判断是否结束抓取
        if self.repeat_post_number == 0:
            self._log(False, '抓取失败后重试的次数为零，结束抓取。')
            return

        # COOKIE
        if self.is_cookie:
            cookie = http.cookiejar.MozillaCookieJar(self.cookie)
            if os.path.isfile(self.cookie):
                cookie.load(self.cookie, ignore_discard=True, ignore_expires=True)
            headler = urllib.request.HTTPCookieProcessor(cookie)
            opener = urllib.request.build_opener(headler)

        # 请求
        request = urllib.request.Request(self.url, self.post_data, self.header)
        try:
            if self.is_cookie:
                response = opener.open(request)
            else:
                response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            if hasattr(e, 'reason'):
                self._log(False, '服务器问题（' + str(e.reason) + '），暂停10秒执行。')
            elif hasattr(e, 'code'):
                self._log(False, '服务器无法完成请求（' + str(e.code) + ' ' + str(e.reason) + '），暂停10秒执行。')
            else:
                self._log(False, '未知错误，暂停10秒执行。')
            time.sleep(10)
            self.repeat_post_number = self.repeat_post_number - 1
            self._grab()
            return

        # 网页源码
        self.web_code = response.read()

        # 是否保存COOKIE
        if self.is_save_cookie:
            cookie.save(ignore_discard=True, ignore_expires=True)

        # GZIP
        http_info = response.info()
        if http_info['Content-Encoding'] == 'gzip':
            # GZIP解压&编码
            self.web_code = zlib.decompress(self.web_code, 16 + zlib.MAX_WBITS)

    '''
    返回COOKIE
    :return string
    '''
    def getCookie(self):
        return str(self.cookie)

    '''
    返回源码
    :return string
    '''
    def getWebCode(self):
        return str(self.web_code)

    '''
    UserAgent
    :param string type='pc'
    :return void
    '''
    def setUserAgent(self):
        self.header['User-Agent'] = '(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

    '''
    COOKIE
    :param string cookie=''
    :param bool is_save_new_cookie=False
    :return void
    '''
    def setCookie(self, is_save_cookie=False, cookie=''):
        self.is_cookie = True
        temp_now_path = os.path.split(os.path.realpath(__file__))[0]
        if cookie == '':
            self.cookie = temp_now_path + '\\Temp\\C' + str(random.randint(0,999)) + '.cookie'
        else:
            self.cookie = cookie
        self.is_save_cookie = is_save_cookie

    '''
    HESDER
    :param string header
    :return void
    '''
    def setHeader(self, header):
        key_list = header.keys()
        for key in key_list:
            self.header[key] = header[key]

    '''
    URL
    :param string url
    :return void
    '''
    def setUrl(self, url):
        self.url = url

    '''
    POST参数
    :param array data
    :return void
    '''
    def setPost(self, data):
        data = urllib.parse.urlencode(data)
        data = data.encode('utf-8')
        self.post_data = data

    '''
    参数清空（准备下一次的抓取）
    :return void
    '''
    def removeData(self):
        self.repeat_post_number = 2
        self.post_data = None
        self.web_code = ''
        self.cookie = ''
        self.is_cookie = False
        self.is_save_cookie = False
        self.header = {}
        self.run_log = []
        self.run_result = True

    '''
    删除COOKIE
    :return void
    '''
    def removeCookie(self):
        if os.path.isfile(self.cookie):
            os.remove(self.cookie)
            self.cookie = ''

    '''
    将网页源码转UTF-8
    :return void
    '''
    def setWebCodeToUtf8(self):
        if self.web_code!='':
            self.web_code = self.web_code.decode('utf-8')

    '''
    数据抓取
    :return void
    '''
    def grabWeb(self):
        begin = datetime.datetime.now() # 抓取前的时间
        # 判断必要的参数是否为空
        if self.url == '':
            self._log(False, '爬虫程序中必要的参数（URL）为空，请传参；结束抓取。')
            return
        # 开始抓取
        self._grab()
        if self.run_result == False:
            return
        # 返回
        end = datetime.datetime.now() # 抓取结束的时间
        self._log(True, '页面数据抓取完毕，耗时：' + str(end - begin))
