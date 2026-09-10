# amr_mission_manager

The warehouse mission and inventory layer for SIH26112. This ROS 2 Jazzy
`ament_python` package turns an item/SKU request into the rack's target pose in
the `map` frame. It runs independently of the robot model, Gazebo, SLAM, Nav2,
and motor control.

`DELIVER` currently means **resolve the requested SKU and publish its rack
target**. It does not drive the robot, collect an item, or execute a delivery.

## Architecture

```text
Warehouse task JSON on /amr/task_request
              |
              v
    Parse and validate task_id, sku, action
              |
              v
    InventoryManager: SKU -> item -> rack ID -> x, y, yaw
              |
              v
    Mission logic: planar yaw -> quaternion
              |
              v
    mission_manager: map-frame PoseStamped
              |
              +--> /amr/target_pose
              +--> /amr/mission_status
              |
              v
    Future adapter -> Nav2 NavigateToPose
```

- `inventory_manager.py` loads and validates YAML and provides item/rack lookup
  through ordinary Python methods.
- `mission_logic.py` validates requests and generates target data without ROS
  dependencies.
- `mission_manager.py` owns ROS subscriptions, publications, parameters,
  timestamps, and logging.
- `send_demo_task` is a separate executable for sending one task.

## Topics and request format

| Topic | Type | Direction | Content |
|---|---|---|---|
| `/amr/task_request` | `std_msgs/msg/String` | Subscribe | Task JSON |
| `/amr/target_pose` | `geometry_msgs/msg/PoseStamped` | Publish | Rack target in `map` |
| `/amr/mission_status` | `std_msgs/msg/String` | Publish | Human-readable processing state |

All three topics use reliable, volatile QoS with a queue depth of 10. Start
subscribers before sending a task: previously published targets and statuses
are not replayed to late subscribers.

```json
{"task_id": "TASK001", "sku": "SKU001", "action": "DELIVER"}
```

The JSON must be an object with nonempty string fields `task_id`, `sku`, and
`action`. Surrounding whitespace in request fields is trimmed; SKU and action
matching are case sensitive. The supported action is `DELIVER`. `task_id` and
`sku` are limited to 128 characters each, and a request to 16,384 characters.
Duplicate JSON keys and nonstandard constants such as `NaN` are rejected.
Invalid input produces a status without publishing a target.

Statuses have the form `STATE task_id=... sku=...: detail`:

| State | Meaning |
|---|---|
| `TASK_RECEIVED` | The request passed JSON/schema validation |
| `SKU_RESOLVED` | The SKU and its configured rack were found |
| `TARGET_GENERATED` | A target pose was published |
| `INVALID_SKU` | The request was valid but its SKU was unknown |
| `INVALID_REQUEST` | Malformed JSON, missing/invalid fields, or unsupported action |

A successful request emits `TASK_RECEIVED`, `SKU_RESOLVED`, then
`TARGET_GENERATED`. An unknown SKU emits `TASK_RECEIVED`, then `INVALID_SKU`.
`TARGET_GENERATED` reports pose publication only; it does not report navigation
acceptance or arrival.

## Inventory YAML

The installed `config/inventory.yaml` contains ten sample items and racks. Its
format is:

```yaml
items:
  SKU001:
    name: "Laptop"
    rack: "RACK_A1"
  SKU002:
    name: "Keyboard"
    rack: "RACK_B2"

racks:
  RACK_A1:
    x: 2.0
    y: 4.0
    yaw: 0.0
  RACK_B2:
    x: 6.5
    y: 1.5
    yaw: 1.57
```

`x` and `y` are metres in `map`; `yaw` is radians about the positive Z axis.
The target has `z = 0`, with quaternion
`x = 0, y = 0, z = sin(yaw / 2), w = cos(yaw / 2)`.

The inventory validates mapping structure, identifiers, item names, rack
references, and finite numeric coordinates. Booleans are not coordinates.
Inventory identifiers must not contain surrounding whitespace.
An unreadable or invalid inventory, including an item referencing a missing
rack, prevents node startup and logs an error. The file is loaded once at
startup; restart the node after editing it.

These coordinates are examples. Before enabling navigation, replace them with
surveyed, reachable rack **approach poses** in the actual warehouse map, leaving
clearance for the robot footprint. Rack centres may be occupied and unsuitable
as navigation goals.

## Build

