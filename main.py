#Ramtin Abolfazli 101419226
#Sherry Zarei 101274382
import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS Product (
                    ProductId INTEGER PRIMARY KEY AUTOINCREMENT,
                    ProductName TEXT,
                    ProductPrice REAL,
                    ProductCategory TEXT,
                    Product_Type TEXT
                )'''
        self.execute_query(query)
        self.commit()

    def insert_product(self, name, price, category, productType):
        query = "INSERT INTO Product(ProductName, ProductPrice, ProductCategory, Product_Type) VALUES (?, ?, ?, ?)"
        params = (name, price, category, productType)
        self.execute_query(query, params)
        self.commit()



def insert_products(db_manager, products):
    for name, price, category, productType in products:
        try:
            existing_product = db_manager.execute_query("SELECT * FROM Product WHERE ProductName = ?", (name,))
            if not existing_product:
                db_manager.insert_product(name, price, category, productType)
                db_manager.commit()
        except Exception as e:
            print(f"Error inserting product {name}: {e}")

class ShoppingCart:
    def __init__(self):
        self.db_manager = Database("Python.db")
        self.single_items = []
        self.combo_items = []
        self.confirmation = False

    #this function will be used inside order_products function
    def add_item(self, item_id, items, quantity):
        try:
            product = self.db_manager.execute_query("SELECT * FROM Product where ProductId = ?", (item_id,))
            if not product:
                print("Product not found")
                return
            elif items == "combo":
                self.combo_items.append((product, quantity))
            elif items == "sale":
                self.single_items.append((product, quantity))
            else:
                print("Invalid Item Type")
        except Exception as e:
            print("Error Inserting Item Type", e)

    #This function will be used inside the view_products function
    def print_products(self, p_type=None):
        print("+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10)
        print("|{:<10}|{:<15}|{:<10}|{:<15}|{:<10}|".format("Id", "Name", "Price", "Category", "ProductType"))
        print("+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10)
        if p_type:
            rows = self.db_manager.execute_query("SELECT * FROM Product WHERE Product_Type = ?", (p_type,))
        else:
            rows = self.db_manager.execute_query("SELECT * FROM Product")
        for row in rows:
            print("|{:<10}|{:<15}|{:<10}|{:<15}|{:<10}|".format(row[0], row[1], row[2], row[3], row[4]))
        print("+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10)

    def view_products(self):
        print("Here is the list of our products:")
        self.print_products()
        global items
        while True:
            items = input("Would you like to order Combo items or single item? Enter Combo or Single: ")
            if items.lower() == "combo":
                self.print_products("Combo")
                break
            elif items.lower() == "single":
                self.print_products("sale")
                break
            else:
                print("Invalid Input")
                continue

    def order_products(self):
        count = 0  # Initialize count outside the loop
        while True:
            try:
                item_id = input("Please enter the id of the product you would like to order: ")
                quantity = input("Please enter the quantity of the product you would like to order: ")
            except ValueError:
                print("Invalid Input")
                continue

            try:
                item_id = int(item_id)
                quantity = int(quantity)
                if quantity <= 0:
                    print("Quantity must be greater than 0")
                    continue
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
                continue

            self.add_item(item_id, "sale" if items == "single" else "combo", quantity)
            count += 1
            if items.lower() == "combo" and count <= 1:
                print("You need to order at least two different items")
                continue

            while True:
                choose = input("Would you like to add another item? (Y/N): ").lower()
                if choose == 'y' or choose == 'n':
                    break
                else:
                    print("Invalid Input")
                    continue

            if choose.lower() == "n":
                break

    def shopping_cart(self):
        if not self.single_items and not self.combo_items:
            print("Your shopping card is empty. Please try again.")
            return
        while True:
            self.generate_receipt()
            answer = input("Would you like to purchase these items? (Y/N): ").lower()
            if answer == "y":
                self.confirmation = True
                print("Here is your receipt: ")
                self.generate_receipt()
                print("Receipt has been saved in '{}'".format(receipt_file_name))
                print("Thanks for shopping with us...")
                break
            elif answer == "n":
                break
            else:
                print("Invalid Input. Please enter 'Y' or 'N'.")

    def generate_receipt(self):
        global receipt_file_name
        receipt_file_name = "receipt.txt"
        receipt_content = ""
        receipt_content += ("+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 5 +"\n")
        receipt_content += ("|{:<10}|{:<15}|{:<10}|{:<15}|{:<10}|{:<5}|".format("Id", "Name", "Price", "Category", "ProductType",
                                                                  "quantity\n"))
        receipt_content += ("+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 5 + "\n")
        total_price = 0
        total_quantity = 0

        for item_name, item_quantity in self.single_items:
            item = item_name[0]
            price = float(item[2][1:])
            receipt_content += ("|{:<10}|{:<15}|{:<10}|{:<15}|{:<10}|{:<5}|\n".format(item[0], item[1], item[2], item[3], item[4],
                                                                      item_quantity))
            total_price += item_quantity * price
            total_quantity += item_quantity

        for item_name, item_quantity in self.combo_items:
            item = item_name[0]
            price = float(item[2][1:])
            receipt_content += ("|{:<10}|{:<15}|{:<10}|{:<15}|{:<10}|{:<5}|\n".format(item[0], item[1], item[2], item[3], item[4],
                                                                      item_quantity))
            total_price += item_quantity * price * 0.97  # 3% discount for purchasing combo items
            total_quantity += item_quantity
        receipt_content += ("+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 15 + "+" + "-" * 10 + "+" + "-" * 5 + "\n")

        if total_quantity >= 10:
            total_price *= 0.95  # 5% discount if the items are more than 10

        if total_price < 75:
            total_price += 9.99  # shipping fee if it costs less that 75

        total_price *= 1.13  # including tax

        receipt_content += ("Total price: ${:,.2f}\n".format(total_price))

        print(receipt_content)
        with open("receipt.txt", "w") as f:
            f.write(receipt_content)


def main():
    db_manager = Database("Python.db")
    db_manager.create_table()
    products = [
        ['Jean', 60, 'Clothing', 'Combo'],
        ['Nike Shirt', 40, 'Clothing', 'sale'],
        ['Adidas shoes', 120, 'Clothing', 'sale'],
        ['MacBook Air', 1750, 'Electronics', 'sale'],
        ['Lenovo Laptop', 1600, 'Electronics', 'Combo'],
        ['S23 Samsung', 1100, 'Electronics', 'sale'],
        ['Educated', 21, 'Books', 'Combo'],
        ['The Stranger', 25, 'Books', 'Combo'],
        ['Animal Farm', 15, 'Books', 'sale']
    ]

    insert_products(db_manager, products)
    shopping_cart = ShoppingCart()

    print("Hello And welcome to our Online shop.")
    name = input("Please enter your name: ")
    while True:
        try:
            print("What would you like to do in our online shop?\n"
              "1. View Products\n"
              "2. Shopping card\n"
              "3. View your receipt\n"
              "4. Exit")
            choice = int(input("Please enter your choice: "))
        except ValueError:
            print("Invalid Input. Please try again.")
            continue
        if choice == 1:
            shopping_cart.view_products()
            shopping_cart.order_products()
        elif choice == 2:
            shopping_cart.shopping_cart()
        elif choice == 3:
            if shopping_cart.confirmation == True:
                shopping_cart.generate_receipt()
            else:
                print("Nothing has been purchased yet. Please go to your shopping card.")
        elif choice == 4:
            print("Have a good rest of your day!")
            break
        else:
            print("Invalid Input.")

if __name__ == "__main__":
    main()


