import requests
import json


def transformShopifyProduct(domain):
    def getProduct(product):
        buttons = [
            {
                "type": "web_url",
                "url": domain+"/products/"+product["handle"],
                "title": "View"
            },
            {
                "type": "web_url",
                "url": domain+"/cart/"+str(product["variants"][0]["id"])+":1",
                "title": "Buy"
            }
        ]
        return {
            "title": product["title"],
            "image_url":
            product["image"]["src"],
            "subtitle": product["variants"][0]["presentment_prices"][0]["price"]["currency_code"]+product["variants"][0]["presentment_prices"][0]["price"]["amount"],
            "default_action": {
                "type": "web_url",
                "url": domain+"/products/"+product["handle"],
                "webview_height_ratio": "tall"
            },
            "buttons": buttons
        }
    return getProduct


def getId(graphqlId):
    parts = graphqlId.split('/')
    return parts[-1]


def getSubTitle(priceRangeV2):
    if priceRangeV2['minVariantPrice']["currencyCode"] == priceRangeV2['maxVariantPrice']["currencyCode"] and priceRangeV2['minVariantPrice']["amount"] == priceRangeV2['maxVariantPrice']["amount"]:
        return priceRangeV2['minVariantPrice']["currencyCode"] + priceRangeV2['minVariantPrice']["amount"]
    else:
        return priceRangeV2['minVariantPrice']["currencyCode"] + priceRangeV2['minVariantPrice']["amount"]+' - '+priceRangeV2['maxVariantPrice']["currencyCode"] + priceRangeV2['maxVariantPrice']["amount"]


def transformShopifyProductGraphql(domain):
    def getProduct(product):
        productNode = product['node']
        buttons = [
            {
                "type": "web_url",
                "url": domain+"/products/"+productNode["handle"],
                "title": "View"
            },
            {
                "type": "web_url",
                "url": domain+"/cart/"+str(getId(productNode["variants"]['edges'][0]['node']["id"]))+":1",
                "title": "Buy"
            }
        ]
        return {
            "title": productNode["title"],
            "image_url":
            productNode["featuredImage"]["originalSrc"],
            "subtitle": getSubTitle(productNode["priceRangeV2"]),
            "default_action": {
                "type": "web_url",
                "url": domain+"/products/"+productNode["handle"],
                "webview_height_ratio": "tall"
            },
            "buttons": buttons
        }
    return getProduct


def getProducts(domain, accessToken, query={}, *args, **kwargs):
    productsDomain = domain + "/admin/products.json"
    params = {
        "access_token": accessToken,
        "published_status": 'published',
        "limit": 10,
        **query
    }
    result = requests.get(productsDomain, headers={
                          'X-Shopify-Api-Features': 'include-presentment-prices'}, params=params)
    result = result.json()
    if not result.get("products"):
        return None
    products = map(transformShopifyProduct(domain), result["products"])
    return list(products)


def getProductsFromGraphQLAPI(domain, accessToken, productTitle, *args, **kwargs):
    productsDomain = domain+"/admin/api/2021-01/graphql.json"
    headers = {
        "X-Shopify-Access-Token": accessToken,
        "Content-Type": 'application/json'
    }
    data = {
        "query": "query { products(first:10, query:\"title:*"+productTitle+"*\") { edges { node { id title handle featuredImage{ originalSrc } priceRangeV2{ maxVariantPrice{ currencyCode amount } minVariantPrice{ currencyCode amount } } variants(first:3) { edges { node { id displayName price } } } } } } }"
    }
    result = requests.post(
        productsDomain, data=json.dumps(data), headers=headers)
    status_code =result.status_code
    result = result.json()
    if status_code != 200 or data.get("errors") or len(result["data"]["products"]["edges"]) == 0:
        return None
    products = map(transformShopifyProductGraphql(
        domain), result["data"]["products"]["edges"])
    return list(products)
