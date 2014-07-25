# Testing communication with the M-Blocks from a python script.
# Originally: James Bern 7/25

# Uses prSerial
# https://pypi.python.org/pypi/pyserial

import serial
import time

def output_to_terminal(serial_port):
    # FORNOW: wait a second for command to go through
    time.sleep(1)
    output = ''
    while serial_port.inWaiting() > 0:
        output += serial_port.read(1)
    print(output)

def execute_command(serial_port, string):
    serial_port.write(string + '\r')
    output_to_terminal(serial_port)

def main():
    ser = serial.Serial('COM5', 115200, timeout=1)
    print("\nCommunicating on {}\n".format(ser.portstr))

    execute_command(ser, "atd")
    execute_command(ser, "charge info")
    for _ in xrange(3):
        execute_command(ser, "brake f 4000 250")
    execute_command(ser, "blediscon")

    ser.close()

if __name__ == '__main__':
    main()

