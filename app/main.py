import argparse

from ingestion.sync_ingestor import SyncIngestor

""" Later you can import AsyncIngestor for --mode async"""


def main():
    parser = argparse.ArgumentParser(description="Run ingestion pipeline")

    # Define the --mode argument to choose sync or async ingestion
    parser.add_argument(
        "--mode",
        choices=['sync', 'async'],  # Allowed options
        default="sync",  # Default mode if no argument passed
        help="Choose ingestion mode: sync or async"
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Select the Ingestor class based on --mode argument
    if args.mode == "sync":
        ingestor = SyncIngestor()

    else:
        """ Async ingestion not implemented yet"""
        raise NotImplementedError("Async mode not implemented yet")

    # Run the ingestion pipeline: fetch + process data
    data = ingestor.run()

    # Print the number of records processed a summary
    print(f"fecthed and processed {len(data)} records")


# Standard python entrypoint check
# Ensures this runs only when executing this script directly,
# not when imported as a module elsewhere

if __name__ == "__main__":
    main()
