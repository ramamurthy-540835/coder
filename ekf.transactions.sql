CREATE OR REPLACE TABLE `ctoteam.ekf.transactions` (
    transaction_id STRING NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    customer_id STRING,
    store_id STRING,
    channel STRING NOT NULL,
    product_sku STRING NOT NULL,
    quantity INT64 NOT NULL,
    item_price NUMERIC NOT NULL,
    discount_amount NUMERIC NOT NULL,
    tax_amount NUMERIC NOT NULL,
    payment_method STRING,
    transaction_type STRING NOT NULL
)
PARTITION BY DATE(transaction_time)
CLUSTER BY customer_id, product_sku;

OPTIONS (
    description = 'Atomic-level transactions',
    labels = [('retail_business_domain', 'transactions')]
);
