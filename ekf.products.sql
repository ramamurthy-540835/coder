CREATE OR REPLACE TABLE `ctoteam.ekf.products` (
    product_sku STRING NOT NULL,
    product_name STRING NOT NULL,
    brand STRING,
    category_l1 STRING,
    category_l2 STRING,
    current_retail_price NUMERIC NOT NULL,
    is_active BOOL NOT NULL
)
CLUSTER BY brand, category_l1;

OPTIONS (
    description = 'Curated product catalog',
    labels = [('retail_business_domain', 'products')]
);
