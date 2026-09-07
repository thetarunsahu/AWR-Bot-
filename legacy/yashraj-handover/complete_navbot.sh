#!/bin/bash
set -e

source /opt/ros/jazzy/setup.bash

WS=/root/navbot_ws
PKG=$WS/src/navbot_description
WORLD=$PKG/worlds/navbot_sih_world.sdf

mkdir -p "$PKG/worlds" "$PKG/src" "$PKG/urdf" "$PKG/launch"

echo "========================================"
echo "NAVBOT SIH SIMULATION BOOTSTRAP"
echo "========================================"

# ---------- Package ----------
cat > "$PKG/package.xml" <<'EOF'
<?xml version="1.0"?>
<package format="3">
  <name>navbot_description</name>
  <version>0.1.0</version>
  <description>NavBot SIH robotics simulation</description>
  <maintainer email="navbot@example.com">NavBot Team</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
</package>
EOF

cat > "$PKG/CMakeLists.txt" <<'EOF'
cmake_minimum_required(VERSION 3.8)
project(navbot_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf worlds launch src
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
EOF

# ---------- Autonomous ROS controller foundation ----------
cat > "$PKG/src/navbot_controller.py" <<'EOF'
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class NavBotController(Node):
    def __init__(self):
        super().__init__('navbot_controller')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.move)

    def move(self):
        msg = Twist()
        msg.linear.x = 0.4
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = NavBotController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
EOF

chmod +x "$PKG/src/navbot_controller.py"

# ---------- Clean Gazebo world ----------
cat > "$WORLD" <<'EOF'
<?xml version="1.0"?>
<sdf version="1.9">

  <world name="navbot_sih_world">

    <plugin filename="gz-sim-physics-system"
            name="gz::sim::systems::Physics"/>

    <plugin filename="gz-sim-user-commands-system"
            name="gz::sim::systems::UserCommands"/>

    <plugin filename="gz-sim-scene-broadcaster-system"
            name="gz::sim::systems::SceneBroadcaster"/>

    <gravity>0 0 -9.81</gravity>

    <scene>
      <ambient>0.8 0.8 0.8 1</ambient>
      <background>0.85 0.85 0.85 1</background>
    </scene>

    <light type="directional" name="sun">
      <pose>0 0 10 0 0 0</pose>
      <direction>-0.5 -0.2 -1</direction>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
    </light>

    <!-- Ground -->
    <model name="ground">
      <static>true</static>
      <link name="ground_link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>30 30</size>
            </plane>
          </geometry>
        </collision>

        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>30 30</size>
            </plane>
          </geometry>
          <material>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Obstacle 1 -->
    <model name="obstacle_1">
      <static>true</static>
      <pose>4 1 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>0.8 0.8 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>0.8 0.8 1</size></box>
          </geometry>
          <material>
            <diffuse>1 0.15 0.15 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Obstacle 2 -->
    <model name="obstacle_2">
      <static>true</static>
      <pose>6 -1.5 0.75 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1 1 1.5</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1 1 1.5</size></box>
          </geometry>
          <material>
            <diffuse>1 0.55 0.1 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- NAVBOT -->
    <model name="navbot">

      <!-- Wheels touch the ground: wheel radius = 0.15 -->
      <pose>0 0 0.15 0 0 0</pose>

      <!-- Main body -->
      <link name="base_link">

        <pose>0 0 0.25 0 0 0</pose>

        <inertial>
          <mass>8.0</mass>
          <inertia>
            <ixx>0.5</ixx>
            <iyy>0.7</iyy>
            <izz>0.8</izz>
          </inertia>
        </inertial>

        <collision name="collision">
          <geometry>
            <box>
              <size>1.0 0.7 0.3</size>
            </box>
          </geometry>
        </collision>

        <visual name="visual">
          <geometry>
            <box>
              <size>1.0 0.7 0.3</size>
            </box>
          </geometry>
          <material>
            <diffuse>0.05 0.25 0.9 1</diffuse>
          </material>
        </visual>

        <!-- LiDAR foundation -->
        <sensor name="lidar" type="gpu_lidar">
          <pose>0.25 0 0.35 0 0 0</pose>
          <topic>/lidar</topic>
          <always_on>true</always_on>
          <update_rate>10</update_rate>
          <ray>
            <scan>
              <horizontal>
                <samples>360</samples>
                <resolution>1</resolution>
                <min_angle>-3.14159</min_angle>
                <max_angle>3.14159</max_angle>
              </horizontal>
            </scan>
            <range>
              <min>0.1</min>
              <max>10</max>
              <resolution>0.01</resolution>
            </range>
          </ray>
        </sensor>

      </link>

      <!-- LEFT WHEEL -->
      <link name="left_wheel">

        <pose>0 0.43 0 1.5708 0 0</pose>

        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.01</ixx>
            <iyy>0.01</iyy>
            <izz>0.01</izz>
          </inertia>
        </inertial>

        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.15</radius>
              <length>0.08</length>
            </cylinder>
          </geometry>
        </collision>

        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.15</radius>
              <length>0.08</length>
            </cylinder>
          </geometry>
          <material>
            <diffuse>0.05 0.05 0.05 1</diffuse>
          </material>
        </visual>

      </link>

      <!-- RIGHT WHEEL -->
      <link name="right_wheel">

        <pose>0 -0.43 0 1.5708 0 0</pose>

        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.01</ixx>
            <iyy>0.01</iyy>
            <izz>0.01</izz>
          </inertia>
        </inertial>

        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.15</radius>
              <length>0.08</length>
            </cylinder>
          </geometry>
        </collision>

        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.15</radius>
              <length>0.08</length>
            </cylinder>
          </geometry>
          <material>
            <diffuse>0.05 0.05 0.05 1</diffuse>
          </material>
        </visual>

      </link>

      <!-- LEFT JOINT -->
      <joint name="left_wheel_joint" type="revolute">
        <parent>base_link</parent>
        <child>left_wheel</child>
        <axis>
          <xyz>0 1 0</xyz>
          <limit>
            <lower>-1e16</lower>
            <upper>1e16</upper>
          </limit>
        </axis>
      </joint>

      <!-- RIGHT JOINT -->
      <joint name="right_wheel_joint" type="revolute">
        <parent>base_link</parent>
        <child>right_wheel</child>
        <axis>
          <xyz>0 1 0</xyz>
          <limit>
            <lower>-1e16</lower>
            <upper>1e16</upper>
          </limit>
        </axis>
      </joint>

      <!-- Differential drive -->
      <plugin filename="gz-sim-diff-drive-system"
              name="gz::sim::systems::DiffDrive">

        <left_joint>left_wheel_joint</left_joint>
        <right_joint>right_wheel_joint</right_joint>

        <wheel_separation>0.86</wheel_separation>
        <wheel_radius>0.15</wheel_radius>

        <topic>/cmd_vel</topic>
        <odom_topic>/odom</odom_topic>

        <odom_publish_frequency>30</odom_publish_frequency>

      </plugin>

    </model>

  </world>

