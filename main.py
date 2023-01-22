import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import telegram_foward
import planilha_api
import time


def get_response(url):
    ua = UserAgent()
    headers = {'User-Agent':str(ua.chrome),
           'Accept-Language': 'en-US, en;q=0.5'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('Acesso negado')
        exit()
    return response

url_by_category = {
    'notebook': ['https://www.kabum.com.br/computadores/notebooks?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjE0NDUuNDksIm1heCI6MTE1MzUuMjF9fQ==&sort=most_searched'],
    'monitor': ['https://www.kabum.com.br/computadores/monitores?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjc1LjA1LCJtYXgiOjI3MTguNTR9fQ==&sort=most_searched'],
    'mouse': ['https://www.kabum.com.br/busca/mouse?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjY2LjcsIm1heCI6NjQzLjM5fX0=&sort=most_searched'],
    'teclado':  ['https://www.kabum.com.br/perifericos/teclado-gamer?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjc1LjYzLCJtYXgiOjY5OC40OX19&sort=most_searched'],
    'headset': ['https://www.kabum.com.br/perifericos/headset-gamer?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjcwLjEsIm1heCI6NjY2LjAzfX0=&sort=most_searched']    
}

def main():
    while True:
        planilha, service = planilha_api.main()
        tags = {}
        for i in range(len(planilha)):
            try:
                tags[planilha[i][0].lower()].append({'modelo': planilha[i][1],
                                                    'referencia': planilha[i][3],
                                                    'price': [float(x) for x in planilha[i][4].strip('R$').strip().split(',')[:-1]][0]*1000,
                                                    'linha': str(i+5)})
            except:
                try:
                    tags[planilha[i][0].lower()] = [{'modelo': planilha[i][1],
                                                    'referencia': planilha[i][3],
                                                    'price': [float(x) for x in planilha[i][4].strip('R$').strip().split(',')[:-1]][0]*1000,
                                                    'linha': str(i+5)}]
                except:
                    pass

        for tag in tags.keys():
            try:
                url_inicial = url_by_category[tag][0] + '1' + url_by_category[tag][1]
                response = get_response(url_inicial)
                site = BeautifulSoup(response.content, 'html.parser')
                qtd_produtos = site.find('div', id='listingCount').text.strip()
                index = qtd_produtos.index(' ')
                qtd_produtos = qtd_produtos[:index]
                num_paginas = int(int(qtd_produtos)/100) + 1
                for i in range(1, num_paginas + 1):
                    url = url_by_category[tag][0] + str(i) + url_by_category[tag][1]
                    response = get_response(url)
                    site = BeautifulSoup(response.content, 'html.parser')
                    product_cards = site.find_all('div', class_=re.compile('productCard'))
                    for dados_do_produto in tags[tag]:
                        for product_card in product_cards:
                            titulo_produto = product_card.find('span', class_=re.compile('nameCard')).text
                            if dados_do_produto['modelo'] in titulo_produto:
                                price = product_card.find('span', class_=re.compile('priceCard')).text
                                price_value = [float(i) for i in price.strip('R$').strip().split(',')[:-1]][0]*1000
                                try:
                                    if price_value < dados_do_produto['price']:
                                        print({'ID': dados_do_produto['modelo'], 
                                            'Title': titulo_produto, 
                                            'Value': price.replace(u'\xa0', u' ')}) # enviar ao banco de dados
                                        
                                        planilha_api.atualizar_planilha('Produtos Kabum!G' + dados_do_produto['linha'], price.replace(u'\xa0', u' '))
                                        
                                        if price_value < int(dados_do_produto['referencia']):
                                            print('No precinho! Enviando notificação para o telegram...')
                                            telegram_foward.send_message(f'Modelo: ' + dados_do_produto['modelo'] + f'\n\n{titulo_produto} \n\n{price}')
                                        
                                except Exception as e:
                                    print(e)  
            except Exception as e:
                print(e)
        time.sleep(600)


if __name__ == '__main__':
    main()
                