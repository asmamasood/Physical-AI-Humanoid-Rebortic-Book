---
title: "Module 1: The Robotic Nervous System (ROS 2) - Chapter 1"
---

# Module 1: The Robotic Nervous System (ROS 2)

## Chapter 1: Introduction to ROS 2

### Subchapter 1: Understanding ROS 2 Fundamentals

#### Nodes

**Introduction**
This section introduces the concept of nodes in ROS 2, which are the fundamental processes that perform computation.

**Description**
In ROS 2, a node is an executable that uses ROS 2 client libraries to communicate with other nodes. Nodes can receive and send messages to other nodes using topics, services, and actions. They are the basic building blocks of a ROS 2 system, allowing for modular and distributed robot software development. For example, a camera driver might be a node that publishes images, and a node that processes these images might subscribe to the camera's topic.

**Code Example**
```python
# Basic ROS 2 node example in Python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_minimal_node')
        self.get_logger().info('Hello from my minimal ROS 2 node!')

def main(args=None):
    rclpy.init(args=args)
    minimal_node = MyNode()
    try:
        rclpy.spin(minimal_node)
    except KeyboardInterrupt:
        pass
    finally:
        minimal_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Diagram/Graph Placeholder**
![Diagram: A simple ROS 2 computation graph showing nodes, topics, and publishers/subscribers.](pathname:///static/img/placeholder_diagram_ros2_nodes.png)

**Quiz**
What is the primary role of a ROS 2 node?
a) To manage the robot's hardware.
b) To perform computations and communicate with other nodes.
c) To store robot configuration files.
d) To provide a user interface for robot control.

**Glossary**
-   **Node**: An executable process in ROS 2 that performs computation and communicates with other nodes.
-   **rclpy**: The Python client library for ROS 2.

**References**
-   [ROS 2 Documentation - Nodes](https://docs.ros.org/en/rolling/Concepts/About-Nodes.html)

**History**
ROS 2 nodes are an evolution from ROS 1 nodes, designed with improved security, real-time capabilities, and support for DDS (Data Distribution Service). The concept of modular executables communicating over a middleware remains central.
