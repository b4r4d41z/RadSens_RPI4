import smbus
import time
import matplotlib.pyplot as plt
from threading import Thread

class CG_RadSens:
    RS_DEFAULT_I2C_ADDRESS = 0x66

    def __init__(self, address=RS_DEFAULT_I2C_ADDRESS):
        self.address = address
        self.bus = smbus.SMBus(1)  # Initialize SMBus for device communication

    def init(self):
        try:
            chip_id = self.get_chip_id()  # Retrieve sensor chip ID
            return chip_id == 0x7D  # Check if chip ID is correct
        except:
            return False  # Handle initialization errors

    def get_chip_id(self):
        return self.bus.read_byte_data(self.address, 0x00)  # Read chip ID

    def get_firmware_version(self):
        return self.bus.read_byte_data(self.address, 0x01)  # Read firmware version

    def get_sensitivity(self):
        high_byte = self.bus.read_byte_data(self.address, 0x12)  # Read sensitivity (high byte)
        low_byte = self.bus.read_byte_data(self.address, 0x13)  # Read sensitivity (low byte)
        return (high_byte << 8) + low_byte  # Combine high and low bytes

    def set_sensitivity(self, sensitivity):
        high_byte = (sensitivity >> 8) & 0xFF  # Split sensitivity into high and low bytes
        low_byte = sensitivity & 0xFF
        self.bus.write_byte_data(self.address, 0x12, high_byte)  # Write high byte of sensitivity
        self.bus.write_byte_data(self.address, 0x13, low_byte)  # Write low byte of sensitivity

    def get_hv_generator_state(self):
        return self.bus.read_byte_data(self.address, 0x11) == 1  # Get high-voltage generator state

    def set_hv_generator_state(self, state):
        self.bus.write_byte_data(self.address, 0x11, 1 if state else 0)  # Set high-voltage generator state

    def get_led_state(self):
        return self.bus.read_byte_data(self.address, 0x10) == 1  # Get LED indicator state

    def set_led_state(self, state):
        self.bus.write_byte_data(self.address, 0x10, 1 if state else 0)  # Set LED indicator state

    def get_rad_intensy_dynamic(self):
        high_byte = self.bus.read_byte_data(self.address, 0x03)  # Read dynamic radiation intensity (high byte)
        low_byte = self.bus.read_byte_data(self.address, 0x04)  # Read dynamic radiation intensity (low byte)
        return (high_byte << 8) + low_byte  # Combine high and low bytes

    def get_rad_intensy_static(self):
        high_byte = self.bus.read_byte_data(self.address, 0x06)  # Read static radiation intensity (high byte)
        low_byte = self.bus.read_byte_data(self.address, 0x07)  # Read static radiation intensity (low byte)
        return (high_byte << 8) + low_byte  # Combine high and low bytes

    def get_number_of_pulses(self):
        high_byte = self.bus.read_byte_data(self.address, 0x09)  # Read number of pulses (high byte)
        low_byte = self.bus.read_byte_data(self.address, 0x0A)  # Read number of pulses (low byte)
        return (high_byte << 8) + low_byte  # Combine high and low bytes


def calculate_radiation_activity(N, Pcp, dT):
    return (N * 60 * 60) / (Pcp * dT)  # Calculate radiation activity


def plot_data(data):
    plt.clf()  # Clear the current plot
    plt.plot(data, color='red')  # Plot the data with specified line color
    plt.xlabel('Time (s)')  # Set X-axis label
    plt.ylabel('Radiation Activity (µR/h)')  # Set Y-axis label
    plt.title('Radiation Activity Over Time')  # Set plot title
    plt.grid(True)  # Enable grid on the plot
    plt.pause(0.01)  # Pause briefly to update the plot


