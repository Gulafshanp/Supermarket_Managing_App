import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime


# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://gulafshan302003:1nfAp8AygOIH1RCS@cluster0.8cvfvhg.mongodb.net/?retryWrites=true&w=majority")
db = client["supermarket"]
products_collection = db["products"]
inventory_collection = db["inventory"]
orders_collection = db["orders"]
staff_collection = db["staff"]
departments_collection = db["departments"]
revenues_collection = db["revenues"]

# Helper functions
def add_product(name, price, quantity, category):
    product = {
        "name": name,
        "price": price,
        "quantity": quantity,
        "category": category
    }
    products_collection.insert_one(product)

def get_products():
    products = list(products_collection.find())
    return products

def update_product_quantity(product_id, quantity):
    products_collection.update_one({"_id": product_id}, {"$set": {"quantity": quantity}})

def add_order(product_id, quantity):
    product = products_collection.find_one({"_id": product_id})
    if product:
        order = {
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "total_amount": product["price"] * quantity,
            "order_date": datetime.now()
        }
        orders_collection.insert_one(order)
        update_product_quantity(product_id, product["quantity"] - quantity)

def delete_product(product_id):
    product = products_collection.find_one({"_id": product_id})
    if product:
        confirmation = st.warning(f"Are you sure you want to delete {product['name']}? This action cannot be undone.")
        if confirmation.button("Delete"):
            products_collection.delete_one({"_id": product_id})
            st.success("Product deleted successfully!")

def add_staff(name, department, salary):
    staff = {
        "name": name,
        "department": department,
        "salary": salary
    }
    staff_collection.insert_one(staff)

def get_staff():
    staff = list(staff_collection.find())
    return staff

def add_department(name):
    department = {
        "name": name
    }
    departments_collection.insert_one(department)

def get_departments():
    departments = list(departments_collection.find())
    return departments

def add_revenue(amount):
    revenue = {
        "amount": amount,
        "date": datetime.now()
    }
    revenues_collection.insert_one(revenue)

def get_revenues():
    revenues = list(revenues_collection.find())
    return revenues
def add_to_cart(product_id, quantity):
    product = products_collection.find_one({"_id": product_id})
    if product:
        cart_item = {
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "price": product["price"]
        }
        cart_collection = db["cart"]
        cart_collection.insert_one(cart_item)

def get_cart():
    cart_collection = db["cart"]
    cart_items = list(cart_collection.find())
    return cart_items

def delete_cart_item(cart_item_id):
    cart_collection = db["cart"]
    cart_item = cart_collection.find_one({"_id": cart_item_id})
    if cart_item:
        confirmation = st.warning(f"Are you sure you want to delete {cart_item['product_name']} from cart? This action cannot be undone.")
        if confirmation.button("Delete"):
            cart_collection.delete_one({"_id": cart_item_id})
            st.success("Cart item deleted successfully!")


