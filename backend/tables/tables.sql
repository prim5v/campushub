CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,      -- optional email
    phone VARCHAR(50) UNIQUE NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'comrade', 'landlord', 'e_service') NOT NULL,
    plan VARCHAR(50) NULL DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    session_id VARCHAR(100) NOT NULL UNIQUE,
    user_id VARCHAR(50) NOT NULL,

    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    device_id VARCHAR(50),
    device_name VARCHAR(100),
    browser VARCHAR(50),
    os VARCHAR(50),
    ip_address VARCHAR(50),
    location_address VARCHAR(100),

    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS security_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NULL,
    id_number VARCHAR(50) NULL,
    full_name VARCHAR(100) NULL,
    check_type ENUM('landlord', 'comrade', 'e_service') NULL,
    status ENUM('pending', 'verified') NOT NULL DEFAULT 'pending',
    reviewed_by VARCHAR(50),
    review_notes TEXT,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;


Create table if not exists images (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NULL,
    tenant_id VARCHAR(50) NULL,
    session_id VARCHAR(50) NULL,
    listing_id VARCHAR(50) NULL,
    property_id VARCHAR(50) NULL,
    product_id VARCHAR(50) NULL,
    service_id VARCHAR(50) NULL,
    image_url VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE verification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    session_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS email_otp (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    email VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL,

    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'comrade', 'landlord', 'e_service') NOT NULL,

    otp_code VARCHAR(10) NOT NULL,
    plan VARCHAR(50) NULL DEFAULT 'free',
    expires_at TIMESTAMP NOT NULL,

    attempts INT DEFAULT 0,
    used BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(email)
);

CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    landlord_id INT REFERENCES landlords(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    price DECIMAL(10,2),
    deposit DECIMAL(10,2),
    location VARCHAR(255),
    distance VARCHAR(50),
    size VARCHAR(50),
    max_occupants INT,
    available_from DATE,
    description TEXT,
    verified BOOLEAN DEFAULT FALSE,
    rating DECIMAL(2,1),
    reviews_count INT DEFAULT 0
);



