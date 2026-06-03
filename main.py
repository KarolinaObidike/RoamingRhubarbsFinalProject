# THIS CODE WILL RUN THE FULL ETL PIPELINE
from databases import connectdb
from ETL import Extract, Transform
from ETL.load import load_all


def main():


    rawdata = Extract.get_data()
    transformed_data = Transform.transform(rawdata)

    with connectdb.get_connection() as conn:
        load_counts = load_all(transformed_data, conn)

    print("Load completed successfully.")
    print(load_counts)


if __name__ == "__main__":
    main()
