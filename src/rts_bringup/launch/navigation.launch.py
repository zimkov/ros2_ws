import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_nav2_bringup = FindPackageShare('nav2_bringup').find('nav2_bringup')
    
    # Путь к нашему файлу параметров по умолчанию
    default_params_file = os.path.expanduser('~/ros2_ws/src/rts_bringup/config/nav2_params.yaml')

    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=os.path.expanduser('~/my_map.yaml'),
        description='Full path to map yaml file to load'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    # Запуск стандартного bringup_launch.py из nav2_bringup
    nav2_bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
            'use_collision_monitor': 'False',
            'use_docking': 'False',
        }.items()
    )

    return LaunchDescription([
        declare_map_yaml_cmd,
        declare_params_file_cmd,
        declare_use_sim_time_cmd,
        declare_autostart_cmd,
        nav2_bringup_cmd
    ])