def update_data(radSens, rad_activity_data):
    while True:
        num_pulses = radSens.get_number_of_pulses()  # Get the number of pulses
        Pcp = radSens.get_sensitivity()  # Get current sensitivity
        dT = 1  # Registration time interval in seconds
        rad_activity = calculate_radiation_activity(num_pulses, Pcp, dT)  # Calculate radiation activity

        # Print dynamic/static intensity, pulse count, and radiation activity
        print(f"Rad intensity dynamic: {radSens.get_rad_intensy_dynamic()} μR/h")
        print(f"Rad intensity static: {radSens.get_rad_intensy_static()} μR/h")
        print(f"Number of pulses: {num_pulses}")
        print(f"Radiation activity: {rad_activity} μR/h")

        rad_activity_data.append(rad_activity)  # Add radiation activity to data list
        time.sleep(0.25)  # Wait 0.25 seconds for data collection


def main():
    radSens = CG_RadSens()  # Create radiation sensor instance
    time.sleep(0)  # Short pause for initialization

    if not radSens.init():
        print("Sensor wiring error!")  # Print message if sensor wiring error occurs
        return

    sensor_chip_id = radSens.get_chip_id()  # Get sensor chip ID
    print(f"Chip id: 0x{sensor_chip_id:X}")  # Display chip ID in hexadecimal format

    firmware_ver = radSens.get_firmware_version()  # Get sensor firmware version
    print(f"Firmware version: {firmware_ver}")  # Display firmware version

    # Sensitivity control example
    print("-------------------------------------")
    print("Set Sensitivity example:\n")
    sensitivity = radSens.get_sensitivity()  # Get current sensitivity
    print(f"\t getSensitivity(): {sensitivity}")

    print("\t setSensitivity(55)... ")
    radSens.set_sensitivity(55)  # Set sensitivity to 55
    print(f"\t getSensitivity(): {radSens.get_sensitivity()}")

    print("\t setSensitivity(105)... ")
    radSens.set_sensitivity(105)  # Set sensitivity to 105
    print(f"\t getSensitivity(): {radSens.get_sensitivity()}")
    print("-------------------------------------")

    # High-voltage generator control example
    print("HW generator example:\n")
    hv_generator_state = radSens.get_hv_generator_state()  # Get high-voltage generator state
    print(f"\n\t HV generator state: {hv_generator_state}")

    print("\t setHVGeneratorState(false)... ")
    radSens.set_hv_generator_state(False)  # Turn off high-voltage generator
    print(f"\t HV generator state: {radSens.get_hv_generator_state()}")

    print("\t setHVGeneratorState(true)... ")
    radSens.set_hv_generator_state(True)  # Turn on high-voltage generator
    print(f"\t HV generator state: {radSens.get_hv_generator_state()}")
    print("-------------------------------------")

    # LED indicator control example
    print("LED indication control example:\n")
    led_state = radSens.get_led_state()  # Get LED indicator state
    print(f"\n\t LED indication state: {led_state}")

    print("\t turn off LED indication... ")
    radSens.set_led_state(False)  # Turn off LED indicator
    print(f"\t LED indication state: {radSens.get_led_state()}")

    print("\t turn on LED indication... ")
    radSens.set_led_state(True)  # Turn on LED indicator
    print(f"\t LED indication state: {radSens.get_led_state()}")
    print("\n-------------------------------------")

    rad_activity_data = []

    # Create a separate thread for data updating
    data_thread = Thread(target=update_data, args=(radSens, rad_activity_data))
    data_thread.daemon = True  # Set thread as daemon for automatic exit with the main thread
    data_thread.start()  # Start data collection thread

    # Start a separate thread for plotting data
    plotter_thread = Thread(target=plot_data_thread, args=(rad_activity_data,))
    plotter_thread.start()

    while True:  # Main thread continues with other tasks
        time.sleep(1)  # Pause for the main program


def plot_data_thread(data):
    plt.ion()  # Enable interactive mode for matplotlib
    while True:
        plot_data(data)  # Call function to plot data


if __name__ == "__main__":
    main()
