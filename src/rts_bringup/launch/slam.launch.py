import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_slam_toolbox = FindPackageShare('slam_toolbox').find('slam_toolbox')
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')

    # Путь к конфигурационному файлу (приоритет локальному файлу в домашней папке)
    home_dir = os.path.expanduser('~')
    local_slam_config = os.path.join(home_dir, 'slam_toolbox.yaml')
    default_config_path = local_slam_config if os.path.isfile(local_slam_config) else PathJoinSubstitution([
        FindPackageShare('rts_bringup'),
        'config',
        'slam_toolbox.yaml'
    ])

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock'
    )

    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value=default_config_path,
        description='Full path to the ROS2 parameters file to use for slam_toolbox'
    )

    # Используем официальный launch-файл slam_toolbox, который сам правильно активирует Lifecycle
    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
        }.items()
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_slam_params_file,
        slam_toolbox_launch
    ])
