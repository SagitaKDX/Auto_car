import serial
import serial.tools.list_ports
import pygame
import time
from typing import Optional

class CarController:
    """
    Car controller class for handling physical movement commands.
    Contains movement functions for up, down, left, right directions.
    """
    
    def __init__(self):
        self.serial_conn = None
        self.joystick = None
    
    def list_serial_ports(self):
        """List all available serial ports for car connection."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_serial(self):
        """
        Connect to car via serial communication.
        Prefers /dev/ttyUSB0, falls back to first available port.
        """
        available_ports = self.list_serial_ports()
        port = '/dev/ttyUSB0' if '/dev/ttyUSB0' in available_ports else (available_ports[0] if available_ports else None)
        if not port:
            raise Exception("No serial ports found.")
        self.serial_conn = serial.Serial(port, baudrate=115200, timeout=1)
        return self.serial_conn

    def init_joystick(self):
        """
        Initialize pygame joystick for manual control.
        Connects to the first available controller.
        """
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise Exception("No controller found.")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        return self.joystick

    def get_axes(self):
        """Get current joystick axis values."""
        pygame.event.pump()
        return [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]

    def generate_mctl_command(self, x: int, y: int, rx: int, rt: float) -> str:
        """
        Generate movement control command from joystick inputs.
        Converts joystick values to car movement commands.
        
        Args:
            x: Left stick horizontal (-100 to 100)
            y: Left stick vertical (-100 to 100)
            rx: Right stick horizontal (-100 to 100)
            rt: Right trigger (0 to 1)
        """
        MIN = 50
        MAX = 100
        val = MAX if rt > 0.5 else MIN

        if abs(x) < 20 and abs(y) < 20 and abs(rx) < 20:
            return "mctl 0 0"

        if abs(rx) > 20 and abs(x) < 20 and abs(y) < 20:
            if rx > 20:
                return f"mctl {val} 0"
            elif rx < -20:
                return f"mctl 0 {val}"

        if y < -20:
            return f"mctl {val} {val}"
        elif y > 20:
            return f"mctl {-val} {-val}"

        return "mctl 0 0"

    def send_command(self, command: str):
        """
        Send command to car via serial connection.
        Prints the command for debugging.
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{command}\n".encode())
            print(f"Sent: {command}")

    def move_up(self, speed: int = 70, duration: float = 0.5):
        """
        Move car forward/up.
        
        Args:
            speed: Movement speed (0-100)
            duration: Movement duration in seconds
        """
        # TODO: Implement forward movement
        pass

    def move_down(self, speed: int = 70, duration: float = 0.5):
        """
        Move car backward/down.
        
        Args:
            speed: Movement speed (0-100)
            duration: Movement duration in seconds
        """
        # TODO: Implement backward movement
        pass

    def move_left(self, speed: int = 70, duration: float = 0.3):
        """
        Turn car left.
        
        Args:
            speed: Turn speed (0-100)
            duration: Turn duration in seconds
        """
        # TODO: Implement left turn
        pass

    def move_right(self, speed: int = 70, duration: float = 0.3):
        """
        Turn car right.
        
        Args:
            speed: Turn speed (0-100)
            duration: Turn duration in seconds
        """
        # TODO: Implement right turn
        pass

    def stop(self):
        """
        Stop the car immediately.
        """
        # TODO: Implement stop command
        pass

    def close_connection(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close() 