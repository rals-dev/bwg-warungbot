import random
from datetime import datetime, timedelta, timezone
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-0b38cd6a0a3b"

def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    
    # Clean up existing data
    print("Cleaning up existing collections...")
    for coll_name in ["products", "sales"]:
        docs = db.collection(coll_name).stream()
        for doc in docs:
            doc.reference.delete()

    products_data = [
        {"name": "Es Kopi Susu Gula Aren", "category": "coffee", "description": "Signature iced coffee with palm sugar.", "cost_price": 8000, "sell_price": 18000, "stock": 50, "min_stock": 20, "image_url": ""},
        {"name": "Americano", "category": "coffee", "description": "Classic black coffee, hot or iced.", "cost_price": 5000, "sell_price": 15000, "stock": 40, "min_stock": 10, "image_url": ""},
        {"name": "Cappuccino", "category": "coffee", "description": "Espresso with steamed milk and thick foam.", "cost_price": 7000, "sell_price": 20000, "stock": 30, "min_stock": 10, "image_url": ""},
        {"name": "Matcha Latte", "category": "non-coffee", "description": "Premium Japanese matcha with milk.", "cost_price": 10000, "sell_price": 22000, "stock": 5, "min_stock": 15, "image_url": ""}, # Low stock
        {"name": "Coklat", "category": "non-coffee", "description": "Rich and creamy iced chocolate.", "cost_price": 8000, "sell_price": 18000, "stock": 25, "min_stock": 10, "image_url": ""},
        {"name": "Teh Tarik", "category": "non-coffee", "description": "Pulled milk tea.", "cost_price": 5000, "sell_price": 12000, "stock": 8, "min_stock": 15, "image_url": ""}, # Low stock
        {"name": "Croissant", "category": "pastry", "description": "Buttery and flaky french pastry.", "cost_price": 12000, "sell_price": 25000, "stock": 12, "min_stock": 5, "image_url": ""},
        {"name": "Roti Bakar", "category": "pastry", "description": "Toast with chocolate and cheese toppings.", "cost_price": 8000, "sell_price": 18000, "stock": 20, "min_stock": 10, "image_url": ""},
        {"name": "Pisang Goreng", "category": "pastry", "description": "Fried banana with crispy batter.", "cost_price": 5000, "sell_price": 15000, "stock": 3, "min_stock": 10, "image_url": ""}, # Low stock
        {"name": "V60 Filter", "category": "coffee", "description": "Manual brew filter coffee.", "cost_price": 6000, "sell_price": 18000, "stock": 20, "min_stock": 10, "image_url": ""},
        {"name": "Red Velvet", "category": "non-coffee", "description": "Red velvet latte.", "cost_price": 10000, "sell_price": 22000, "stock": 15, "min_stock": 10, "image_url": ""},
        {"name": "Brownies", "category": "pastry", "description": "Fudgy chocolate brownie.", "cost_price": 15000, "sell_price": 30000, "stock": 8, "min_stock": 5, "image_url": ""}
    ]

    print("Seeding products...")
    product_refs = {}
    for p in products_data:
        doc_ref = db.collection("products").document()
        doc_ref.set(p)
        product_refs[p["name"]] = {"id": doc_ref.id, "sell_price": p["sell_price"]}

    print("Seeding sales...")
    now = datetime.now(timezone.utc)
    for _ in range(15):
        product_name = random.choice(list(product_refs.keys()))
        prod_info = product_refs[product_name]
        quantity = random.randint(1, 3)
        total = prod_info["sell_price"] * quantity
        
        # Random time in the last 7 days
        days_ago = random.uniform(0, 7)
        created_at = now - timedelta(days=days_ago)

        db.collection("sales").add({
            "product_id": prod_info["id"],
            "product_name": product_name,
            "quantity": quantity,
            "total": total,
            "created_at": created_at
        })

    print("Database seeding complete!")

if __name__ == "__main__":
    seed_database()
