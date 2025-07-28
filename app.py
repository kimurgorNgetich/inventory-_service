from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

# This is the same database connection function from the inventory service.
# It reads the database URL from the environment variables.
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")

    try:
        url_parts = database_url.replace('mysql://', '').split('@')
        user_pass, host_db = url_parts[0], url_parts[1]
        user, password = user_pass.split(':')
        host_port, database = host_db.split('/')
        host, port = host_port.split(':')

        conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# A welcome route for the root URL
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the Order Service API!",
        "endpoints": {
            "get_all_orders": "GET /orders",
            "create_new_order": "POST /orders"
        }
    })

# Endpoint to get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(orders)

# Endpoint to create a new order
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    # Basic validation to ensure required data is present
    if not data or 'product_id' not in data or 'quantity' not in data or 'price' not in data:
        return jsonify({'error': 'Missing data: product_id, quantity, and price are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (product_id, quantity, price) VALUES (%s, %s, %s)",
            (data['product_id'], data['quantity'], data['price'])
        )
        conn.commit()
        # Get the ID of the new order to return it
        new_order_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'message': 'Order created successfully', 'order_id': new_order_id}), 201
    except mysql.connector.Error as err:
        # This will catch errors, like if the product_id doesn't exist
        return jsonify({'error': f'Database error: {err}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003)) # Use a different port for local testing
    app.run(host="0.0.0.0", port=port)
