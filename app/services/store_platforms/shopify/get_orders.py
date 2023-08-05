import requests
import os
from lib.utils import decrypt


def getOrders(domain, accessToken, query={}, *args, **kwargs):
    domain = domain + "/admin/orders.json"
    params = {
        "access_token": accessToken,
        **query
    }
    result = requests.get(domain, headers={
                          'X-Shopify-Api-Features': 'include-presentment-prices'}, params=params)
    result = result.json()
    return result