# Streamlit application
def main():
    st.title("Supermarket Management Application 🛒")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page_options = ["Add Product", "View Products", "Place Order", "Add Staff", "View Staff", "Add Department",
                    "View Departments", "Add Revenue", "View Revenues", "View Cart"]
    selected_page = st.sidebar.radio("", options=page_options)

    if selected_page == "Add Product":
        st.header("Add Product")
        product_name = st.text_input("Product Name")
        product_price = st.number_input("Product Price", min_value=0.0)
        product_quantity = st.number_input("Product Quantity", min_value=0)
        product_category = st.selectbox("Product Category", ["Grocery", "Produce", "Dairy", "Bakery"])
        if st.button("Add"):
            add_product(product_name, product_price, product_quantity, product_category)
            st.success("Product added successfully!")

    elif selected_page == "View Products":
        st.header("View Products")
        products = get_products()
        if len(products) > 0:
            df = pd.DataFrame(products)
            st.dataframe(df)
        else:
            st.info("No products found.")
        delete_product_id = st.selectbox("Select Product to Delete", options=[product["_id"] for product in products])
        if st.button("Delete"):
            delete_product(delete_product_id)
        
    
       elif selected_page == "Place Order":
            st.header("Place Order")
            products = get_products()
            product_options = {product["name"]: product["_id"] for product in products}
            selected_product = st.selectbox("Select Product", list(product_options.keys()))
            order_quantity = st.number_input("Order Quantity", min_value=1)
            if st.button("Add to Cart"):
                product_id = product_options[selected_product]
                add_to_cart(product_id, order_quantity)
                st.success("Product added to cart!")
            elif st.button("View Cart"):
                cart_items = get_cart()
                if len(cart_items) > 0:
                    df = pd.DataFrame(cart_items)
                    st.dataframe(df)
                else:
                    st.info("Your cart is empty.")
            elif st.button("Checkout"):
                st.success("Checkout not yet implemented.")



    elif selected_page == "Add Staff":
        st.header("Add Staff")
        staff_name = st.text_input("Staff Name")
        staff_department = st.selectbox("Staff Department",
                                        options=[department["name"] for department in get_departments()])
        staff_salary = st.number_input("Staff Salary", min_value=0)
        if st.button("Add"):
            add_staff(staff_name, staff_department, staff_salary)
            st.success("Staff added successfully!")

    elif selected_page == "View Staff":
        st.header("View Staff")
        staff = get_staff()
        if len(staff) > 0:
            df = pd.DataFrame(staff)
            st.dataframe(df)
        else:
            st.info("No staff found.")

    elif selected_page == "Add Department":
        st.header("Add Department")
        department_name = st.text_input("Department Name")
        if st.button("Add"):
            add_department(department_name)
            st.success("Department added successfully!")

    elif selected_page == "View Departments":
        st.header("View Departments")
        departments = get_departments()
        if len(departments) > 0:
            df = pd.DataFrame(departments)
            st.dataframe(df)
        else:
            st.info("No departments found.")

    elif selected_page == "Add Revenue":
        st.header("Add Revenue")
        revenue_amount = st.number_input("Revenue Amount", min_value=0.0)
        if st.button("Add"):
            add_revenue(revenue_amount)
            st.success("Revenue added successfully!")

    elif selected_page == "View Revenues":
        st.header("View Revenues")
        revenues = get_revenues()
        if len(revenues) > 0:
            df = pd.DataFrame(revenues)
            st.dataframe(df)
        else:
            st.info("No revenues found!")


# Generate random products
def generate_products(num_products):
    categories = ["Grocery", "Produce", "Dairy", "Bakery"]
    products = []
    for _ in range(num_products):
        name = fake.word()
        price = round(random.uniform(1, 100), 2)
        quantity = random.randint(1, 100)
        category = random.choice(categories)
        product = {
            "name": name,
            "price": price,
            "quantity": quantity,
            "category": category
        }
        products.append(product)
    return products

# Generate random staff
def generate_staff(num_staff):
    departments = ["Department A", "Department B", "Department C", "Department D"]
    staff = []
    for _ in range(num_staff):
        name = fake.name()
        department = random.choice(departments)
        salary = round(random.uniform(1000, 5000), 2)
        staff_member = {
            "name": name,
            "department": department,
            "salary": salary
        }
        staff.append(staff_member)
    return staff

# Generate random departments
def generate_departments(num_departments):
    departments = []
    for _ in range(num_departments):
        name = fake.word()
        department = {
            "name": name
        }
        departments.append(department)
    return departments

# Generate random revenues
def generate_revenues(num_revenues):
    revenues = []
    for _ in range(num_revenues):
        amount = round(random.uniform(1000, 5000), 2)
        revenue = {
            "amount": amount,
            "date": fake.date_time_this_year()
        }
        revenues.append(revenue)
    return revenues




if __name__ == "__main__":
    main()

st.sidebar.markdown('---')
st.sidebar.write('Made with ❤️ by [Gulafshan]')

