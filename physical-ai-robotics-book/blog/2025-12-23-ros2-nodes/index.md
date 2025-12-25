---
slug: ros2-nodes-nervous-system
title: Nodes - The Nervous System of Robots
authors: [masood]
tags: [ros2, robotics, physical-ai]
date: 2025-12-23
---

In Chapter 1, we introduced **ROS 2 (Robot Operating System)**. If a robot is a body, then ROS 2 is its nervous system.

At the core of this nervous system are **Nodes**.

<!-- truncate -->

## What is a Node?

A node is typically a single process responsible for a specific function.
-   One node might control the **camera driver**.
-   Another node might perform **object detection** on that camera feed.
-   A third node might calculate the **motor commands** to track the object.

## Why use Nodes?

1.  **Modularity**: You can swap out the camera driver node for a different camera without changing the object detection node.
2.  **Fault Tolerance**: If the object detection node crashes, the motor control node can safely stop the robot instead of freezing the entire system.
3.  **Distribution**: Nodes can run on different computers. The heavy vision processing node can run on a powerful desktop, while the motor control node runs on the robot's onboard Raspberry Pi.

## A Simple Example

Here is a conceptual Python node from Module 1:

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.get_logger().info('Hello, ROS 2!')
```

In the textbook, we will build complex systems using dozens of these nodes communicating in real-time.

[Read Module 1](/docs/module-1/chapter-1) to learn more.
