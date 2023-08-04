"""Loader that fetches data from Stripe"""
import json
import urllib.request
from typing import List, Optional

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.utils import get_from_env, stringify_dict

SHOPIFY_ENDPOINTS = {
    "products": "/admin/products.json",
}


class ShopifyLoader(BaseLoader):
    """Loader that fetches data from Stripe."""

    def __init__(self, domain: str, resource: str, access_token: Optional[str] = None) -> None:
        """Initialize with a resource and an access token.

        Args:
            resource: The resource.
            access_token: The access token.
        """
        self.resource = resource
        self.domain = domain
        access_token = access_token or get_from_env(
            "access_token", "SHOPIFY_ACCESS_TOKEN"
        )
        self.params = f"?access_token={access_token}&published_status=published"

    def _make_request(self, url: str) -> List[Document]:
        request = urllib.request.Request(f"{url}{self.params}")

        with urllib.request.urlopen(request) as response:
            json_data = json.loads(response.read().decode())
            products = json_data.get("products")
            return [Document(page_content=f"{product.get('title', '')}", metadata=product) for product in products]

    def _get_resource(self) -> List[Document]:
        endpoint = SHOPIFY_ENDPOINTS.get(self.resource)
        if endpoint is None:
            return []
        return self._make_request(f"{self.domain}{endpoint}")

    def load(self) -> List[Document]:
        return self._get_resource()
