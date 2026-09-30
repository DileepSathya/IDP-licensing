# IDP Invoice license issuer

`IDP-lic_website` is the only application that generates and signs IDP Invoice
licenses. Keep `keygen/private_key.pem` in this repository's secured deployment;
never copy or bundle it into `IDP_2.0-INVOICE`.

## Machine fingerprint contract

Customers must use the current `fingerprint_tool.exe` distributed with
`IDP_2.0-INVOICE`. It creates a lowercase 64-character SHA-256 fingerprint from
exactly:

- `Win32_Processor.ProcessorId`
- The physical serial number of the disk containing the Windows system drive

The canonical input is `CPU=<NORMALIZED_ID>|DISK=<NORMALIZED_SERIAL>`. The
website receives and stores only its SHA-256 hash. It never receives raw CPU or
disk identifiers.

The website rejects blank, legacy, non-hexadecimal, or non-64-character
fingerprints before loading the signing key, creating a license file, or writing
a database record.

## Customer flow

1. Customer downloads the current fingerprint tool from the licence page.
2. Customer runs it on the Windows machine that will run IDP Invoice.
3. Customer pastes the displayed 64-character fingerprint into the licence page.
4. The website signs the selected plan, expiry/quota, customer ID, issue time,
   and fingerprint and downloads `license.lic`.
5. Customer pastes the license key under **Settings → Licensing** in
   `IDP_2.0-INVOICE`.

Changing the CPU or Windows system disk requires a new fingerprint and license.
Network, VPN, and non-system-disk changes do not affect the fingerprint.

## Migration

Licenses created with the retired MAC/CPU-name/WMIC fingerprint algorithm are
not accepted by the new Invoice application. Rebuild and publish the current
fingerprint tool, collect a new fingerprint for every customer, and issue a new
license from this website.
