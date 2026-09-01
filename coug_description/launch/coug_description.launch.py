# Copyright (c) 2026 BYU FROST Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Any

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchContext, LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    EnvironmentVariable,
    EqualsSubstitution,
    LaunchConfiguration,
    NotEqualsSubstitution,
    OrSubstitution,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context: LaunchContext, *args: Any, **kwargs: Any) -> list[Node]:
    use_sim_time = LaunchConfiguration("use_sim_time")
    agent_ns = LaunchConfiguration("agent_ns")
    agent_ns_str = agent_ns.perform(context)

    coug_description_dir = get_package_share_directory("coug_description")
    fleet_param_file = PathJoinSubstitution(
        [
            EnvironmentVariable("CONFIG_DIR"),
            "fleet",
            "coug_description_params.yaml",
        ]
    )
    config_dir = os.environ["CONFIG_DIR"]

    def load_launch_params(path: str, top_key: str) -> dict[str, Any]:
        try:
            with open(path) as config_file:
                config = yaml.safe_load(config_file)
            return config[top_key]["coug_description_launch"]["ros__parameters"]
        except (KeyError, TypeError, OSError):
            return {}

    fleet_defaults = load_launch_params(
        os.path.join(config_dir, "fleet", "coug_description_params.yaml"), "/**"
    )
    agent_launch_params = load_launch_params(
        os.path.join(config_dir, f"{agent_ns_str}_params.yaml"), f"/{agent_ns_str}"
    )
    urdf_filename = agent_launch_params.get(
        "urdf_file",
        fleet_defaults.get("urdf_file", "couguv_holoocean.urdf.xacro"),
    )
    urdf_file = os.path.join(coug_description_dir, "urdf", urdf_filename)

    frame_prefix = PythonExpression(
        ["'", agent_ns, "/' if '", agent_ns, "' != '' else ''"]
    )

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[
                fleet_param_file,
                agent_launch_params,
                {
                    "robot_description": ParameterValue(
                        Command(["xacro ", urdf_file]),
                        value_type=str,
                    ),
                    "use_sim_time": use_sim_time,
                    "frame_prefix": frame_prefix,
                },
            ],
        ),
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            parameters=[
                fleet_param_file,
                agent_launch_params,
                {"use_sim_time": use_sim_time},
            ],
            condition=IfCondition(
                OrSubstitution(
                    NotEqualsSubstitution(use_sim_time, "true"),
                    EqualsSubstitution(agent_ns, "coug2"),
                )
            ),
        ),
    ]


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation/rosbag clock if true",
            ),
            DeclareLaunchArgument(
                "agent_ns",
                default_value="auv0",
                description="Namespace for the agent (e.g. auv0)",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
