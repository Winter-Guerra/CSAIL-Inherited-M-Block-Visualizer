# Testing communication with the M-Blocks from a python script.
# Originally: James Bern 7/25

# Uses prSerial
# https://pypi.python.org/pypi/pyserial


import serial
import time


PORT_NAME = 'COM5'
BAUD_RATE = 115200
TIMEOUT = 1 # FORNOW: number of seconds to wait on output


def output_to_terminal(serial_port):
    '''
    Output everying in the receive buffer to terminal.
    Should wait for the conclusion of the action.
    '''
    output = ''
    # # FORNOW: wait a few seconds for command to go through
    time.sleep(4)
    while serial_port.inWaiting() > 0:
        output += serial_port.read(1)
    print(output)


def execute_command(serial_port, string_rep):
    '''
    Send a command to the specified serial_port.
    example: execute_command(ser, "atd")
    '''
    serial_port.write(string_rep + '\r')
    output_to_terminal(serial_port)


def main():
    # Open up the serial port
    try:
        ser = serial.Serial(PORT_NAME, BAUD_RATE, timeout=TIMEOUT)
    except serial.serialutil.SerialException:
        print("\nYou probably specified the wrong port.\n" +
                "Try something like 'COM5'.\nTerminating.\n")
        exit(1)
    print("\nOpened port with name {}\n".format(ser.portstr))

    # Connect to M-Block
    execute_command(ser, "atd")

    # Test sequence
    execute_command(ser, "charge info")

    # for _ in xrange(3):
        # execute_command(ser, "brake f 4000 250")
    # execute_command(ser, "ia f 4000 4000 250")
    # execute_command(ser, "ia r 4000 4000 250")
    # execute_command(ser, "ia r 4000 4000 250")
    # execute_command(ser, "ia f 4000 4000 250")

    # Disconnect from M-Block
    execute_command(ser, "blediscon")

    # Close serial port
    ser.close()


if __name__ == '__main__': main()

