Create table if not exists users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) enum ('admin', 'comrade', 'landlord', 'e_service') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists security_checks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    id_number INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) enum ('pending', 'verified') NOT NULL,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists Location_data (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    sales_id VARCHAR(50) REFERENCES sales_data(sales_id) ON DELETE CASCADE,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    address VARCHAR(255) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create tables if not exists sales_data (
    id SERIAL PRIMARY KEY,
    sales_id VARCHAR(50) UNIQUE NOT NULL,
    sales_name VARCHAR(100) NOT NULL,
    sales_type VARCHAR(100) enum ('products', 'services', 'rents') NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    stock INT NOT NULL DEFAULT 0,
    price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

Create table if not exists sales_moreInfo (
    id SERIAL PRIMARY KEY,
    sales_id VARCHAR(50) REFERENCES sales_data(sales_id) ON DELETE CASCADE,
    description TEXT,
    category VARCHAR(100),
    tags VARCHAR(255),
    warranty_period INT,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    additional_info JSONB
);

Create table if not exists images (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    sales_id VARCHAR(50) REFERENCES sales_data(sales_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    mpesa_code VARCHAR(50),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) enum ('pending', 'completed', 'failed') NOT NULL
);

Create table if not exists Mpesa_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    checkout_request_id VARCHAR(255) NOT NULL,
    mpesa_code VARCHAR(50),
    order_id VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    product_data JSONB,
    status VARCHAR(20) enum ('initiated', 'completed', 'failed') NOT NULL
);

Create table if not exists EmailOTP (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON DELETE CASCADE,
    email VARCHAR(100) REFERENCES users(email) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) enum ('admin', 'comrade', 'landlord', 'e_service') NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE
);

Create table if not exists orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    sales_id VARCHAR(50) REFERENCES sales_data(sales_id) ON DELETE CASCADE,
    total_price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) enum ('pending', 'shipped', 'delivered', 'cancelled') NOT NULL
);

Create table if not exists order_items (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(order_id) ON DELETE CASCADE,
    sales_id VARCHAR(50) REFERENCES sales_data(sales_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL
    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists cart_items (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    sales_id VARCHAR(50) REFERENCES sales_data(sales_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


Create table if not exists e_earnings(
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    earning_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100) NOT NULL
);


Create table if not exists audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);