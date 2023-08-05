import requests


def getCustomer(domain, accessToken, email, query={}, *args, **kwargs):
    domain = domain + "/admin/customers/search.json"
    result = requests.get(domain, headers={'X-Shopify-Api-Features': 'include-presentment-prices'}, params={
        "access_token": accessToken,
        "query": email,
        **query
    })
    result = result.json()
    return result
