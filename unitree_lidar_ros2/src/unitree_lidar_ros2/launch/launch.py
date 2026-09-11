import os
import subprocess

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import GroupAction, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    complementary_args = [
        DeclareLaunchArgument("cf_publish_tf", default_value="true"),
        DeclareLaunchArgument("cf_use_mag", default_value="false"),
        DeclareLaunchArgument("cf_bias_alpha", default_value="0.01"),
        DeclareLaunchArgument("cf_gain_acc", default_value="0.01"),
        DeclareLaunchArgument("cf_gain_mag", default_value="0.01"),
    ]
    cf_parameters = [{arg.name: LaunchConfiguration(arg.name)} for arg in complementary_args]

    # Run unitree lidar
    node1 = Node(
        package='unitree_lidar_ros2',
        executable='unitree_lidar_ros2_node',
        name='unitree_lidar_ros2_node',
        output='screen',
        parameters= [
                
                {'initialize_type': 2},
                {'work_mode': 1},
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
                {'imu_frame': "unilidar_imu"},
                {'imu_topic': "unilidar/imu"},
                {'publish_imu_initial_tf': True},
                {'publish_imu_to_lidar_tf': True},
                ]
    )

    imu_iomp_node = Node(
        package='imu_complementary_filter',
        executable='complementary_filter_node',
        name='complementary_filter_node',
        parameters=cf_parameters,
        remappings=[
            ('/imu/data_raw', '/unilidar/imu')
        ],
        output='screen',
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
    return LaunchDescription(
        complementary_args + [
        node1,
        imu_iomp_node,
        rviz_node
    ])