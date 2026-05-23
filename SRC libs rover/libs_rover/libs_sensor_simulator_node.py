#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import yaml
import os
import time
from ament_index_python.packages import get_package_share_directory
from std_msgs.msg import Empty
from libs_rover_pkg.msg import SpectrumData
from libs_rover_pkg.srv import TriggerMeasurement
from libs_rover.utils.spectrum_generator import SpectrumGenerator

import matplotlib.pyplot as plt

class LibsSensorSimulatorNode(Node):
    def __init__(self):
        super().__init__('libs_sensor_simulator')
        self.declare_parameter('database_file', 'spectral_database.yaml')
        self.declare_parameter('noise_level', 0.05)
        
        # Load configuration / calibrate data 
        self.load_database()
        self.generator = SpectrumGenerator(self.database)
        
        # Publisher
        self.publisher_ = self.create_publisher(SpectrumData, '/libs/spectrum', 10)
        
        # Subscriber (for simple trigger)
        self.trigger_sub = self.create_subscription(
            Empty, 
            '/libs/trigger', 
            self.trigger_callback, 
            10
        )

        # Service to trigger measurement directly (testing, debugging and manual triggering)
        self.srv = self.create_service(
            TriggerMeasurement, 
            '/libs/sensor/scan', 
            self.scan_callback
        )
        
        self.get_logger().info('LIBS Sensor Simulator initialized. Ready to scan.')

    def load_database(self):
        try:
            # Try to find file in share directory first
            pkg_share = get_package_share_directory('libs_rover_pkg')
            config_file = os.path.join(pkg_share, 'config', 'spectral_database.yaml')
            
            with open(config_file, 'r') as f:
                self.database = yaml.safe_load(f)
            self.get_logger().info(f'Loaded spectral database from {config_file}')
        except Exception as e:
            self.get_logger().error(f'Failed to load spectral database: {e}')
            # Fallback for testing without install
            self.database = {'samples': {}, 'element_signatures': {}}

    def scan_callback(self, request, response):
        self.get_logger().info(f'Received scan request for sample: {request.sample_type}')
        try:
            # Get current noise level from parameters
            noise = self.get_parameter('noise_level').value
            wavelengths, intensities = self.generator.generate_spectrum(request.sample_type, noise_level=noise)
            
            # Create message
            msg = SpectrumData()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "libs_sensor_link"
            msg.sample_id = f"{request.sample_type}_{int(time.time())}"
            msg.wavelengths = wavelengths.tolist()
            msg.intensities = intensities.tolist()
            msg.integration_time = 0.1
            
            # Plot and save locally (for visualization without GUI)
            self.save_plot(wavelengths, intensities, msg.sample_id)
            
            # Publish
            self.publisher_.publish(msg)
            
            response.success = True
            response.message = f"Scan complete. Data published for {request.sample_type}"
            response.spectrum = msg
        except Exception as e:
            response.success = False
            response.message = f"Scan failed: {str(e)}"
            self.get_logger().error(f"Scan failed: {e}")
            
        return response

    def trigger_callback(self, msg):
        self.get_logger().info('Received simple trigger. Scanning default sample (basalt)...')
        # Simulate a request
        request = TriggerMeasurement.Request()
        request.sample_type = 'basalt'
        response = TriggerMeasurement.Response()
        
        self.scan_callback(request, response)

    def save_plot(self, wavelengths, intensities, sample_id):
        try:
            output_dir = '/ros2_ws/output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            plt.figure(figsize=(10, 6))
            plt.plot(wavelengths, intensities, color='purple', linewidth=1)
            plt.title(f'LIBS Spectrum: {sample_id}')
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Intensity (a.u.)')
            plt.grid(True, alpha=0.3)
            
            filename = os.path.join(output_dir, f'spectrum_{sample_id}.png')
            plt.savefig(filename)
            plt.close()
            self.get_logger().info(f'Saved spectrum plot to {filename}')
        except Exception as e:
            self.get_logger().error(f'Failed to save plot: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = LibsSensorSimulatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
