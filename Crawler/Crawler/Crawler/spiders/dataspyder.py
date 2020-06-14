# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from Crawler.items import ItemsData
from time import sleep
from copy import deepcopy
from scrapy_splash import SplashRequest

class DataSpider(Spider):
    name = "Data"
    id = 0
    start_urls=["https://papperstudio.com/shop",
                "https://skin9hari.co.kr/product/list.html?cate_no=48",
                "http://mama-casar.com",
                "http://healthybros.co.kr/product/list.html?cate_no=44",
                "https://belabef.com"]

    def start_requests(self):
        yield SplashRequest(url=self.start_urls[0], callback=self.papp_parse,
                            endpoint='render.html', args={'wait': 1})
        yield SplashRequest(url=self.start_urls[1], callback=self.skin_parse,
                            endpoint='render.html', args={'wait': 1})
        yield SplashRequest(url=self.start_urls[2], callback=self.mama_parse,
                            endpoint='render.html', args={'wait': 1})
        yield SplashRequest(url=self.start_urls[3], callback=self.heal_parse,
                            endpoint='render.html', args={'wait': 1})
        yield SplashRequest(url=self.start_urls[4], callback=self.bela_parse,
                            endpoint='render.html', args={'wait': 1})

    def papp_parse(self, response):
        selector = Selector(text=response.body)
        selects = selector.xpath('//*[@id="productListWrapper14933507"]/div/div')
        item = ItemsData()
        for sel in selects:
            self.id = self.id+1
            item['id'] = self.id
            item['name'] = sel.xpath('./a/div[2]/div/div/div[1]/text()').get().strip()
            item['url'] = response.urljoin(sel.xpath('./a/@href').get())
            item['image_url'] = sel.xpath('./a/div[1]/div/@style').re_first(r'\(([^)]+)')
            item['base_price'] = sel.xpath('./a/div[2]/div/div/div[2]/span[2]/text()').get()
            item['sale_price'] = sel.xpath('./a/div[2]/div/div/div[2]/span[1]/text()').get().strip()
            if item['base_price'] == None:
                item['base_price'] = deepcopy(item['sale_price'])
            sold = sel.xpath('./a/div[1]/div[3]/div/span/text()').get()
            if sold == "Sold Out":
                item['is_sold_out'] = True
            else:
                item['is_sold_out'] = False
            yield item


    def skin_parse(self, response):
        selector = Selector(text=response.body)
        pagelists = selector.xpath('//*[@id="contents"]/div[2]/div[2]/ul/li')
        itempages = []
        for pagelist in pagelists:
            itempages.append(response.urljoin(pagelist.xpath('./div/div[1]/a/@href').get()))
        for itempage in itempages:
            yield SplashRequest(url=itempage, callback=self.get_skin_item,
                                endpoint='render.html', args={'wait': 1})

    def get_skin_item(self, response):
        sel = Selector(text=response.body)
        item = ItemsData()
        self.id = self.id+1
        item['id'] = self.id
        item['name'] = sel.xpath('//*[@id="df-product-detail"]/div[1]/div[2]/div/div/div[1]/div[1]/div[1]/h2/text()').get().strip()
        item['url'] = response.url
        item['image_url'] = "https:"+sel.xpath('//*[@id="df-product-detail"]/div[1]/div[1]/div/div/div[1]/span/img/@src').get()
        item['base_price'] = sel.xpath('//*[@id="span_product_price_text"]/text()').get().strip()
        item['sale_price'] = sel.xpath('//*[@id="span_product_price_sale"]/text()').get().strip()
        sold = sel.xpath('//*[@id="df-product-detail"]/div[1]/div[2]/div/div/div[2]/div[1]/div[3]/@class').get()
        if sold == 'ac-soldout wrap displaynone':
            item['is_sold_out'] = False
        else:
            item['is_sold_out'] = True
        yield item


    def mama_parse(self, response):
        selector = Selector(text=response.body)
        catelists = selector.xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/ul/li[4]/ul/li')
        pagelists = []
        for catelist in catelists:
            goodslists = catelist.xpath('./ul/li')
            for goodslist in goodslists:
                pagelists.append(response.urljoin(goodslist.xpath('./a/@href').get()))
        for pagelist in pagelists:
            yield SplashRequest(url=pagelist, callback=self.get_mama_itemlist,
                                endpoint='render.html', args={'wait': 1})

    def get_mama_itemlist(self, response):
        selector = Selector(text=response.body)
        pagelists = selector.xpath('/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/ul/li')
        for pagelist in pagelists:
            itempage = response.urljoin(pagelist.xpath('./div/div/div[1]/a/@href').get())
            yield SplashRequest(url=itempage, callback=self.get_mama_item,
                                endpoint='render.html', args={'wait': 1})

    def get_mama_item(self, response):
        sel = Selector(text=response.body)
        item = ItemsData()
        self.id = self.id+1
        item['id'] = self.id
        item['name'] = sel.xpath('//*[@id="frmView"]/div/div[1]/div[1]/div/h2/text()').get().strip()
        item['url'] = response.url
        item['image_url'] = response.urljoin(sel.xpath('//*[@id="detail"]/div[3]/p[1]/img[2]/@src').get())
        prices = sel.xpath('//*[@id="frmView"]/div/div[2]/ul/li')
        if prices[0].xpath('./strong/text()').get().strip() == "판매가":
            item['base_price'] = prices[0].xpath('./div/strong/text()').get().strip()+"원"
            item['sale_price'] = prices[0].xpath('./div/strong/text()').get().strip()+"원"
        else:
            item['base_price'] = prices[0].xpath('./div/del/span/text()').get().strip()+"원"
            item['sale_price'] = prices[1].xpath('./div/strong/text()').get().strip()+"원"
        stock = sel.xpath('/html/head/script[7]').re_first('(?:stockNo = )([^;]*)')
        if stock == '0':
            item['is_sold_out'] = True
        else:
            item['is_sold_out'] = False
        yield item


    def heal_parse(self, response):
        selector = Selector(text=response.body)
        itempages = selector.xpath('//*[@id="contents"]/div[5]/div[1]/div/ul/li')
        for itempage in itempages:
            prices = itempage.xpath('./div[3]/ul/li')
            if len(prices) == 2:
                basep = prices[0].xpath('./span/text()').get()
                salep = prices[1].xpath('./span[1]/text()').get()
            else:
                basep = prices[0].xpath('./span[1]/text()').get()
                salep = prices[0].xpath('./span[1]/text()').get()
            itempageurl = response.urljoin(itempage.xpath('./div[1]/a/@href').get())
            yield SplashRequest(url=itempageurl,
                                callback=self.get_heal_item,
                                endpoint='render.html', args={'wait': 1},
                                meta={'basep':basep,'salep':salep})

    def get_heal_item(self, response):
        sel = Selector(text=response.body)
        item = ItemsData()
        self.id = self.id+1
        item['id'] = self.id
        item['name'] = sel.xpath('//*[@id="contents"]/div/div[1]/div[2]/div[2]/h3/text()').get().strip()
        item['url'] = response.url
        item['image_url'] = response.urljoin(sel.xpath('//*[@id="slideshow-list"]/li[1]/a/img/@src').get())
        item['base_price'] = response.meta['basep']
        item['sale_price'] = response.meta['salep']
        sold = sel.xpath('//*[@id="contents"]/div/div[1]/div[2]/div[2]/div[4]/div[1]/span/@class').get()
        if sold == 'displaynone':
            item['is_sold_out'] = False
        else:
            item['is_sold_out'] = True
        yield item


    def bela_parse(self, response):
        selector = Selector(text=response.body)
        pages = selector.xpath('/html/body/header/div/div/div[1]/div[2]/div[3]/div/div[2]/div/div/div/ul/div[1]/li[2]/ul/li/a/@href').getall()
        for i, page in enumerate(pages):
            pages[i] = response.urljoin(page)
        for page in pages:
            yield SplashRequest(url=page, callback=self.get_bela_itemlist,
                                endpoint='render.html', args={'wait': 1})

    def get_bela_itemlist(self, response):
        selector = Selector(text=response.body)
        imglists = selector.xpath('/html/body/div[4]/main/div[1]/div[4]/div/div/div/div/div/div/div[2]/div')
        itemlists = selector.xpath('/html/body/div[4]/main/div[1]/div[4]/div/div/div/div/div/div/div[2]/div/div[1]/a/@href').getall()
        for i, itemlist in enumerate(itemlists):
            itemlists[i] = response.urljoin(itemlist)
        for i, itemlist in enumerate(itemlists):
            imgsrc = imglists[i].xpath('./div/a/img/@data-src').get()
            yield SplashRequest(url=itemlist, callback=self.get_bela_item,
                                endpoint='render.html', args={'wait': 1},
                                meta={'imgsrc':imgsrc})

    def get_bela_item(self, response):
        sel = Selector(text=response.body)
        item = ItemsData()
        self.id = self.id+1
        item['id'] = self.id
        item['name'] = sel.xpath('/html/body/div[4]/main/div/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div/header/div[1]/text()').get().strip()
        item['url'] = response.url
        item['image_url'] = response.meta['imgsrc']
        prices = sel.xpath('/html/body/div[4]/main/div/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div/header/div[3]/div/span/span')
        if len(prices) == 2:
            item['base_price'] = prices[1].xpath('./text()').get().strip()
            item['sale_price'] = prices[0].xpath('./text()').get().strip()
        else:
            item['base_price'] = prices[0].xpath('./text()').get().strip()
            item['sale_price'] = prices[0].xpath('./text()').get().strip()
        sold = sel.xpath('/html/body/div[4]/main/div/div[1]/div/div/div/div[1]/div/div[2]/div[2]/div/div[6]/a[1]/text()').get().strip()
        if sold == "구매하기":
            item['is_sold_out'] = False
        else:
            item['is_sold_out'] = True
        yield item