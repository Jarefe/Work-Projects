import pandas as pd


def clean_column_names(df):
    """Normalize column names: remove extra spaces and non-breaking characters."""
    df.columns = [' '.join(col.strip().split()) for col in df.columns]
    return df


def get_field(row, field_name):
    """Safely extract a field or return placeholder if missing."""
    value = row.get(field_name, None)
    if pd.isna(value):
        return f"[{field_name}]"
    cleaned = ' '.join(str(value).strip().split())
    return cleaned if cleaned else f"[{field_name}]"


def lookup_row(dataframe, identifier):
    """Find the row based on PO-Line (e.g., '1234-56') or Serial Number."""
    if '-' in identifier:
        parts = identifier.split('-')
        if len(parts) == 2 and all(part.strip().isdigit() for part in parts):
            po, line = parts[0].strip(), parts[1].strip()
            row = dataframe[
                (dataframe['PO#'].astype(str).str.strip() == po) &
                (dataframe['Line#'].astype(str).str.strip() == line)
                ]
            if row.empty:
                return None, f"No record found for PO#: {po}, Line#: {line}"
        else:
            return None, "Invalid PO-Line format. Use '1234-56'."
    else:
        sn = identifier.strip()
        row = dataframe[dataframe['SN'].astype(str).str.strip() == sn]
        if row.empty:
            return None, f"No record found for Serial Number: {sn}"
    return row.iloc[0], None

def generate_server_title(dataframe, identifier, max_length=80):
    """
    Generate an optimized server title within eBay's character limit (default: 80 characters).
    Format: [Brand][Model][# of Bays][HDD Form Factor][Processor][RAM][RAID] Server [# of PSUs]
    Fields are removed in priority order to fit if too long.
    """

    row, error = lookup_row(dataframe, identifier)
    if error:
        return error

    # Required fields
    brand = get_field(row, 'MFGR')
    model = get_field(row, 'Item#')
    bays = get_field(row, '# of Bays')
    hdd_form_factor = get_field(row, 'HDD Form Factor')
    num_processors = get_field(row, '# of Processors')
    processor = get_field(row, 'Processor(s)')
    processor_info = f"{num_processors}x {processor}" if num_processors and processor else processor

    # Optional fields
    ram_breakdown = get_field(row, 'RAM Breakdown')
    ram_type = get_field(row, 'Type of RAM')
    ram = f"{ram_type} {ram_breakdown}".strip()
    raid = get_field(row, 'RAID Card')
    psus = get_field(row, '# of PSUs')
    psu_text = f"{psus}PSU" if psus and not psus.startswith("[") else ""

    # Build title in full form first
    parts = [
        brand, model, f"{bays}-Bay", hdd_form_factor, processor_info,
        ram, raid, "Server", psu_text
    ]

    title = ' '.join(part for part in parts if part and not part.isspace())
    original_title = title

    # Shorten title if it exceeds max_length
    remove_order = ['psu', 'raid', 'ram']
    components = {
        'psu': psu_text,
        'raid': raid,
        'ram': ram
    }

    while len(title) > max_length and remove_order:
        to_remove = remove_order.pop()
        part_value = components[to_remove]

        if part_value in title:
            title = title.replace(part_value, "").replace("  ", " ").strip()

    # Final cleanup
    cleaned_title = ' '.join(title.split())

    titles = f'Original title: {original_title}\nCleaned title: {cleaned_title}'

    return titles



def generate_switch_title(dataframe, identifier, max_length=80):
    """
    Generate an eBay-optimized switch title.
    Format: [Brand][Model][Ports][Speed] Switch [# of PSUs]
    Fields removed in order if too long: PSU, Speed, Ports
    """

    row, error = lookup_row(dataframe, identifier)
    if error:
        return error

    brand = get_field(row, 'MFGR')
    model = get_field(row, 'Item#')
    psus = get_field(row, '# of PSUs')
    psu_text = f"{psus}PSU" if psus and not psus.startswith("[") else ""
    ports = '[Ports]'
    speed = '[Speed]'

    # Full title initially
    parts = [brand, model, ports, speed, "Switch", psu_text]
    title = ' '.join(part for part in parts if part and not part.isspace())
    original_title = title

    # Shorten title if needed
    remove_order = ['psu', 'speed', 'ports']
    components = {
        'psu': psu_text,
        'speed': speed,
        'ports': ports
    }

    while len(title) > max_length and remove_order:
        to_remove = remove_order.pop()
        part_value = components[to_remove]
        if part_value in title:
            title = title.replace(part_value, "").replace("  ", " ").strip()

    cleaned_title = ' '.join(title.split())

    titles = f'Original title: {original_title}\nCleaned title: {cleaned_title}'

    return titles


# TODO: implement to file upload and searching by combining with format api

# Load data
server_df = clean_column_names(pd.read_excel('server report for automation.xlsx'))
switch_df = clean_column_names(pd.read_excel('switch report for automation.xlsx'))

# Test with PO-Line
print(generate_server_title(server_df, '9104-27'))
print()
print(generate_switch_title(switch_df, '9104-35'))
print()

# Test with Serial Number
print(generate_server_title(server_df, 'H5B5F33'))
print()
print(generate_switch_title(switch_df, 'FDO24350MAP'))
