import os
import json
from datetime import datetime
import shopify
from dotenv import load_dotenv

class ShopifyClient:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        
        # Initialize Shopify API
        shop_url = "agilite-co-il.myshopify.com"
        api_version = "2024-01"  # Use the latest stable version
        
        shopify.ShopifyResource.set_site(f"https://{shop_url}/admin/api/{api_version}")
        shopify.ShopifyResource.set_headers({
            'X-Shopify-Access-Token': os.getenv('SHOPIFY_ACCESS_TOKEN')
        })
        
    def get_all_products(self):
        """Get all products from the store"""
        products_data = []
        
        # Get products with pagination
        products = shopify.Product.find(limit=250)
        while products:
            for product in products:
                product_data = {
                    "id": product.id,
                    "title": product.title,
                    "handle": product.handle,
                    "vendor": product.vendor,
                    "product_type": product.product_type,
                    "status": product.status,
                    "variants": [],
                    "timestamp": datetime.now().isoformat()
                }
                
                # Get variants for each product
                for variant in product.variants:
                    variant_data = {
                        "id": variant.id,
                        "title": variant.title,
                        "price": float(variant.price),
                        "sku": variant.sku,
                        "inventory_quantity": variant.inventory_quantity,
                        "inventory_management": variant.inventory_management,
                        "inventory_policy": variant.inventory_policy,
                        "barcode": variant.barcode
                    }
                    product_data["variants"].append(variant_data)
                
                products_data.append(product_data)
            
            # Get next page of products
            products = products.next_page()
        
        return products_data
    
    def get_inventory_levels(self, inventory_item_ids):
        """Get inventory levels for specific items"""
        inventory_levels = shopify.InventoryLevel.find(
            inventory_item_ids=inventory_item_ids
        )
        return inventory_levels
    
    def save_products_data(self, products_data, output_dir):
        """Save products data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"products_{timestamp}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
        
        return output_path

if __name__ == "__main__":
    # Test the client
    client = ShopifyClient()
    products = client.get_all_products()
    print(f"Retrieved {len(products)} products") 