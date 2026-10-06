import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_rts_description = FindPackageShare(package='rts_description').find('rts_description')
    pkg_rts_bringup = FindPackageShare(package='rts_bringup').find('rts_bringup')
    
    home_dir = os.path.expanduser('~')
    local_world = os.path.join(home_dir, 'map_for_rts.sdf')
    local_bridge = os.path.join(home_dir, 'bridge.yaml')

    world_file = local_world if os.path.isfile(local_world) else PathJoinSubstitution([pkg_rts_description, 'models', 'rts', 'map_for_rts.sdf'])
    bridge_config = local_bridge if os.path.isfile(local_bridge) else PathJoinSubstitution([pkg_rts_bringup, 'config', 'bridge.yaml'])
    
    # ВАЖНО: заставляем OGRE2 использовать software rendering (работает под WSL2)
    env_vars = [
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.expanduser('~/ros2_ws/install/rts_description/share')),
    ]
    
    rviz_arg = DeclareLaunchArgument('rviz', default_value='false', description='Open RViz2 if true')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock')
    
    # Gazebo
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={'LIBGL_ALWAYS_SOFTWARE': '1'}
    )
    
    # Мост Gazebo <-> ROS
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='parameter_bridge',
        output='screen',
        parameters=[{'config_file': bridge_config}],
    )
    
    # RViz2 (запуск со временем симуляции)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )
    
    # Статические TF для сенсоров (фреймы в точности соответствуют Gazebo Sim)
    tf_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_lidar',
        arguments=['0.02', '0.0', '0.130', '0', '0', '0', 'base_link', 'rts_robot/base_link/lidar_front'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    # Алиас для стандартного имени lidar_front
    tf_lidar_alias = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_lidar_alias',
        arguments=['0', '0', '0', '0', '0', '0', 'rts_robot/base_link/lidar_front', 'lidar_front'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    tf_camera_left = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_camera_left',
        arguments=['0.10', '0.025', '0.1124', '0', '0', '0', 'base_link', 'rts_robot/base_link/camera_left'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    tf_camera_right = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_camera_right',
        arguments=['0.10', '-0.025', '0.1124', '0', '0', '0', 'base_link', 'rts_robot/base_link/camera_right'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    tf_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_imu',
        arguments=['0.0', '0.0', '0.05', '0', '0', '0', 'base_link', 'rts_robot/base_link/imu'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    return LaunchDescription([
        *env_vars,
        rviz_arg,
        use_sim_time_arg,
        gazebo,
        bridge,
        rviz_node,
        tf_lidar,
        tf_lidar_alias,
        tf_camera_left,
        tf_camera_right,
        tf_imu,
    ])
