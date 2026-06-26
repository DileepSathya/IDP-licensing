CREATE TRIGGER trg_set_expiry_date
BEFORE INSERT ON clients_licenses
FOR EACH ROW
EXECUTE FUNCTION set_expiry_date();