# Technical Deep-Dive: LIBS Sensor ROS 2 Integration

This document provides a comprehensive breakdown of the implementation logic, physical modelling, and software engineering decisions made during the development of the LIBS Rover Prototype.

---

## 1. Physical Simulation Logic (The Digital Twin)

To build a meaningful prototype without hardware, we implemented a **stochastic spectrum generator** in `spectrum_generator.py`. 

### Signal Composition
A simulated spectrum $S(\lambda)$ is modeled as the sum of three distinct components:

$$S(\lambda) = B(\lambda) + \sum P_i(\lambda) + N(\lambda)$$

1.  **Baseline ($B$):** A low-frequency polynomial curve representing background Bremsstrahlung radiation (common in hot plasmas).
2.  **Characteristic Peaks ($P$):** For each element in a sample, we retrieve its "Emission Lines" from `spectral_database.yaml`. Each line is modeled as a **Gaussian Distribution**:
    $$G(\lambda) = A \cdot \exp\left(-\frac{(\lambda - \mu)^2}{2\sigma^2}\right)$$
    where $\mu$ is the target wavelength and $\sigma$ is the instrument's spectral resolution.
3.  **Additive Noise ($N$):** White Gaussian Noise is added to simulate sensor shot noise and electronic interference.

### The Advantage
This allows the **Spectrum Analyzer** to be tested against a variety of signal-to-noise ratios (SNR). By decreasing the "Laser Power" in the simulator, we can observe the Analyzer's confidence score drop, simulating real-world degradation.

---

## 2. Advanced Signal Processing in `spectrum_analyzer_node.py`

The analyzer does not "cheat" by reading the requested sample type. It performs automated spectral analysis using the following pipeline:

### Step 1: Noise Reduction & Data Integrity
Incoming `SpectrumData.msg` arrays are converted into NumPy arrays for high-performance vector operations.

### Step 2: Algorithmic Peak Detection
We utilize the `scipy.signal.find_peaks` algorithm. We apply two critical constraints:
*   **Prominence**: Only peaks that stand out significantly from the noise floor (threshold > 0.2) are considered.
*   **Distance**: A minimum distance constraint prevents the analyzer from double-counting noise spikes near a real peak.

### Step 3: Spectral Pattern Matching
The detected peaks are cross-referenced with the `element_signatures` database. A **Tolerance Window** (typically $\pm 2.0nm$) is used to account for the simulated instrument's resolution and calibration drift.

---

## 3. Distributed ROS 2 Architecture

The project leverages the power of ROS 2's **Data Distribution Service (DDS)** to ensure reliable communication.

### Custom Interfaces
| Interface Type | Name | Purpose |
| :--- | :--- | :--- |
| **Message** | `SpectrumData.msg` | Carries raw 1D arrays of sensor intensities. |
| **Message** | `AnalysisResult.msg` | Carries a list of identified elements and confidence scores. |
| **Service** | `TriggerMeasurement.srv` | Blocks the caller until the measurement cycle is complete. |

### Solving the Deadlock
The `MeasurementController` node performs a "synchronous" call to the Sensor. In standard ROS 2, this would freeze the node. 

**Implementation Strategy:**
```python
# From measurement_controller_node.py
node = MeasurementControllerNode()
executor = MultiThreadedExecutor() # Allows parallel processing
executor.add_node(node)
executor.spin()
```
By using the `MultiThreadedExecutor`, we allow one thread to "wait" for the sensor's service response while another thread remains free to handle incoming timer callbacks or heartbeats.

---

## 4. Containerization and Lifecycle

Using **Docker Compose**, we ensure that the entire ROS 2 environment, including scientific dependencies like `scipy`, is perfectly replicated regardless of the host OS (Windows/Mac/Linux).

The `entrypoint.sh` script handles the ROS 2 environment sourcing, ensuring that:
1.  Environment variables are set.
2.  Custom packages are sourced.
3.  The launch file is triggered as the main process (PID 1).

---

## 5. Future Scalability

This architecture is **Production-Ready** in its design:
*   **Hardware Abstraction**: To move to real hardware, one only needs to replace `libs_sensor_simulator_node.py` with a hardware-specific driver node.
*   **Navigation Integration**: The `AnalysisResult` can be piped into a mapping node (e.g., SLAM) to create a "Mineral Map" of the rover's environment.
*   **Autonomous Logic**: The `MeasurementController` can be extended to trigger measurements automatically based on visual detection of interesting rocks.
