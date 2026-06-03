Check over each individual task, does the result meet the requirements given by the product owner.
# Does it do, what it needs to be doing?
# Do any errors occur? 
# Are there ways implemented, for preventing those errors?
# Have the errors being handled, after the pipeline was ran again?
# Was the review by another team member done, and correctly?

Example: CSV Data Extraction (Task)
- CSV loads successfully
- Rows converted successfully into Python objects
- No errors occur with mock/sample file


## RFP-14 Convert create SQL script to .sql format instead
02/06/2026

- A standalone `.sql` schema file exists in `databases/db-scripts/`
- The SQL file contains the full table creation script
- The SQL file does not depend on Python to create the schema
- The old Python schema creation file no longer contains the active schema definition
- Documentation has been updated to show where the schema file lives
- Work has been reviewed by another team 

## RFP-11 Transform - Normalise data to match schema
02/06/2026
- Sensitive fields are removed before normalisation.
- `items ordered` is split into separate item records.
- Product names and prices are separated.
- UUIDs are generated in Python.
- Data is shaped for the database tables: branches, payment_type, products, transactions, and transaction_items.
- Foreign key relationships are preserved in the transformed data.
- Transform output is tested/reviewed before moving ticket to Done.
