from flask import Flask, jsonify, request
import mysql.connector
import os # Imports should be at the top of the file

app = Flask(__name__)

# --- CORRECT DATABASE CONNECTION FOR RENDER ---
# This function reads the secure database URL provided by Render
# and establishes a connection.
def get_db_connection():
    # The DATABASE_URL is automatically set by Render in your environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")

    # The URL format is mysql://user:password@host:port/database
    # We need to parse it for the mysql.connector library
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
        # This will print a more helpful error to the Render logs if connection fails
        print(f"Error connecting to database: {e}")
        raise

@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, stock, price) VALUES (%s, %s, %s)",
        (data['name'], data['stock'], data['price'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Product added'}), 201

# --- CORRECT INDENTATION ---
if __name__ == '__main__':
    # The port is automatically handled by Render's web service environment
    # We don't need to specify it here when using the 'flask run' command
    # The Dockerfile's CMD ["flask", "run"] will handle this.
    # For local testing, you might still want to define a port.
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)
