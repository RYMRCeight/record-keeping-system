from record_keeper import RecordKeeper

# Initialize the RecordKeeper
def update_dates():
    keeper = RecordKeeper()
    records = keeper.get_all_records()
    updated = False

    # Update records with MM.DD.YYYY or MM/DD/YYYY format
    for record in records:
        if record.date and ('.' in record.date or '/' in record.date):
            parsed_date = keeper._parse_and_format_date(record.date)
            if parsed_date and parsed_date != record.date:
                print(f"Updating date from {record.date} to {parsed_date}")  # Debug
                record.date = parsed_date
                updated = True

    if updated:
        keeper.save_records()
        print("Records updated successfully.")
    else:
        print("No records requiring date updates.")

if __name__ == "__main__":
    update_dates()