Use a Linux environment with ROS 2 Jazzy installed, such as Ubuntu 24.04. From
the repository root:

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
colcon build --packages-select amr_mission_manager --symlink-install
source install/setup.bash
```

Runtime dependencies are ROS 2 Python/package support, standard/geometry
messages, launch support, and PyYAML. Nav2 is not a package dependency.

## Run

In each terminal, source ROS 2 and this workspace's `install/setup.bash`. From
`ros2_ws`, start the node with its installed inventory:

```bash
ros2 launch amr_mission_manager mission_manager.launch.py
```

The launch file passes an `inventory_file` parameter resolved from
`get_package_share_directory('amr_mission_manager')`. Override it with a custom
file if needed:

```bash
ros2 launch amr_mission_manager mission_manager.launch.py \
  inventory_file:="$(pwd)/src/amr_mission_manager/config/inventory.yaml"
```

The equivalent direct node invocation also finds the installed default file:

```bash
ros2 run amr_mission_manager mission_manager
```

`use_sim_time` defaults to `false`. When connected later to a simulation that
publishes `/clock`, use `use_sim_time:=true` on the launch command. Target
timestamps come from the node's ROS clock.

## Demo and expected output

Start these observers in separate sourced terminals before the request:

```bash
ros2 topic echo /amr/mission_status std_msgs/msg/String
```

```bash
ros2 topic echo /amr/target_pose geometry_msgs/msg/PoseStamped
```

Send a task:

```bash
ros2 run amr_mission_manager send_demo_task SKU001 --task-id TASK001
```

Without `--task-id`, the demo generates a task ID. It waits up to five seconds
for a subscriber and waits for middleware acknowledgement before exiting. A
timeout produces a nonzero exit status. Middleware acknowledgement is not a
mission execution acknowledgement.

For a source-tree invocation after sourcing the built workspace:

```bash
python3 src/amr_mission_manager/scripts/send_demo_task.py SKU001
```

The ROS CLI can send the same request:

```bash
ros2 topic pub --once /amr/task_request std_msgs/msg/String \
  '{data: "{\"task_id\":\"TASK001\",\"sku\":\"SKU001\",\"action\":\"DELIVER\"}"}'
```

For `SKU001`, the status observer shows the three successful states with
`task_id=TASK001` and `sku=SKU001`. The target contains a current timestamp and:

```yaml
header:
  frame_id: map
pose:
  position: {x: 2.0, y: 4.0, z: 0.0}
  orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
```

Use an unknown SKU such as `UNKNOWN` to observe `INVALID_SKU` with no new pose.
Malformed JSON or an unsupported action yields `INVALID_REQUEST` with no new
pose; neither stops subsequent valid requests from being processed.

## Tests

From a built, sourced `ros2_ws`:

```bash
colcon test --packages-select amr_mission_manager --event-handlers console_direct+
colcon test-result --verbose
```

Pure Python tests cover SKU resolution, unknown SKUs, missing racks, coordinate
lookup, invalid inventory data, malformed requests, and quaternion conversion.
The ROS integration test exercises the real topic interface when ROS 2 is
available; it is skipped in environments without the required ROS packages.

To run only the pure tests without ROS 2, install PyYAML and pytest in your
Python environment, then run from the package directory:

```bash
python3 -m pytest test/test_inventory_manager.py test/test_mission_logic.py
```

## Future Nav2 integration and limitations

The exact next integration point is a separate adapter subscribing to
`/amr/target_pose` and using an action client for
`nav2_msgs/action/NavigateToPose` (typically `/navigate_to_pose`):

```python
goal = NavigateToPose.Goal()
goal.pose = received_target_pose
# Submit with the adapter's NavigateToPose action client.
```

The adapter should own server readiness, goal admission, cancellation, feedback,
and navigation results. The inventory and mission resolution code can remain
unchanged. `PoseStamped` contains no `task_id`: reliable task-to-action UUID
correlation needs an explicit interface design before supporting concurrent
missions or reporting per-task arrival. The status strings are diagnostic
output rather than a structured action result protocol.

This package currently resolves each request immediately. It provides no task
queue, duplicate suppression/idempotency, persistence, inventory stock
quantities, dynamic updates, cancellation, map/TF reachability checks, docking,
or payload handling. Repeating a valid request publishes another target.
Enabling the adapter still depends on the project's motion, TF, odometry,
localization, and Nav2 milestones.
