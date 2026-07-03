CREATE OR REPLACE TABLE `ctoteam.ekf.customers` (
    customer_id STRING NOT NULL,
    external_crm_id STRING,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone_number STRING,
    registration_date DATE,
    last_purchase_date DATE,
    total_spend_lifetime NUMERIC,
    loyalty_tier STRING
)
CLUSTER BY loyalty_tier, last_purchase_date;

OPTIONS (
    description = 'Unified customer master record',
    labels = [('retail_business_domain', 'customers')]
);
