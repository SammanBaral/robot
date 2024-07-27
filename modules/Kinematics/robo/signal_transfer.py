# Function to send motor commands
def send_wheel_command(arduino, move1, move2):
    command = f"MOVE {move1} {move2}\n"
    print(f"Sending command: {command.strip()}")
    arduino.write(command.encode())  # Send the command to the Arduino
