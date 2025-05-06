import serial, threading, time, os, re
import serial.tools.list_ports

# Common baud rates to try
BAUD_RATES = [9600, 19200, 38400, 57600, 115200]

# Serial timeout
TIMEOUT = 1

# Delays to give the switch time to respond
COMMAND_DELAY = 0.5
READ_DELAY = 0.5

# Output log filepaths; change accordingly
OUTPUT_DIR = 'Test'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Commands to run on each switch (CISCO ONLY)
CISCO_COMMANDS = [
    'sh inv', 'wr er', 'sh ver', 'sh env',
    'sh lice', 'sh lice default', 'sh lice status',
    'sh lice detail', 'sh lice feature', 'sh lice summary',
    'sh inv', 'sh inv', 'exit'
]


def create_folder(folder_name):
    """Make a new folder if it doesn't already exist."""
    # TODO: edit to handle creating PO folder in usual log location
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f'Created folder: {folder_name}')
    else:
        print(f'Folder already exists: {folder_name}')


def discover_serial_ports(ports_in_use=None):
    """List all connected COM ports or return only the ones specified by the user."""
    if ports_in_use is not None:
        cleaned_ports = []
        for item in ports_in_use.split(','):
            item = item.strip().upper()  # Normalize case
            if item.startswith('COM'):
                cleaned_ports.append(item)
            elif item.isdigit():  # Allow just '1' as shorthand for COM1
                cleaned_ports.append(f'COM{item}')
        print(f'Using user-specified ports: {cleaned_ports}')
        return cleaned_ports

    ports = [port.device for port in serial.tools.list_ports.comports()]
    print(f'Found COM ports: {ports}')
    return ports


def sanitize_filename(name):
    """Prevent illegal characters in filenames."""
    return name.replace('/', '_').replace(':', '_')


def parse_inventory(output):
    """Try to pull serial number and model from 'sh inv' output."""
    serial_number = model = 'Unknown'
    for line in output.splitlines():
        if 'SN:' in line or 'Serial Number' in line:
            match = re.search(r'SN:\s*(\S+)', line) or re.search(r'Serial Number.*?:\s*(\S+)', line)
            if match:
                serial_number = match.group(1)
        if 'Model number' in line or 'NAME:' in line:
            match = re.search(r'Model number\s*:\s*(\S+)', line)
            if match:
                model = match.group(1)
    return serial_number, model


def test_baud_rate(port):
    """Try different baud rates until the switch responds to 'sh inv'."""
    for baud in BAUD_RATES:
        try:
            with serial.Serial(port, baudrate=baud, timeout=TIMEOUT) as ser:
                ser.write(b'sh inv\r\n')
                time.sleep(READ_DELAY)
                response = ser.read(ser.in_waiting or 1024).decode(errors='ignore')

                if any(key in response for key in ['NAME:', 'PID:', 'SN:']):
                    print(f'{port} responded at {baud} baud.')
                    return baud
        except:
            pass
    print(f'No valid baud rate found on {port}.')
    return None


def process_switch(port):
    """Connect to a switch, run commands, and save output."""
    baud = test_baud_rate(port)
    if not baud:
        print(f'Skipping {port} — can’t get a response.')
        return

    commands = select_commands(CISCO_COMMANDS)

    if not commands:
        print('Invalid command selection. Exiting program.')

    try:
        with serial.Serial(port, baudrate=baud, timeout=TIMEOUT) as ser:
            # Run 'sh inv' to grab model info
            ser.write(b'sh inv\r\n')
            time.sleep(COMMAND_DELAY + READ_DELAY)
            response = ser.read(ser.in_waiting or 1024).decode(errors='ignore')

            # Try to get model and serial from output
            serial_num, model = parse_inventory(response)
            model_name = sanitize_filename(model if model != 'Unknown' else port)

            # Use model name and timestamp for filenames
            log_path = os.path.join(OUTPUT_DIR, f'{model_name}.txt')
            info_path = os.path.join(OUTPUT_DIR, f'info_{model_name}.txt')

            with open(log_path, 'w') as log_file, open(info_path, 'w') as info_file:
                log_file.write(f'## sh inv\n{response}')
                info_file.write(f'Serial Number: {serial_num}\nModel: {model}\n')
                print(f'[{port}] Serial: {serial_num}, Model: {model}')

                # Run the list of commands
                for cmd in commands:
                    ser.write((cmd + '\r\n').encode())
                    time.sleep(COMMAND_DELAY + READ_DELAY)
                    response = ser.read(ser.in_waiting or 1024).decode(errors='ignore')
                    log_file.write(f'\n\n## {cmd}\n{response}')
                    log_file.flush()

            print(f'Done with {port} at {baud} baud.')

    except Exception as e:
        print(f'Error talking to {port} at {baud} baud: {e}')


def select_commands(choice):
    """Prompt the user to select commands to run."""

    if choice == 'cisco':
        return CISCO_COMMANDS

    return None


def main():
    print('Make sure you’ve cleared the password and are at the switch prompt (e.g. "Switch#") before continuing.')

    folder_name = input('Enter the PO or folder name to save logs: ')
    if not folder_name:
        print('Folder name is required. Exiting program.')
        return
    create_folder(folder_name)

    # Get ports in use from user or default to checking every possible port
    ports = discover_serial_ports(input('Enter any ports already in use (comma-separated): '))
    valid_ports = []

    for port in ports:
        if test_baud_rate(port):
            valid_ports.append(port)
        else:
            print(f'Ignoring {port} — no valid response.')

    if not valid_ports:
        print('No responsive switches found.')
        return

    threads = []
    # Start a process for each valid switch
    for port in valid_ports:
        t = threading.Thread(target=process_switch, args=(port,))
        t.start()
        threads.append(t)

    # Wait until all processes are done
    for t in threads:
        t.join()

    print('Done.')


if __name__ == '__main__':
    main()
