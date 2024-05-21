import scrapy
from basic_scrapy_spider.items import QuoteItem
from datetime import date as dt, datetime, timezone
import scrapy
import gspread
import pytz
import json
from google.oauth2 import service_account

scopes = [
    'https://www.googleapis.com/auth/spreadsheets', 
    'https://www.googleapis.com/auth/drive',
    'https://mail.google.com/' 
]
creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1tyx1QmOeYv0w9pJ0QpTmvTVR2yRVnWiGlLfBNwz-JRc"
sheet = client.open_by_key(sheet_id)

worksheets = sheet.worksheets()


class astrovialsSpider(scrapy.Spider):


    name = 'vannapharma'
    # allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://vannapharma.cc/estrogens/']


    dataRows = []

    def parse(self, response):
            
            products = ['https://vannapharma.cc/shop/estradiol-gel-110ml/',
                        'https://vannapharma.cc/shop/estradiol-undecylate-10ml-40mg-ml/',
                        'https://vannapharma.cc/shop/estradiol-gel-55ml/',
                        'https://vannapharma.cc/shop/estradiol-cypionate/',
                        'https://vannapharma.cc/shop/estradiol-enanthate/',
                        'https://vannapharma.cc/shop/estradiol-valerate/'
                        ]
            # products = response.css('.button.product_type_simple::attr(href )').extract()

            if len(products) == 0:
                print('\n')
                print("---------------------------------------- products List is returning Zero -------------------------------------")
                print('\n')
                print("------------------ Site ------- is ----- Down -----------------------")
                print('\n')

            priceList = ['160', '95', '95', '70', '65', '60' ]
                

            for index, product in enumerate(products):

                
                    # priceList = response.css('bdi::text').extract()
                    print(f"Price List : {priceList}")

                    price = priceList[index]
                    print(price)
                    meta = {'index': index, 'price' : price} 
                    yield scrapy.Request(url=product, callback=self.parseAstrovialsProduct, meta=meta)

          

    def parseAstrovialsProduct(self, response):

        price = response.meta['price']
        print(f"PR II CCC EEEE  ::::  {price}")

        productName = response.css('.entry-title::text').get().strip()
        productPrice = price
        productStock = response.css('input::attr(max)').get()

        if productStock is None:
            productStock = "0"

        print('\n')

        # try:
        #     if 'in stock' in productStock:
        #         productStock = productStock.replace('in stock', "")
        # except Exception as e:
        #     print(e)

        print(f"product Name : {productName}")
        print(f"product Price : {productPrice}")
        print(f"product Stock : {productStock}")

        data = {
            'Product Name': productName,
            'Price': productPrice,
            'Stock': productStock
        }

        index = response.meta['index']  # Retrieve the index from metadata
        # Ensure that the dataRows list has enough elements
        while len(self.dataRows) <= index:
            self.dataRows.append({})
            
        self.dataRows[index] = data

        print(self.dataRows)


    def closed(self, reason):
        print("Closed")


        print(self.dataRows)

        for i, worksheet in enumerate(worksheets):
            
            # worksheet = sheet.get_worksheet(i)

            # current_date = dt.today()
            # date = current_date.isoformat()

            us_eastern = pytz.timezone('US/Eastern')
            us_Date = datetime.now(us_eastern).date()

            usDateStr = datetime.strftime(us_Date, "%Y-%m-%d")

            print(f"usDate time {us_Date}")

            # utcDate = datetime.now(timezone.utcoffset())
            # print(f"utcDate {utcDate}")
            # print(f"tzinfo  {utcDate.tzname()}")

            # utcDateStr = datetime.strftime(utcDate, "%Y-%m-%d")
            # print(utcDateStr)
            
           
            print(f"product is {self.dataRows[i]}")
        

            lastRowIndex = len(worksheet.get_all_values())
            print(f"last Row index{lastRowIndex}")

            if lastRowIndex == 1:
                print("in condition 1")
                data_to_write = []

                product1 = self.dataRows[i] 
                print(f"product 1 is {product1}")
                
                data_to_write.append([product1.get('Product Name', ''), product1.get('Price', ''), product1.get('Stock', ''), 
                                        ])
                
                print(f"data_to_write   {data_to_write}")

                productName =  product1.get('Product Name', '')
                worksheet.update_cell(lastRowIndex+1,1,productName)

                productPrice =  product1.get('Price', '')
                worksheet.update_cell(lastRowIndex+1,2,productPrice)

                stock =  product1.get('Stock', '')
                worksheet.update_cell(lastRowIndex+1,3,stock)

                # date update
                worksheet.update_cell(2,7,usDateStr)
            
            else:
                lastRowDate = worksheet.cell(lastRowIndex, 7).value
                
                # utcDateStr = datetime.strftime(utcDate, "%Y-%m-%d")
                if lastRowDate is not None:
                    lastRowDate = datetime.strptime(lastRowDate, "%Y-%m-%d").date()

                # print(f"tzinfo  {lastRowDate.tzname()}")
                # lastRowDate = lastRowDate.replace(tzinfo=timezone.utc)
                # print(f"tzinfo  {lastRowDate.tzname()}")

                    lastRowDate = datetime.strftime(lastRowDate, "%Y-%m-%d" )

                # lastRowDate_utc = lastRowDate.replace(tzinfo=timezone('UTC'))
                    print("LLLLASSSTTT")
                    print(lastRowDate)
                
                

                if lastRowDate == usDateStr:
                    print("Same Date as Today")

                    # # Write the current stock values to the "Previous Stock" column
                    stockValue = worksheet.cell(lastRowIndex,3).value
                    worksheet.update_cell(lastRowIndex,4, stockValue)

                    # loading A b c

                    # data_to_write = []

                    product1 = self.dataRows[i]
                    
                    # data_to_write.append([product1.get('Product Name', ''), product1.get('Price', ''), product1.get('Stock', ''), 
                    #                         ])
                    
                                    
                    # print(f"data_to_write   {data_to_write}")

                    productName =  product1.get('Product Name', '')
                    worksheet.update_cell(lastRowIndex,1,productName)

                    productPrice =  product1.get('Price', '')
                    worksheet.update_cell(lastRowIndex,2,productPrice)

                    stock =  product1.get('Stock', '')
                    worksheet.update_cell(lastRowIndex,3,stock)

                
                    # range_name = 'A2:C'  
                    # request_body = {
                    #     'value_input_option': 'USER_ENTERED',  
                    #     'data': [
                    #         {
                    #             'range': range_name,  
                    #             'values': data_to_write,  
                    #         }
                    #     ]
                    # }
                    # service = discovery.build('sheets', 'v4', credentials=creds)
                    # response = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet.id, body=request_body).execute()


                    # calc
                    
                    previousStock =  worksheet.cell(lastRowIndex,4).value
                    if previousStock is not None:
                        previousStock = int(previousStock)
                        print(f"previous stock {previousStock}")

                    else:
                        previousStock = 0



        

                    stock = self.dataRows[i].get('Stock', '')
                    print(f"stock {stock}")

                    if stock:
                        stock = int(stock)
                    else:
                        stock = 0

                    currentPrice = self.dataRows[i].get('Price', '')
                    if currentPrice:
                         currentPrice = float(currentPrice)
                    else:
                        currentPrice = 0

                    currentSoldStock = previousStock - stock
                    if currentSoldStock < 0:
                        currentSoldStock = 0
                    print(f"cuurent sold stock ::: {currentSoldStock}")
                    # if currentSoldStock < 1:
                    #     currentSoldStock = 0

                    CurrentRevenue = currentPrice * currentSoldStock

                    # adding into sold stock and revenue
                    soldStock =  worksheet.cell(lastRowIndex,5).value
                    if soldStock is None:
                        soldStock = 0
                    soldStock = int(soldStock)

                

                    updatedSoldStock = soldStock + currentSoldStock

                    Revenue =  worksheet.cell(lastRowIndex,6).value
                    if Revenue is None:
                        Revenue = 0

                    Revenue = float(Revenue)

                    updatedRevenue = Revenue + CurrentRevenue

                    worksheet.update_cell(lastRowIndex,5,updatedSoldStock)
                    worksheet.update_cell(lastRowIndex,6,updatedRevenue)



                else:
                    print("NOOOO")
                    print("Date Changed")

                    newRow = lastRowIndex + 1
                    preStk = worksheet.cell(lastRowIndex,3).value
                    worksheet.update_cell(newRow,4, preStk)

                    # load a b c g

                    # data_to_write = []

                    product1 = self.dataRows[i]
                        
                    # data_to_write.append([product1.get('Product Name', ''), product1.get('Price', ''), product1.get('Stock', ''), 
                    #                             ])
                    
                                    
                    # print(f"data_to_write   {data_to_write}")
                    
                    productName =  product1.get('Product Name', '')
                    worksheet.update_cell(newRow,1,productName)

                    productPrice =  product1.get('Price', '')
                    worksheet.update_cell(newRow,2,productPrice)

                    stock =  product1.get('Stock', '')
                    worksheet.update_cell(newRow,3,stock)

                    # calcs
                    previousStock =  preStk
                    if previousStock is not None:
                        previousStock = int(previousStock)
                        print(f"previous stock {previousStock}")

                    else:
                        previousStock = 0



        

                    stock = self.dataRows[i].get('Stock', '')
                    print(f"stock {stock}")

                    if stock:
                        stock = int(stock)
                    else:
                        stock = 0

                    currentPrice = self.dataRows[i].get('Price', '')
                    if currentPrice:
                         currentPrice = float(currentPrice)
                    else:
                        currentPrice = 0

                    currentSoldStock = previousStock - stock
                    if currentSoldStock < 0:
                        currentSoldStock = 0
                    print(f"cuurent sold stock ::: {currentSoldStock}")
                    # if currentSoldStock < 1:
                    #     currentSoldStock = 0

                    CurrentRevenue = currentPrice * currentSoldStock

                    # adding into sold stock and revenue
                    soldStock =  0
                    if soldStock is None:
                        soldStock = 0
                    soldStock = int(soldStock)

                

                    updatedSoldStock = soldStock + currentSoldStock

                    Revenue =  0
                    if Revenue is None:
                        Revenue = 0

                    Revenue = float(Revenue)

                    updatedRevenue = Revenue + CurrentRevenue

                    worksheet.update_cell(newRow,5,updatedSoldStock)
                    worksheet.update_cell(newRow,6,updatedRevenue)


                    # update Date
                    worksheet.update_cell(newRow,7, usDateStr)
    