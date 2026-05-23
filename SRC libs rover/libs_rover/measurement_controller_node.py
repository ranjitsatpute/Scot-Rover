#!/usr/bin/env python3
import rclpy
import random
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Empty
from libs_rover_pkg.srv import TriggerMeasurement

class MeasurementControllerNode(Node):
    def __init__(self):
        super().__init__('measurement_controller')
        
        # Use ReentrantCallbackGroup to allow concurrent service calls
        self.cb_group = ReentrantCallbackGroup()
        
        # Service Server: Accepts high-level command from user
        self.srv = self.create_service(
            TriggerMeasurement, 
            '/libs/trigger_measurement', 
            self.handle_measurement_request,
            callback_group=self.cb_group
        )
        
        # Service Client: Calls the sensor simulator
        self.sensor_client = self.create_client(
            TriggerMeasurement, 
            '/libs/sensor/scan', 
            callback_group=self.cb_group
        )
        
        self.get_logger().info('Measurement Controller ready. Request measurements via /libs/trigger_measurement')

    def handle_measurement_request(self, request, response):
        target_sample = request.sample_type
        
        # Handle random selection - valid samples list
        valid_samples = ['basalt', 'granite', 'iron_ore', 'limestone']
        
        if target_sample == 'random' or target_sample == '':
            target_sample = random.choice(valid_samples)
            self.get_logger().info(f'Randomly selected: {target_sample}')
            
        self.get_logger().info(f'Controller processing request for: {target_sample}')
        
        # 1. Validation logic
        if request.laser_power_percent > 100 or request.laser_power_percent < 0:
            response.success = False
            response.message = "Invalid laser power setting."
            return response
            
        self.get_logger().info('Rover systems ready. Aiming laser...')
        self.get_logger().info('Firing laser...')
        
        # 2. Rover ready Call Sensor
        if not self.sensor_client.wait_for_service(timeout_sec=2.0):
            response.success = False
            response.message = "Sensor service not available!"
            return response

        # controller Construct new request
        sensor_req = TriggerMeasurement.Request()
        sensor_req.sample_type = target_sample
        sensor_req.laser_power_percent = request.laser_power_percent
            
        # Synchronous call is safe here because we are using MultiThreadedExecutor
        try:
            sensor_resp = self.sensor_client.call(sensor_req) # fires in sim
            response.success = sensor_resp.success #sensor sends the spectrum back and puts in response box 
            response.message = f"Controller: {sensor_resp.message}" 
            response.spectrum = sensor_resp.spectrum #controller sends the spectrum back to user
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')
            response.success = False
            response.message = f"Sensor call failed: {str(e)}"
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = MeasurementControllerNode()
    
    # Use MultiThreadedExecutor to handle service callbacks concurrently
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
