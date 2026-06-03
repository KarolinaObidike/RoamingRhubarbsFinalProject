# THIS CODE WILL RUN THE FULL ETL PIPELINE
from databases import create_database, connectdb
from ETL import Extract, transform
from ETL.load import load_all


def main():
    create_database.setup_db()

    rawdata = Extract.get_data()
    transformed_data = transform.transform(rawdata)

    with connectdb.get_connection() as conn:
        load_counts = load_all(transformed_data, conn)

    print("Load completed successfully.")
    print(load_counts)


if __name__ == "__main__":
    main()
