CREATE OR REPLACE FUNCTION set_expiry_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expiry_date IS NULL THEN
        CASE LOWER(NEW.plan)
            WHEN 'monthly' THEN
                NEW.expiry_date := NEW.issue_date + INTERVAL '1 month';
            WHEN 'yearly' THEN
                NEW.expiry_date := NEW.issue_date + INTERVAL '1 year';
            WHEN 'quota' THEN
                NEW.expiry_date := NULL;
            WHEN 'onetime' THEN
                NEW.expiry_date := NULL;
        END CASE;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;