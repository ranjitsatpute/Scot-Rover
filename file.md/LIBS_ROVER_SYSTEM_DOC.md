# LIBS Rover Project: Comprehensive Technical Documentation

## 1. Project Vision
The **Laser-Induced Breakdown Spectroscopy (LIBS) Rover** is a complete ROS 2 ecosystem designed to simulate planetary exploration and mineral analysis. It bridges high-level software orchestration with low-level sensor simulation, providing a realistic platform for testing automated chemical analysis.

---

## 2. Full System Architecture & File Structure

### Project Layout (as shown in Workspace)
```text
o:/CODE PLAYGROUND/DEMO_LIBS/test/libs_rover_ws/
├── Dockerfile                  # Defines the ROS 2 Humble environment
├── docker-compose.yml          # Orchestrates the container services
├── entrypoint.sh               # Environment sourcing script
├── LIBS_ROVER_SYSTEM_DOC.md    # [This File] Full technical specs
├── output/                     # Generated data (Plots, logs, JSON)
│   └── spectrum_basalt_...png  # Visualization of mineral readings
└── src/
    └── libs_rover/             # Main ROS 2 Package (libs_rover_pkg)
        ├── CMakeLists.txt      # Build instructions (C++)
        ├── package.xml         # Package metadata & dependencies
        ├── config/
        │   └── spectral_database.yaml # Mineral signatures (Fe, Si, Mg, etc.)
        ├── launch/             # ROS 2 Launch files
        │   └── libs_demo.launch.py # Starts simulator, analyzer, and controller
        ├── msg/                # Custom Interface Definitions
        │   ├── SpectrumData.msg
        │   ├── ElementResult.msg
        │   └── AnalysisResult.msg
        ├── srv/
        │   └── TriggerMeasurement.srv # Trigger service definition
        └── libs_rover/         # Python Node Implementations
            ├── libs_sensor_simulator_node.py
            ├── measurement_controller_node.py
            ├── spectrum_analyzer_node.py
            ├── backend_monitor_node.py
            ├── __init__.py
            └── utils/
                ├── spectrum_generator.py # Logic for synthetic data
                └── __init__.py
```

---

## 3. Node-by-Node Implementation Details

### A. LIBS Sensor Simulator (`libs_sensor_simulator_node`)
- **Type**: Hardware Layer Simulation.
- **Service Server**: Offers `/libs/trigger_measurement`.
- **Publisher**: Sends data to `/libs/spectrum` using `SpectrumData.msg`.
- **Logic**:
    1. Loads `spectral_database.yaml` upon startup.
    2. Listens for parameters (e.g., `noise_level`).
    3. When triggered, it uses `SpectrumGenerator` to create a noisy NumPy array of wavelengths and intensities.
    4. **Output**: Automatically saves a `.png` plot to the `output/` directory for visual confirmation.

### B. Measurement Controller (`measurement_controller_node`)
- **Type**: Mission Control / Safety Layer.
- **Logic**:
    - Acts as a gatekeeper.
    - Validates `laser_power_percent`. If power > 100%, it blocks the command for safety.
    - If safe, it forwards the request to the sensor node.

### C. Spectrum Analyzer (`spectrum_analyzer_node`)
- **Type**: Data Processing Layer.
- **Subscriber**: Listens to `/libs/spectrum`.
- **Publisher**: Sends findings to `/libs/analysis_results`.
- **Logic**:
    - Receives raw intensity data.
    - Runs **Peak Detection** algorithm (SciPy).
    - Compares detected peaks against known elements (Iron, Silicon, etc.) in the database.
    - Calculates confidence scores for each detected element.

### D. Backend Monitor (`backend_monitor_node`)
- **Type**: Observability.
- **Logic**:
    - Aggregates logs and status messages.
    - Provides a terminal-based UI to track every "Laser Fire" event and its success rate.

---

## 4. Key ROS 2 Concepts Applied

### A. Launch Files
The file `libs_demo.launch.py` is the **"Start Button"** for the whole system. Instead of running 4 separate commands in 4 terminals, you run one launch file.
- It also injects settings, like telling the simulator node exactly where to find the `spectral_database.yaml`.

### B. Quality of Service (QoS)
| Topic | QoS Profile | Rationale |
| :--- | :--- | :--- |
| `/libs/spectrum` | **RELIABLE** | We cannot afford to lose scientific data during transmission. |
| `/diagnostics` | **BEST EFFORT** | High-frequency telemetry where the latest data is better than old re-sent data. |

### C. TF2 & Coordinate Frames
- **`libs_sensor_link`**: The data's origin. Every spectrum message is tagged with this frame.
- **Transform Tree**: Allows the system to map a "found mineral" to a 3D location on the Mars map by calculating the offset between the sensor and the rover's wheels.

### D. Parameter System
The node behavior can be changed without rebooting:
- `ros2 param set /libs_sensor_simulator noise_level 0.5`
- This immediately updates the internal `self.noise_level` variable in the Python class.

---

## 5. Custom Interfaces (The "Language")

### `SpectrumData.msg`
Used for transmitting high-density raw data.
- `std_msgs/Header header`: Timestamp and `frame_id`.
- `float64[] wavelengths`: X-axis (nm).
- `float64[] intensities`: Y-axis (Energy).

### `TriggerMeasurement.srv`
The "Command" link.
- **Request**: `string sample_type`, `float64 laser_power_percent`.
- **Response**: `bool success`, `string message`, `SpectrumData spectrum`.

---

## 6. Development & Deployment (Docker)

The project is built on **ROS 2 Humble** and synchronized via Docker:
- **Build**: `colcon build --symlink-install` allows code changes inside the container to reflect immediately.
- **Persistent Storage**: The `output/` directory is often mounted so that plots saved inside the container appear in your Windows folder instantly.

---

## 7. How to Operate (PowerShell / Windows)

Due to PowerShell's unique treatment of quotes and braces, we use the **Stop-Parsing Operator (`--%`)**:

```powershell
docker --% exec -it libs_rover_ros2 bash -c "ros2 service call /libs/trigger_measurement libs_rover_pkg/srv/TriggerMeasurement \"{sample_type: 'basalt', laser_power_percent: 100.0}\""
```
