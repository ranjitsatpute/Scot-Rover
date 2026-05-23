#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np
import yaml
import os
from ament_index_python.packages import get_package_share_directory
from libs_rover_pkg.msg import SpectrumData, ElementResult, AnalysisResult
from scipy.signal import find_peaks

class SpectrumAnalyzerNode(Node):
    def __init__(self):
        super().__init__('spectrum_analyzer')
        
        self.load_database()
        
        self.subscription = self.create_subscription(
            SpectrumData,   
            '/libs/spectrum',
            self.listener_callback,
            10)
            
        self.publisher_ = self.create_publisher(AnalysisResult, '/libs/analysis', 10)
        
        self.get_logger().info('Spectrum Analyzer initialized and listening...')

    def load_database(self):
        try:
            pkg_share = get_package_share_directory('libs_rover_pkg')
            config_file = os.path.join(pkg_share, 'config', 'spectral_database.yaml')
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.signatures = data.get('element_signatures', {})
        except Exception as e:
            self.get_logger().error(f'Failed to load database: {e}')
            self.signatures = {}

    def listener_callback(self, msg):
        self.get_logger().info(f'Received spectrum: {msg.sample_id} ({len(msg.wavelengths)} points)')
        
        wavelengths = np.array(msg.wavelengths)
        intensities = np.array(msg.intensities)
        
        peaks, _ = find_peaks(intensities, height=0.2, distance=10)
        
        detected_elements = []
        found_symbols = set()   
        
        # 2. Match peaks to database
        self.get_logger().info(f"Found {len(peaks)} significant peaks. Analysing...")
        
        # Dictionary to track how many lines we find for each element
        # Form: { 'Fe': [line1_found, line2_found, ...], ... }
        match_tracker = {symbol: [False] * len(lines) for symbol, lines in self.signatures.items()}
        # To store the max intensity found for each matched element
        max_intensities = {symbol: 0.0 for symbol in self.signatures}
        # To store the first wavelength we found for each element (for the report)
        first_wavelengths = {symbol: 0.0 for symbol in self.signatures}

        for peak_idx in peaks:
            peak_wl = wavelengths[peak_idx]
            peak_int = intensities[peak_idx]
            
            for symbol, lines in self.signatures.items():
                for i, line in enumerate(lines):
                    if abs(peak_wl - line) < 2.0: # 2nm tolerance
                        match_tracker[symbol][i] = True
                        max_intensities[symbol] = max(max_intensities[symbol], peak_int)
                        if first_wavelengths[symbol] == 0.0:
                            first_wavelengths[symbol] = peak_wl

        # 3. Calculate Final Confidence and Build Results
        for symbol, matches in match_tracker.items():
            lines_found = sum(matches)
            if lines_found > 0:
                total_lines = len(matches)
                # MULTI-PEAK CONFIDENCE CALCULATION:
                # 70% based on how many of the element's lines we found (The "Pattern")
                # 30% based on how strong the strongest peak was (The "Intensity")
                line_ratio = lines_found / total_lines
                intensity_factor = max_intensities[symbol]
                
                final_confidence = (0.7 * line_ratio) + (0.3 * intensity_factor)
                
                self.get_logger().info(f"  -> Match: {symbol} ({lines_found}/{total_lines} lines found). Conf: {final_confidence:.2f}")

                #Constructs ElementResult objects for each detected element.
                result = ElementResult()
                result.element_symbol = symbol
                result.element_name = self.get_element_name(symbol)
                result.confidence = float(final_confidence)
                result.relative_intensity = float(max_intensities[symbol])
                result.wavelength_detected = float(first_wavelengths[symbol])
                
                detected_elements.append(result)
        
        # 3. Publish results :message containing the spectrum and the detected elements.
        analysis_msg = AnalysisResult()
        analysis_msg.header = msg.header
        analysis_msg.spectrum = msg
        analysis_msg.found_elements = detected_elements
        
        self.publisher_.publish(analysis_msg)
        
        # Logs a human-readable report of all detected elements and their confidence.
        self.get_logger().info("--- ANALYSIS REPORT ---")
        if not detected_elements:
            self.get_logger().info("No known elements identified.")
        for res in detected_elements:
            self.get_logger().info(f"Element: {res.element_name} ({res.element_symbol}) - Conf: {res.confidence:.2f}")
        self.get_logger().info("-----------------------")

    def get_element_name(self, symbol):
        names = {
            "Fe": "Iron", "Si": "Silicon", "Ca": "Calcium", 
            "Mg": "Magnesium", "Al": "Aluminum", "Ti": "Titanium",
            "K": "Potassium", "Na": "Sodium", "O": "Oxygen", "C": "Carbon"
        }
        return names.get(symbol, "Unknown")

def main(args=None):
    rclpy.init(args=args)
    node = SpectrumAnalyzerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
