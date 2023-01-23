import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import telegram_foward
import planilha_api
import time

URL_NOTEBOOKS_PARSED = {'Notebook': ['https://www.kabum.com.br/computadores/notebooks?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjE0NDUuNDksIm1heCI6MTE1MzUuMjF9fQ==&sort=price'],
                        'Monitor': ['https://www.kabum.com.br/computadores/monitores?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjc1LjA1LCJtYXgiOjI3MTguNTR9fQ==&sort=price'],
                        'Mouse': ['https://www.kabum.com.br/busca/mouse?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjY2LjcsIm1heCI6NjQzLjM5fX0=&sort=price'],
                        'Teclado':  ['https://www.kabum.com.br/perifericos/teclado-gamer?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjc1LjYzLCJtYXgiOjY5OC40OX19&sort=price'],
                        'Headset': ['https://www.kabum.com.br/perifericos/headset-gamer?page_number=', '&page_size=100&facet_filters=eyJwcmljZSI6eyJtaW4iOjcwLjEsIm1heCI6NjY2LjAzfX0=&sort=price'] 
                    }

def get_response(url):
    ua = UserAgent()
    headers = {'User-Agent':str(ua.chrome),
           'Accept-Language': 'en-US, en;q=0.5'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('Acesso negado')
        exit()
    return response

def send_product_data(nome, id, preco):
    data = {'ID': id,
            'Título': nome,
            'Preço': preco}
    print(data)

def main():
    while True:
        try:
            planilha = planilha_api.main()
            for i in range(len(planilha)):
                codigo_do_produto = planilha[i][1]
                referencia = planilha[i][3]
                old_price = [float(x) for x in planilha[i][4].strip('R$').strip().split(',')[:-1]][0]*1000
                categoria = planilha[i][0]
                url = URL_NOTEBOOKS_PARSED[categoria][0] + '1' + URL_NOTEBOOKS_PARSED[categoria][1]
                response = get_response(url)
                site = BeautifulSoup(response.content, 'html.parser')
                qtd_produtos = site.find('div', id='listingCount').text.strip()
                index = qtd_produtos.index(' ')
                qtd_produtos = qtd_produtos[:index]
                num_paginas = int(int(qtd_produtos)/100) + 1
                price_value = 100000
                n = 0
                while n < num_paginas:
                    n += 1
                    url = URL_NOTEBOOKS_PARSED[categoria][0] + str(n) + URL_NOTEBOOKS_PARSED[categoria][1]
                    response = get_response(url)
                    site = BeautifulSoup(response.content, 'html.parser')
                    product_cards = site.find_all('div', class_=re.compile('productCard'))
                    for product_card in product_cards:
                        titulo_produto = product_card.find('span', class_=re.compile('nameCard')).text
                        if codigo_do_produto in titulo_produto:
                            price = product_card.find('span', class_=re.compile('priceCard')).text
                            price_value = [float(i) for i in price.strip('R$').strip().split(',')[:-1]][0]*1000 
                            send_product_data(titulo_produto, codigo_do_produto, price)
                            planilha_api.atualizar_planilha('Produtos Kabum!G' + str(i+5), price.replace(u'\xa0', u' '))
                            n = 20000
                            break
                if price_value < old_price and price_value < referencia:
                    print('No precinho! Enviando notificação para o telegram...')
                    telegram_foward.send_message(f'Modelo: ' + codigo_do_produto + f'\n\n{titulo_produto} \n\n{price}')
        except Exception as e:
            print(e)
        time.sleep(600)

if __name__ == '__main__':
    main()