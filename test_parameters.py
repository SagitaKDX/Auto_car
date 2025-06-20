#!/usr/bin/env python3
"""
Parameter Testing Script for Autonomous Car
This script helps you test and calibrate movement parameters
"""

from movement import CarController
import time

def test_single_movement():
    """Test basic car movements for calibration"""
    controller = CarController()
    
    try:
        controller.connect_serial()
        print("=== Single Movement Test ===")
        
        tests = [
            ("Forward", "mctl 70 70", 0.5),
            ("Backward", "mctl -70 -70", 0.5), 
            ("Turn Left", "mctl 0 70", 0.3),
            ("Turn Right", "mctl 70 0", 0.3),
        ]
        
        for name, command, duration in tests:
            input(f"Press Enter to test {name}...")
            print(f"Testing {name}: {command} for {duration}s")
            controller.send_command(command)
            time.sleep(duration)
            controller.send_command("mctl 0 0")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if controller.serial_conn:
            controller.serial_conn.close()
            print("Connection closed")

def test_parameter_combinations():
    """Test different parameter combinations for pathfinding"""
    test_configs = [
        {
            "name": "Conservative",
            "move_speed": 50,
            "move_duration": 0.6,
            "turn_speed": 50,
            "turn_duration": 0.4,
            "step_delay": 0.3
        },
        {
            "name": "Standard", 
            "move_speed": 70,
            "move_duration": 0.5,
            "turn_speed": 70,
            "turn_duration": 0.3,
            "step_delay": 0.2
        },
        {
            "name": "Fast",
            "move_speed": 85,
            "move_duration": 0.4,
            "turn_speed": 85, 
            "turn_duration": 0.25,
            "step_delay": 0.1
        }
    ]
    
    controller = CarController()
    
    try:
        print("=== Parameter Combination Test ===")
        controller.load_grid("floor2.csv")
        print("Grid loaded successfully")
        
        controller.connect_serial()
        print("Serial connection established")
        
        start_pos = (12, 17)
        end_pos = (13, 17)  # Just one step for testing
        
        for i, config in enumerate(test_configs):
            print(f"\n--- Test {i+1}: {config['name']} ---")
            print(f"Speed: {config['move_speed']}, Duration: {config['move_duration']}s")
            print(f"Turn Speed: {config['turn_speed']}, Turn Duration: {config['turn_duration']}s")
            print(f"Step Delay: {config['step_delay']}s")
            
            input("Press Enter to start this test...")
            
            success = controller.run_autonomous_test(
                start=start_pos,
                end=end_pos,
                move_speed=config["move_speed"],
                move_duration=config["move_duration"],
                turn_speed=config["turn_speed"],
                turn_duration=config["turn_duration"],
                step_delay=config["step_delay"]
            )
            
            result = "SUCCESS" if success else "FAILED"
            print(f"Test {config['name']}: {result}")
            
            if i < len(test_configs) - 1:
                input("Press Enter for next test...")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if controller.serial_conn:
            controller.serial_conn.close()
            print("Connection closed")

def test_custom_path():
    """Test a longer path with current parameters"""
    controller = CarController()
    
    try:
        print("=== Custom Path Test ===")
        controller.load_grid("floor2.csv")
        controller.connect_serial()
        
        # Define test path
        start_pos = (12, 17)
        end_pos = (15, 20)  # Longer path for real testing
        
        print(f"Testing path from {start_pos} to {end_pos}")
        
        # Use current parameters from movement.py
        success = controller.run_autonomous_test(
            start=start_pos,
            end=end_pos,
            move_speed=70,
            move_duration=0.5,
            turn_speed=70,
            turn_duration=0.3,
            step_delay=0.2
        )
        
        result = "SUCCESS" if success else "FAILED"
        print(f"Custom path test: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if controller.serial_conn:
            controller.serial_conn.close()

def quick_connectivity_test():
    """Quick test to verify serial connection"""
    controller = CarController()
    
    try:
        print("=== Connectivity Test ===")
        controller.connect_serial()
        print("✓ Serial connection established")
        
        # Send stop command
        controller.send_command("mctl 0 0")
        print("✓ Command sent successfully")
        
        print("✓ All connections working!")
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("Check:")
        print("- Car is connected via USB")
        print("- Serial port permissions")
        print("- Correct port (usually /dev/ttyUSB0)")
    finally:
        if controller.serial_conn:
            controller.serial_conn.close()

def main():
    """Main menu for parameter testing"""
    while True:
        print("\n" + "="*50)
        print("    AUTONOMOUS CAR PARAMETER TESTING")
        print("="*50)
        print("1. Quick connectivity test")
        print("2. Test single movements (calibration)")
        print("3. Test parameter combinations")
        print("4. Test custom path")
        print("5. Exit")
        print("-"*50)
        
        choice = input("Select test (1-5): ").strip()
        
        if choice == "1":
            quick_connectivity_test()
        elif choice == "2":
            test_single_movement()
        elif choice == "3":
            test_parameter_combinations()
        elif choice == "4":
            test_custom_path()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main() 