</sdf>
EOF

# ---------- Documentation ----------
cat > "$WS/README.md" <<'EOF'
# NavBot SIH Foundation

Current implemented simulation layer:

- ROS 2 Jazzy package
- Gazebo Sim world
- Differential-drive NavBot
- cmd_vel interface
- odometry interface
- LiDAR sensor foundation
- obstacle environment
- autonomous controller foundation

Next layer:

- ROS-Gazebo bridge
- obstacle avoidance logic
- SLAM
- Nav2
- global path planning
- autonomous mission logic
- hardware integration
EOF

echo ""
echo "Building package..."
cd "$WS"
colcon build --packages-select navbot_description

echo ""
echo "Stopping old Gazebo processes..."
pkill -f "gz sim" 2>/dev/null || true
sleep 2

echo ""
echo "Starting NavBot simulation..."

# Start movement publisher after simulation has loaded
(
  sleep 10

  echo "NAVBOT AUTO DEMO: FORWARD"

  for i in $(seq 1 80); do
    gz topic -t /cmd_vel -m gz.msgs.Twist \
      -p 'linear: {x: 0.35}, angular: {z: 0.0}' >/dev/null 2>&1
    sleep 0.1
  done

  echo "NAVBOT AUTO DEMO: TURN"

  for i in $(seq 1 40); do
    gz topic -t /cmd_vel -m gz.msgs.Twist \
      -p 'linear: {x: 0.0}, angular: {z: 0.5}' >/dev/null 2>&1
    sleep 0.1
  done

  echo "NAVBOT AUTO DEMO: FORWARD"

  for i in $(seq 1 80); do
    gz topic -t /cmd_vel -m gz.msgs.Twist \
      -p 'linear: {x: 0.35}, angular: {z: 0.0}' >/dev/null 2>&1
    sleep 0.1
  done

  gz topic -t /cmd_vel -m gz.msgs.Twist \
    -p 'linear: {x: 0.0}, angular: {z: 0.0}' >/dev/null 2>&1

) &

# GUI support for your existing Windows XLaunch setup
export DISPLAY=${DISPLAY:-host.docker.internal:0.0}
export QT_X11_NO_MITSHM=1

echo ""
echo "========================================"
echo "NAVBOT READY"
echo "========================================"
echo "Robot: navbot"
echo "Interfaces: /cmd_vel /odom /lidar"
echo "Auto movement begins after Gazebo loads."
echo "========================================"

gz sim -r "$WORLD"
