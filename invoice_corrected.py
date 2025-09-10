from datetime import datetime
import mysql.connector

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="anu_.103",
    database="product_sale"
)
cursor = conn.cursor()

# ✅ Auto-increment Invoice Number
cursor.execute("SELECT MAX(invoice_no) FROM transaction_file")
result = cursor.fetchone()
invoice_no = (result[0] or 0) + 1

# ✅ Date Auto-Fill
invoice_date = datetime.today().strftime("%Y-%m-%d")
supply_date = invoice_date

# ✅ Party Info
party = {
    "party_id": input("Party ID: ").strip(),
    "party_name": input("Party Name: ").strip(),
    "address": input("Address: ").strip(),
    "city": input("City: ").strip(),
    "state": input("State: ").strip(),
    "pin_code": input("Pin Code: ").strip(),
    "contact_number": input("Contact Number: ").strip(),
    "email_id": input("Email ID: ").strip(),
    "GSTN": input("GST Number: ").strip(),
    "pan_number": input("PAN Number: ").strip(),
    "credit_limit": "0",
    "outstanding_balance": "0",
    "status": "Active"
}

cursor.execute("""
    INSERT INTO party_master (
        party_id, party_name, address, city, state, pin_code,
        contact_number, email_id, GSTN, pan_number,
        credit_limit, outstanding_balance, status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", tuple(party.values()))

# ✅ Products List
products = {
    "510100023": {"name": "GHEE 500 ML", "rate": 514.80, "stock": 100},
    "510100002": {"name": "PANEER 200 GM", "rate": 177.84, "stock": 100},
    "510100013": {"name": "GULAB JAMUN 1 KG", "rate": 346.55, "stock": 100},
    "510100015": {"name": "RASSAGULLA 100 GM", "rate": 33.63, "stock": 100}
}

selected_products = []

while True:
    print("\nAvailable Products:")
    for pid, p in products.items():
        print(f"{pid} | {p['name']} | ₹{p['rate']} | Stock: {p['stock']}")

    pid = input("Enter Product ID: ").strip()
    if pid not in products:
        print("❌ Invalid Product ID")
        continue

    try:
        qty = int(input(f"Enter quantity for {products[pid]['name']}: "))
    except ValueError:
        print("❌ Quantity must be a number.")
        continue

    if qty > products[pid]["stock"]:
        print("⚠️ Not enough stock.")
        continue

    rate = products[pid]["rate"]
    value = qty * rate
    cgst = round(value * 0.025, 2)
    sgst = round(value * 0.025, 2)
    total = round(value + cgst + sgst, 2)

    selected_products.append({
        "product_id": pid,
        "product_name": products[pid]["name"],
        "qty": qty,
        "rate": rate,
        "cgst": cgst,
        "sgst": sgst,
        "total": total
    })

    products[pid]["stock"] -= qty

    more = input("Add more products? (yes/no): ").lower()
    if more != "yes":
        break

# ✅ Payment Info
payment_mode = "Cash"
amount_received = sum([p["total"] for p in selected_products])
excess = 0

# ✅ Insert into transaction_file
for item in selected_products:
    cursor.execute("""
        INSERT INTO transaction_file (
            invoice_no, invoice_date, supply_date,
            payment_mode, amount_recieved, excess_amount,
            product_ID, product_name, unit,
            quantity, rate, GST_rate, product_value
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        invoice_no, invoice_date, supply_date,
        payment_mode, amount_received, excess,
        item["product_id"], item["product_name"], "Units",
        item["qty"], item["rate"], 5.0, item["total"]
    ))

# ✅ Generate Invoice String
invoice_text = "\n"
invoice_text += "          PATNA DAIRY PROJECT\n"
invoice_text += "               TAX INVOICE\n\n"
invoice_text += f"INVOICE NO. {invoice_no}       INVOICE DATE: {invoice_date}\n\n"
invoice_text += "Sno  Product              Qty  Rate   CGST   SGST   Total\n"
invoice_text += "-" * 60 + "\n"

grand_total = 0
for idx, item in enumerate(selected_products, 1):
    invoice_text += f"{idx:<4} {item['product_name'][:18]:<18} {item['qty']:<4} {item['rate']:<6.2f} {item['cgst']:<6.2f} {item['sgst']:<6.2f} {item['total']:<.2f}\n"
    grand_total += item['total']

invoice_text += "\n" + " " * 40 + f"Total = ₹{grand_total:.2f}\n"
invoice_text += "\nAuthorised Signature\n"
invoice_text += "_" * 25 + "\n"

# ✅ Print to console
print(invoice_text)

# ✅ Save to file
file_name = f"invoice_{invoice_no}.txt"
with open(file_name, "w", encoding="utf-8") as f:  # FIXED encoding
    f.write(invoice_text)

print(f"\n✅ Invoice saved as '{file_name}'")

# ✅ Commit and close
conn.commit()
conn.close()