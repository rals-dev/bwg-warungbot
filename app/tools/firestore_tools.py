from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

PROJECT_ID = "qwiklabs-gcp-03-0b38cd6a0a3b"

def get_db():
    return firestore.Client(project=PROJECT_ID)

def list_products(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List products with their name, sell price, category, and current stock level.
    
    Args:
        category: Optional category filter (e.g. 'coffee', 'non-coffee', 'pastry').
        
    Returns:
        List of product records.
    """
    db = get_db()
    query = db.collection("products")
    if category:
        query = query.where(filter=FieldFilter("category", "==", category.lower()))
    
    docs = query.stream()
    products = []
    for doc in docs:
        data = doc.to_dict()
        products.append({
            "id": doc.id,
            "name": data.get("name"),
            "category": data.get("category"),
            "sell_price": f"Rp{data.get('sell_price', 0):,}".replace(",", "."),
            "sell_price_raw": data.get("sell_price", 0),
            "stock": data.get("stock", 0),
            "min_stock": data.get("min_stock", 0)
        })
    return products

def get_low_stock() -> List[Dict[str, Any]]:
    """Return products whose current stock level is less than or equal to their minimum stock threshold.
    
    Returns:
        List of products needing restock.
    """
    db = get_db()
    docs = db.collection("products").stream()
    low_stock = []
    for doc in docs:
        data = doc.to_dict()
        stock = data.get("stock", 0)
        min_stock = data.get("min_stock", 0)
        if stock <= min_stock:
            low_stock.append({
                "id": doc.id,
                "name": data.get("name"),
                "category": data.get("category"),
                "stock": stock,
                "min_stock": min_stock,
                "sell_price": f"Rp{data.get('sell_price', 0):,}".replace(",", ".")
            })
    return low_stock

def record_sale(product_name: str, quantity: int) -> Dict[str, Any]:
    """Record a sale of a product, deducting inventory stock using a transaction.
    
    Args:
        product_name: Name of the product sold.
        quantity: Number of units sold.
        
    Returns:
        Confirmation details including total price and updated stock level.
    """
    if quantity <= 0:
        return {"status": "error", "message": "Quantity must be greater than zero."}

    db = get_db()
    products_ref = db.collection("products")
    docs = list(products_ref.stream())
    
    # Find matching product case-insensitively
    matched_doc = None
    for doc in docs:
        data = doc.to_dict()
        if data.get("name", "").lower() == product_name.lower():
            matched_doc = doc
            break
            
    if not matched_doc:
        return {"status": "error", "message": f"Product '{product_name}' not found."}

    doc_ref = matched_doc.reference

    @firestore.transactional
    def update_in_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        data = snapshot.to_dict()
        current_stock = data.get("stock", 0)
        if current_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {current_stock}, requested: {quantity}")
        
        new_stock = current_stock - quantity
        transaction.update(ref, {"stock": new_stock})
        
        sell_price = data.get("sell_price", 0)
        total = sell_price * quantity
        
        sale_data = {
            "product_id": ref.id,
            "product_name": data.get("name"),
            "quantity": quantity,
            "total": total,
            "created_at": datetime.now(timezone.utc)
        }
        
        sales_ref = db.collection("sales").document()
        transaction.set(sales_ref, sale_data)
        
        return {
            "product_name": data.get("name"),
            "quantity_sold": quantity,
            "total_price": f"Rp{total:,}".replace(",", "."),
            "total_raw": total,
            "new_stock": new_stock
        }

    transaction = db.transaction()
    try:
        result = update_in_transaction(transaction, doc_ref)
        result["status"] = "success"
        return result
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to record sale: {str(e)}"}

def update_stock(product_name: str, new_stock: int) -> Dict[str, Any]:
    """Update / restock the inventory level for a specific product.
    
    Args:
        product_name: Name of the product to update.
        new_stock: The new stock count.
        
    Returns:
        Updated product details.
    """
    if new_stock < 0:
        return {"status": "error", "message": "Stock cannot be negative."}

    db = get_db()
    docs = list(db.collection("products").stream())
    
    matched_doc = None
    for doc in docs:
        data = doc.to_dict()
        if data.get("name", "").lower() == product_name.lower():
            matched_doc = doc
            break
            
    if not matched_doc:
        return {"status": "error", "message": f"Product '{product_name}' not found."}
        
    matched_doc.reference.update({"stock": new_stock})
    data = matched_doc.to_dict()
    
    return {
        "status": "success",
        "product_name": data.get("name"),
        "previous_stock": data.get("stock"),
        "new_stock": new_stock,
        "message": f"Stock for {data.get('name')} updated to {new_stock}."
    }

def get_sales_summary(days: int = 7) -> Dict[str, Any]:
    """Summarize total revenue, total profit, and best-selling products over the last N days.
    
    Args:
        days: Number of days in the past to summarize (defaults to 7).
        
    Returns:
        Summary metrics including revenue, profit, and top product in Rupiah.
    """
    db = get_db()
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Fetch products to calculate cost price map
    products = {}
    for p_doc in db.collection("products").stream():
        p_data = p_doc.to_dict()
        products[p_doc.id] = p_data
        products[p_data.get("name")] = p_data

    sales_docs = db.collection("sales").where(filter=FieldFilter("created_at", ">=", since)).stream()
    
    total_revenue = 0
    total_cost = 0
    product_sales_count = {}
    
    for s_doc in sales_docs:
        s_data = s_doc.to_dict()
        qty = s_data.get("quantity", 0)
        total = s_data.get("total", 0)
        total_revenue += total
        
        p_id = s_data.get("product_id")
        p_name = s_data.get("product_name")
        
        cost_price = 0
        if p_id in products:
            cost_price = products[p_id].get("cost_price", 0)
        elif p_name in products:
            cost_price = products[p_name].get("cost_price", 0)
            
        total_cost += cost_price * qty
        
        product_sales_count[p_name] = product_sales_count.get(p_name, 0) + qty

    total_profit = total_revenue - total_cost
    
    best_seller = None
    best_seller_qty = 0
    if product_sales_count:
        best_seller = max(product_sales_count, key=product_sales_count.get)
        best_seller_qty = product_sales_count[best_seller]
        
    return {
        "period_days": days,
        "total_revenue": f"Rp{total_revenue:,}".replace(",", "."),
        "total_revenue_raw": total_revenue,
        "total_profit": f"Rp{total_profit:,}".replace(",", "."),
        "total_profit_raw": total_profit,
        "best_selling_product": best_seller or "None",
        "best_selling_quantity": best_seller_qty
    }
