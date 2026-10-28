from launch import LaunchDescription
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_share = FindPackageShare('one_joint_robot_description')

    robot_description = Command([
        'xacro ',
        PathJoinSubstitution([
            package_share,
            'urdf',
            'one_joint_robot.urdf.xacro'
        ])
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('ros_gz_sim'),
            '/launch/gz_sim.launch.py'
        ]),
        launch_arguments={
            'gz_args': '-r -v 1 empty.sdf --render-engine ogre'
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': ParameterValue(
                robot_description,
                value_type=str
            ),
            'use_sim_time': True
        }],
        output='screen'
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'one_joint_robot',
            '-allow_renaming', 'true'
        ],
        output='screen'
    )

    load_controllers = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager',
                    '/controller_manager'
                ],
                output='screen'
            ),
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'forward_position_controller',
                    '--controller-manager',
                    '/controller_manager'
                ],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        load_controllers
    ])
