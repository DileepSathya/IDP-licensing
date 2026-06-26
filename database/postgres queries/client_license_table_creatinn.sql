CREATE TABLE clients_licenses (

    email           CITEXT NOT NULL,
    fingerprint_id  VARCHAR(255) NOT NULL,
    plan            VARCHAR(20) NOT NULL CHECK (LOWER(plan) IN ('monthly', 'yearly', 'quota', 'onetime')),
    issue_date      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expiry_date     TIMESTAMP WITH TIME ZONE,
    quota           INT,
    license_file_path VARCHAR(255)
);