Create table if not exists listings_data (
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR(50) UNIQUE NOT NULL,
    property_id VARCHAR(50) REFERENCES properties_data(property_id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    listing_name VARCHAR(100) NOT NULL,
    listing_description TEXT NOT NULL,
    deposits JSON,
    room_size VARCHAR(50),
    max_occupants INT NULL,
    listing_type enum ('apartment', 'bedsitter', 'hostel'),
    price DECIMAL(10,2) NOT NULL,
    renting_price DECIMAL(10,2) NULL,
    timeline enum ('daily', 'weekly', 'monthly') NOT NULL,
    availability_status enum ('available', 'rented') NOT NULL,
    availability_date TIMESTAMP,
    listed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



Create table if not exists properties_data (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    verified BOOLEAN DEFAULT FALSE,
    property_name VARCHAR(100) NOT NULL,
    property_description TEXT NOT NULL,
    property_type enum ('house', 'apartment', 'condo', 'townhouse', 'hostel', 'bedsitter'),
    listed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE amenities (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) NOT NULL UNIQUE,
    label VARCHAR(100) NOT NULL
);


CREATE TABLE listings_amenities (
    listing_id VARCHAR(50) REFERENCES listings_data(listing_id) ON DELETE CASCADE,
    amenity_id INT REFERENCES amenities(id) ON DELETE CASCADE,
    available BOOLEAN DEFAULT TRUE,
    PRIMARY KEY(listing_id, amenity_id)
);



create table if not exists reviews(
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR(50) NULL,
    user_id VARCHAR(50) NULL,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


Create table if not exists Location_data (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    property_id VARCHAR(50) NULL,
    listing_id VARCHAR(50) NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    address VARCHAR(255) NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists products_data (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists product_moreInfo (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) REFERENCES products_data(product_id) ON DELETE CASCADE,
    description TEXT,
    category VARCHAR(100),
    tags VARCHAR(255),
    warranty_period INT,
    period_unit enum ('days', 'months', 'years'),
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    additional_info JSON
);


Create table if not exists documents(
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NULL,
    product_id VARCHAR(50) NULL,
    document_url VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists e_service_data (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    service_description TEXT NULL,
    price DECIMAL(10,2) NOT NULL,
    availability_status enum ('available', 'unavailable') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id VARCHAR(50),
    role VARCHAR(20) NOT NULL DEFAULT 'unknown',

    action VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    method VARCHAR(10),

    ip_address VARCHAR(45),
    user_agent TEXT,
    device_id VARCHAR(100),

    status ENUM('success','failure') NOT NULL DEFAULT 'success',

    details TEXT,
    metadata JSON,

    target_user_id VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id VARCHAR(50),

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);





Create table if not exists transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    paid_by JSON,
    paid_to JSON,
    title VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    transaction_type enum ('income', 'expense') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    mpesa_code VARCHAR(50) NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status enum ('pending', 'completed', 'failed', 'partial') NOT NULL
);


Create table if not exists Mpesa_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    checkout_request_id VARCHAR(255) NOT NULL,
    mpesa_code VARCHAR(50),
    order_id VARCHAR(100) NULL,
    booking_id VARCHAR(100) NULL,
    phone VARCHAR(15) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    product_data JSON,
    status VARCHAR(20) enum ('initiated', 'completed', 'failed') NOT NULL
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

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    booking_id VARCHAR(50) UNIQUE NOT NULL,
    listing_id VARCHAR(50) REFERENCES listings_data(listing_id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    phone_number VARCHAR(50) NOT NULL,
    amount INT NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    booking_status VARCHAR(50) NOT NULL,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(50) UNIQUE NOT NULL,
    listing_id VARCHAR(50) REFERENCES listings_data(listing_id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    phone_number VARCHAR(50) NOT NULL,
    full_name VARCHAR(50) NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Create table if not exists tenants_data(
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) UNIQUE NOT NULL,
    tenant_name VARCHAR(100) UNIQUE NOT NULL,
    tenant_email VARCHAR(100) UNIQUE NOT NULL,
    tenant_phone VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    listing_id VARCHAR(50) REFERENCES listings_data(listing_id) ON DELETE CASCADE,
    lease_start_date TIMESTAMP NOT NULL,
    lease_end_date TIMESTAMP NOT NULL,
    rent_amount DECIMAL(10,2) NOT NULL,
    payment_schedule enum ('monthly', 'quarterly', 'yearly') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

Create table if not exists rent_payments(
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(50) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) REFERENCES Tenants_data(tenant_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL,
    status enum ('pending', 'completed', 'failed') NOT NULL
);

Create table if not exists tenant_deposits(
    id SERIAL PRIMARY KEY,
    deposit_id VARCHAR(50) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) REFERENCES Tenants_data(tenant_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    deposit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status enum ('held', 'refunded', 'forfeited') NOT NULL
);

Creaate table if not exists reports(
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) REFERENCES tenants_data(tenant_id) ON DELETE CASCADE,
    property_id VARCHAR(50) REFERENCES properties_data(property_id) ON DELETE
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    report_data JSON NOT NULL,
    report_status enum ('open', 'in_progress', 'resolved', 'closed') NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plan_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    price INT NOT NULL,
    period VARCHAR(20) NOT NULL,
    description TEXT,
    features JSON NOT NULL,
    not_included JSON NOT NULL,
    popular BOOLEAN DEFAULT FALSE,
    properties_limit INT DEFAULT 1,
    listings_limit INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE pending_landlord_signups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    plan_id INT NOT NULL,
    checkout_request_id VARCHAR(100) NOT NULL,
    status ENUM('pending_payment','paid','failed') DEFAULT 'pending_payment',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_checkout (checkout_request_id),
    UNIQUE KEY uniq_email (email)
);

