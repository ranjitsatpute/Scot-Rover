#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from libs_rover_pkg.msg import SpectrumData, AnalysisResult
from libs_rover_pkg.srv import TriggerMeasurement
from std_msgs.msg import Empty
import sys

class BackendMonitorNode(Node):
    def __init__(self):
        super().__init__('backend_monitor')
        
        # Subscribe to Spectrum Data (from Sensor)
        self.create_subscription(
            SpectrumData, 
            '/libs/spectrum', 
            self.monitor_spectrum, 
            10
        )
        
        # Subscribe to Analysis Results (from Analyzer)
        self.create_subscription(
            AnalysisResult, 
            '/libs/analysis', 
            self.monitor_analysis, 
            10
        )
        
        print("\n" + "="*60)
        print("   LIBS BACKEND MONITOR - WATCHING DATA FLOW")
        print("="*60)
        print(" Waiting for activity...\n")

    def monitor_spectrum(self, msg):
        print(f"\n[SENSOR] -> [ANALYZER]  Topic: /libs/spectrum")
        print(f"  ├── Data Packet Size: {sys.getsizeof(msg.intensities) + sys.getsizeof(msg.wavelengths)} bytes")
        print(f"  ├── Sample ID: {msg.sample_id}")
        print(f"  ├── Data Points: {len(msg.wavelengths)} wavelengths")
        print(f"  └── Timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}")

    def monitor_analysis(self, msg):
        print(f"\n[ANALYZER] -> [DASHBOARD] Topic: /libs/analysis")
        print(f"  ├── Processed Spectrum: {msg.spectrum.sample_id}")
        print(f"  └── Elements Found: {len(msg.found_elements)}")
        
        if len(msg.found_elements) > 0:
            print("      Results:")
            for elem in msg.found_elements:
                bar_len = int(elem.confidence * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"      - {elem.element_name:<10} ({elem.element_symbol}): {bar} {elem.confidence:.1f}")
        else:
            print("      (No elements identified)")
            
        print("-" * 60)

def main(args=None):
    rclpy.init(args=args)
    node = BackendMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
