# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem
from datetime import datetime


class CartaCapitalSpider(scrapy.Spider):
    name = 'carta_capital'
    allowed_domains = ['cartacapital.com.br']
    start_urls = []

    links = []
    urls_seen = []

    def __init__(self, *a, **kw):
        super(CartaCapitalSpider, self).__init__(*a, **kw)
        with open('seeds/carta_capital.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    #
    # Metodo para verificar se os links obtidos fazem parte das
    # secoes validas para o parse principal
    #
    def isValidLink(self, link):
        for site_section in self.start_urls:
            if (site_section.lower() in link.lower()):
                return True
        return False
    
    #
    # Metodo para verificar se eh uma nova noticia
    #
    def isValidNews(self, link):
        if (self.isValidLink(link) and (self.urls_seen.count(link) == 0) and (link is not None)):
            return True
        else:
            return False

    def parse(self, response):

        # Verifica os links encontrados e faz a validação junto com o parse
        links = [a.attrib['href'] for a in response.css('h3 > a.eltdf-pt-link')]
        for url in links:
            yield scrapy.Request(url, self.convert)
        for next in response.css('a::attr(href)').getall():
            if (self.isValidNews(next)):
                yield scrapy.Request(next, self.parse)
            self.links.append(next)
        
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
    
    # Separa os resultados das paginas conforme a especificacao
    # separando os dados atraves do caminho do CSS
    def convert(self, response):
        if (int(response.css('div.eltdf-post-info-date a::attr(href)').get().split("/")[-3]) >= 2018):
            yield {
                'title': response.css('h1.eltdf-title-text::text').get(),
                'sub_title': response.css('div.wpb_text_column > div.wpb_wrapper > h3::text').get(),
                'author': response.css('a.eltdf-post-info-author-link::text').get(),
                'date': datetime.strptime(response.xpath("//meta[@property='article:published_time']/@content").get().replace("T", " ").split("+")[0], '%Y-%m-%d %H:%M:%S'),
                'section': response.css('div.eltdf-post-info-category > a::text').get(),
                'text': "".join(response.css('article p::text').getall()),
                'url': response.url
            }