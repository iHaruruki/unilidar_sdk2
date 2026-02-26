import os
import subprocess

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Run unitree lidar
    node1 = Node(
        package='unitree_lidar_ros2',
        executable='unitree_lidar_ros2_node',
        name='unitree_lidar_ros2_node',
        output='screen',
        parameters= [
                
            {'initialize_type': 2},
            {'work_mode': 0},
            {'use_system_timestamp': True},
            {'range_min': 0.0},
            {'range_max': 100.0},
            {'cloud_scan_num': 18},

            {'serial_port': '/dev/ttyACM0'},
            {'baudrate': 4000000},

            {'lidar_port': 6101},
            {'lidar_ip': '192.168.1.62'},
            {'local_port': 6201},
            {'local_ip': '192.168.1.2'},
            
            {'cloud_frame': "unilidar_lidar"},
            {'cloud_topic': "unilidar/cloud"},
            #{'imu_frame': "unilidar_imu"},
            {'imu_topic': "imu/data_raw"},
        ],
    )

    # imu_complementary_filter
    filter_node = Node(
        package='imu_complementary_filter',
        executable='complementary_filter_node',
        name='complementary_filter_node',
        output='screen',
        parameters= [
            {'bias_alpha': 0.01},
            {'use_mag': False},
            {'fixed_frame': "unilidar_imu_initial"},
            {'publish_tf': True},
            {'publish_debug_topics': True},
        ]
    )

    # Run Rviz
    package_path = subprocess.check_output(['ros2', 'pkg', 'prefix', 'unitree_lidar_ros2']).decode('utf-8').rstrip()
    rviz_config_file = os.path.join(package_path, 'share', 'unitree_lidar_ros2', 'view.rviz')
    print("rviz_config_file = " + rviz_config_file)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='log'
    )
    return LaunchDescription([node1, filter_node, rviz_node])