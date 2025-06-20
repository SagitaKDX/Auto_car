# Quick Setup Guide - File Transfer & Parameter Modification

## 📁 File Transfer to Raspberry Pi

### Method 1: Transfer Single File (floor2.csv)
```bash
# Replace <PI_IP> with your Raspberry Pi's IP address
scp floor2.csv pi@<PI_IP>:/home/pi/Documents/Test/Autocar/Auto_car/

# Example with actual IP:
scp floor2.csv pi@192.168.1.100:/home/pi/Documents/Test/Autocar/Auto_car/
```

### Method 2: Transfer All Project Files
```bash
# Transfer entire project directory
scp -r * pi@<PI_IP>:/home/pi/Documents/Test/Autocar/Auto_car/

# Or transfer specific files
scp movement.py example_usage.py floor2.csv pi@<PI_IP>:/home/pi/Documents/Test/Autocar/Auto_car/
```

### Method 3: Using rsync (Recommended for large files)
```bash
# Sync files efficiently
rsync -av floor2.csv pi@<PI_IP>:/home/pi/Documents/Test/Autocar/Auto_car/

# Sync entire directory
rsync -av ./ pi@<PI_IP>:/home/pi/Documents/Test/Autocar/Auto_car/
```

### Find Your Raspberry Pi IP Address
```bash
# On Raspberry Pi, run:
hostname -I

# Or check from your router's admin panel
# Or use network scanner: nmap -sn 192.168.1.0/24
```

---

## ⚙️ Modifying Constant Values

### 1. Edit Test Parameters in movement.py

Open `movement.py` and find the `run_fixed_scenario()` function (around line 520):

```python
def run_fixed_scenario():
    # ===== MODIFY THESE CONSTANTS =====
    
    # Grid and Position Settings
    GRID_FILE = "floor2.csv"          # Path to your map file
    START_POS = (12, 17)              # Starting position (row, col)
    END_POS = (18, 17)                # Target position (row, col)
    
    # Movement Speed Settings (0-100)
    MOVE_SPEED = 70                   # Forward/backward speed
    TURN_SPEED = 70                   # Left/right turn speed
    
    # Timing Settings (seconds)
    MOVE_DURATION = 0.5               # How long to move forward/back
    TURN_DURATION = 0.3               # How long to turn left/right
    STEP_DELAY = 0.2                  # Pause between each step
```

### 2. Quick Parameter Reference

| Parameter | Typical Range | Description |
|-----------|---------------|-------------|
| `MOVE_SPEED` | 30-100 | Motor speed for forward/backward |
| `TURN_SPEED` | 30-100 | Motor speed for turning |
| `MOVE_DURATION` | 0.3-0.8s | Time to move one grid cell |
| `TURN_DURATION` | 0.2-0.5s | Time for 90-degree turn |
| `STEP_DELAY` | 0.1-0.5s | Pause between movements |

### 3. Position Settings

```python
# Grid coordinates (row, col) - zero-indexed
START_POS = (12, 17)    # Row 12, Column 17
END_POS = (18, 17)      # Row 18, Column 17

# Make sure positions are:
# - Not on walls (value = 0 in CSV)
# - Within grid bounds
# - Reachable path exists
```

### 4. Common Modifications for Testing

#### Slow and Careful (For initial testing):
```python
MOVE_SPEED = 50
TURN_SPEED = 50
MOVE_DURATION = 0.6
TURN_DURATION = 0.4
STEP_DELAY = 0.3
```

#### Fast Movement (After calibration):
```python
MOVE_SPEED = 85
TURN_SPEED = 85
MOVE_DURATION = 0.4
TURN_DURATION = 0.25
STEP_DELAY = 0.1
```

#### Test Adjacent Cells (Short distance):
```python
START_POS = (12, 17)
END_POS = (12, 18)      # Just one cell to the right
```

#### Test Longer Path:
```python
START_POS = (12, 17)
END_POS = (18, 20)      # Multiple turns required
```

---

## 🔧 Quick Edit Commands

### Edit on Raspberry Pi via SSH:
```bash
# SSH into Pi
ssh pi@<PI_IP>

# Navigate to project
cd /home/pi/Documents/Test/Autocar/Auto_car/

# Edit with nano
nano movement.py

# Or edit with vim
vim movement.py
```

### Edit Locally and Transfer:
```bash
# Edit movement.py on your computer
# Then transfer the updated file:
scp movement.py pi@<PI_IP>:/home/pi/Documents/Test/Autocar/Auto_car/
```

---

## 🚀 Test Your Changes

### 1. Quick Test:
```bash
# On Raspberry Pi:
cd /home/pi/Documents/Test/Autocar/Auto_car/
python3 movement.py
# Select option 4
```

### 2. Parameter Testing:
```bash
# Use the testing script:
python3 test_parameters.py
# Select option 1 for connectivity test
# Select option 2 for movement calibration
```

---

## 📝 Example Complete Workflow

1. **Transfer file:**
   ```bash
   scp floor2.csv pi@192.168.1.100:/home/pi/Documents/Test/Autocar/Auto_car/
   ```

2. **SSH and edit:**
   ```bash
   ssh pi@192.168.1.100
   cd /home/pi/Documents/Test/Autocar/Auto_car/
   nano movement.py
   ```

3. **Modify these lines in the file:**
   ```python
   MOVE_SPEED = 60        # Change from 70 to 60
   MOVE_DURATION = 0.6    # Change from 0.5 to 0.6
   START_POS = (10, 15)   # Change start position
   END_POS = (12, 15)     # Change end position
   ```

4. **Save and test:**
   ```bash
   # Save with Ctrl+X, Y, Enter
   python3 movement.py
   # Select option 4
   ```

That's it! Your car will now use the new parameters. 