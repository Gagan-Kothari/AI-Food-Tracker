import requests
try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None
try:
    from pyzbar import pyzbar  # type: ignore
except Exception:  # pragma: no cover
    pyzbar = None
from dotenv import load_dotenv
import os
import re

load_dotenv()

OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v0/product"

# Food categories for classification
FOOD_CATEGORIES = [
    # Spreads & Condiments
    "jam", "jams", "jelly", "jellies", "chutney", "chutneys", "spread", "spreads",
    "peanut butter", "hazelnut spread", "nut butter", "mustard", "mustards",
    "ketchup", "mayonnaise", "mayo", "relish", "sauces", "sauce", "pesto",

    # Beverages
    "beverage", "beverages", "drink", "drinks", "juice", "juices", "soda", "sodas",
    "cola", "colas", "energy drink", "energy drinks", "sports drink", "sports drinks",
    "tea", "teas", "iced tea", "coffee", "coffees", "smoothie", "smoothies",
    "bottled water", "sparkling water", "flavored water", "water", "waters",

    # Snacks
    "chip", "chips", "crisps", "crisp", "snack", "snacks", "popcorn", "pretzel", "pretzels",
    "cracker", "crackers", "rice cake", "rice cakes", "trail mix", "energy bar", "protein bar",
    "bar", "bars", "granola", "granola bar", "nuts", "nut", "seeds", "seed",

    # Sweets & Confectionery
    "candy", "candies", "chocolate", "chocolates", "biscuit", "biscuits", "cookie", "cookies",
    "cake", "cakes", "pastry", "pastries", "donut", "donuts", "brownie", "brownies",
    "gum", "gums", "mint", "mints", "lollipop", "lollipops", "jellybean", "jellybeans",
    "marshmallow", "marshmallows", "toffee", "caramel", "pudding", "dessert", "desserts",

    # Dairy & Refrigerated
    "cheese", "cheeses", "butter", "butters", "yogurt", "yogurts", "milk", "milks", "ghee",
    "cream", "sour cream", "whipped cream", "dairy drink", "dairy dessert", "ice cream", "ice creams",

    # Breakfast Items
    "cereal", "cereals", "oatmeal", "muesli", "granola", "breakfast bar", "pancake", "waffle",

    # Bakery
    "bread", "breads", "bun", "buns", "bagel", "bagels", "muffin", "muffins", "croissant", "toast", "flour", "atta", "maida", "eggs", "egg",

    # Frozen Foods
    "frozen meal", "frozen meals", "frozen pizza", "frozen food", "frozen foods", "ice cream", "ice creams",

    # Ready-to-Eat / Instant
    "instant noodles", "ramen", "noodle soup", "cup soup", "ready meal", "ready meals", "canned soup", "microwave meal",

    # Baby & Kids
    "baby food", "baby foods", "infant formula", "kids snack", "kids juice",

    # Other
    "soup", "soups", "noodles", "pasta", "ravioli", "lasagna", "sushi", "salad", "salads"
]


def extract_quantity_from_text(text):
    """
    Extract quantity information from text using regex patterns.
    
    Args:
        text: Text to extract quantity from
        
    Returns:
        str: Extracted quantity or None if not found
    """
    if not text:
        return None

    # Units and patterns like 100g, 1kg, 250ml, 1.5l, 1 litre, etc.
    pattern = r'(\d+(?:[\.,]?\d+)?)(\s?)(g|gram|grams|kg|kilogram|kilograms|ml|l|litre|litres|oz|ounces)'
    match = re.search(pattern, text.lower())
    if match:
        return match.group(0).replace(",", ".")
    return None


def find_categories(keywords, categories, product_name_en):
    """
    Find food category based on keywords, categories, and product name.
    
    Args:
        keywords: List of keywords
        categories: Category string
        product_name_en: Product name in English
        
    Returns:
        dict: Category information and status
    """
    all_words = set()

    if keywords:
        all_words.update(k.lower() for k in keywords)
    if categories:
        all_words.update(c.strip().lower() for c in categories.split(","))
    if product_name_en:
        all_words.update(product_name_en.lower().split())

    for word in all_words:
        if word in FOOD_CATEGORIES:
            if word == "atta":
                word = "Wheat Flour"
            if word == "maida":
                word = "Refined Wheat Flour"
            return {"category": word, "categorystatus": True}

    return {"category": "", "categorystatus": False}


def filter_data(data):
    """
    Filter and process data from OpenFoodFacts API.
    
    Args:
        data: Raw data from API
        
    Returns:
        dict: Processed food item data
    """
    product = data.get("product", {})

    code = data.get("code")
    product_name_en = product.get("product_name_en")
    energy_kcal_100g = product.get("nutriments", {}).get("energy-kcal_100g")
    quantity = product.get("quantity")
    brands = product.get("brands")
    keywords = product.get("_keywords")
    categories = product.get("categories")
    imageurl = product.get("image_url")

    # Try extracting from quantity field first
    final_quantity = extract_quantity_from_text(quantity)

    # If not found, try from serving_size
    if not final_quantity:
        final_quantity = extract_quantity_from_text(product.get("serving_size"))

    # If still not found, try from product name
    if not final_quantity:
        final_quantity = extract_quantity_from_text(product_name_en)

    categorydata = find_categories(keywords, categories, product_name_en)

    data = {
        "code": code,
        "product_name_en": product_name_en,
        "energy_kcal_100g": energy_kcal_100g,
        "quantity": final_quantity,
        "brands": brands,
        "category": categorydata["category"],
        "categorystatus": categorydata["categorystatus"],
        "imageurl": imageurl
    }

    print(data)
    return data


def fetch_items_offAPI(barcode: str):
    """
    Fetch food item data from OpenFoodFacts API using barcode.
    
    Args:
        barcode: Product barcode
        
    Returns:
        dict: Processed food item data or error message
    """
    url = f"{OPENFOODFACTS_API}/{barcode}.json"
    response = requests.get(url)
    data = response.json()

    if data.get("status") == 1:
        return filter_data(data)

    return {"Message": "failed: fetch_items_offAPI"}


def scan_barcode_live():
    """
    Scan barcode using live camera feed.
    
    Returns:
        str: Barcode data or None if not found
    """
    if cv2 is None or pyzbar is None:
        return None
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            x, y, w, h = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            barcode_data = barcode.data.decode("utf-8")
            cap.release()
            cv2.destroyAllWindows()
            return barcode_data

        cv2.imshow('Barcode Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return None


def opencv_scan_barcode(image):
    """
    Scan barcode from a static image file.
    
    Args:
        image: Image filename (without extension)
    """
    if cv2 is None or pyzbar is None:
        return None
    frame = cv2.imread(f"./ai_food_tracker/app/images/{image}.jpg")

    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        barcode_data = barcode.data.decode("utf-8")

        print(barcode_data)
