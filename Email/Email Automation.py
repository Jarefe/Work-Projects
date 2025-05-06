import win32com.client, re, sys, os, pyperclip, xlwings as xw
from dotenv import load_dotenv


def check_files(excel_path: str, pdf_path: str):
    """Check if the Excel and PDF files exist"""
    excel_exists = os.path.isfile(excel_path)
    pdf_exists = os.path.isfile(pdf_path)

    if excel_exists:
        print(f"Excel file found: {excel_path}")
    else:
        print(f"Excel file not found: {excel_path}")

    if pdf_exists:
        print(f"PDF file found: {pdf_path}")
    else:
        print(f"PDF file not found: {pdf_path}")

    return excel_exists and pdf_exists


def extract_data(data: str):
    """Extract PO, batch number, and device type from user input"""
    pattern = r'(\d{4})-(\d)\s*(Laptop|Desktop|AIO|Mini)'

    match = re.match(pattern, data, re.IGNORECASE)
    if match:
        PO = match.group(1)
        batch = match.group(2)
        device_type = match.group(3).capitalize() + 's'
        return PO, batch, device_type

    print(f"Invalid identifier: {data}")
    return None, None, None


def read_excel(excel_path: str):
    """Read data from Excel file"""
    excel_path = os.path.abspath(excel_path)  # Ensure full path for comparison
    app = xw.App(visible=False)  # Create Excel app (hidden)
    workbook = None
    opened_here = False

    try:
        # Check if workbook is already open
        for wb in app.books:
            if wb.fullname.lower() == excel_path.lower():
                workbook = wb
                break

        # If not open, open it ourselves
        if workbook is None:
            workbook = app.books.open(excel_path, read_only=True)
            opened_here = True

        sheet = workbook.sheets[0]  # Use active sheet

        # Read specific cells
        devices_passed = sheet.range('F10').value
        devices_failed = sheet.range('F12').value
        devices_no_drives = sheet.range('G10').value

        # Read serial numbers from G12 downward
        serial_numbers = []
        row = 12
        while True:
            value = sheet.range(f'G{row}').value
            if value is None:
                break
            serial_numbers.append(value)
            row += 1

        return int(devices_passed), int(devices_failed), int(devices_no_drives), serial_numbers

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None, None, None, []

    finally:
        if opened_here and workbook is not None:
            workbook.close()
        app.quit()


def serial_number_exists(serial_numbers: list[str]):
    """Check if serial numbers exist; if so, return as HTML content for email"""
    if not serial_numbers:
        return 'N/A', []
    else:
        # Create serial numbers HTML content (print them vertically)
        serial_numbers_html = ''
        for serial in serial_numbers:
            # Check if the serial number is purely numeric (can be a float that represents an integer)
            if isinstance(serial, float):
                if serial.is_integer():  # If it's a float like 123.0, treat it as an integer
                    serial = str(int(serial))  # Convert to int, then to string
            elif serial.isdigit():  # If it's a string that contains only digits, treat it as a number
                serial = str(int(serial))  # Convert to int, then to string

            # Add serial number to HTML content
            serial_numbers_html += f'<span>{serial}</span><br>'

        return 'Already Added', serial_numbers_html


def generate_email(num_passed: int, num_failed: int, num_no_drives: int, added: str, serial_numbers_html: str):
    """Generate an email with the results of batch erasure"""
    num_devices = num_passed + num_failed + num_no_drives
    ol = win32com.client.Dispatch('Outlook.Application')
    email = ol.CreateItem(0)
    email.subject = f'{PO} ER Batch #{batch_number} for {num_devices} {device}'

    email.Attachments.Add(ATTACHMENT)

    body = f'''
    <html>
      <body>
        <p></p>
        <span>{num_no_drives} | <font color='blue'>No Drives</font></span><br>
        <span>{num_failed} | <font color='red'>Failed</font></span><br>
        <br>
        <span>PDR | {added}</span><br> 
        {serial_numbers_html.strip()}
      </body>
    </html>
    '''

    email.HTMLBody = body

    email.to = os.getenv('RECIPIENT')

    email.display()


def copy_serial_numbers(serial_numbers: list[str]):
    """Copy serial numbers to clipboard for pasting into PDR"""

    if not serial_numbers:
        return
    # Ensure each serial number is in string format, and handle numbers with possible .0
    serial_numbers = [
        str(int(serial)) if isinstance(serial, float) and serial.is_integer() else str(serial)
        for serial in serial_numbers
    ]

    # Join the serial numbers with newlines and copy to clipboard
    pyperclip.copy('\n'.join(serial_numbers))
    print('Serial numbers copied to clipboard. Paste into PDR.')


user_input = input('Enter PO-batch and device type: ')

PO, batch_number, device = extract_data(user_input)

load_dotenv()

excel_path = os.getenv('EXCEL_FILEPATH')
pdf_path = os.getenv('PDF_FILEPATH')

TRACKING_FILES = f'{excel_path}{PO}-{batch_number}.xlsx'
ATTACHMENT = f'{pdf_path}Erasure Report for PO# {PO}-{batch_number}.pdf'

if not check_files(TRACKING_FILES, ATTACHMENT):
    print('Files not found. Terminating program.')
    sys.exit(1)

# Read in data from personalized excel template
passed, failed, no_drives, SNs = read_excel(TRACKING_FILES)
added, serial_numbers_html = serial_number_exists(SNs)

generate_email(passed, failed, no_drives, added, serial_numbers_html)
copy_serial_numbers(SNs)
