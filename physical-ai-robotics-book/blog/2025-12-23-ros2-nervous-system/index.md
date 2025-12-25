---
slug: ros2-nervous-system
title: ROS 2 - The Nervous System of Robots
authors: [masood]
tags: [ros2, robotics, software-architecture]
date: 2025-12-23
---

If a robot's motors are its muscles and its sensors are its eyes, then **ROS 2 (Robot Operating System 2)** is undoubtedly its nervous system.

![ROS 2 Architecture](/img/hero-light.png)

<!-- truncate -->

## Nodes: The Neurons

In ROS 2, the fundamental building block is the **Node**. A node is a single, executable process that performs a specific computation. 

*   **Camera Node**: Reads data from the camera driver.
*   **Perception Node**: Processes images to find objects.
*   **Planner Node**: Decides where to move to avoid obstacles.
*   **Control Node**: Sends current to the motors.

Just like neurons in a brain, these nodes don't do much on their own. Their power comes from how they connect.

## Topics: The Synapses

Nodes communicate by passing messages over named buses called **Topics**. This follows a strict Publish/Subscribe model:

1.  The Camera Node **Publishes** to the `/camera/image_raw` topic.
2.  The Perception Node **Subscribes** to `/camera/image_raw`.
3.  The Perception Node **Publishes** to `/detected_objects`.
4.  The Planner Node **Subscribes** to `/detected_objects`.

## Real-Time & DDS

One of the biggest upgrades from ROS 1 to ROS 2 is the underlying middleware: **DDS (Data Distribution Service)**. This allows for:

*   **Real-time communication**: Critical for balance and safety.
*   **Quality of Service (QoS)**: Configurable reliability (e.g., "Best Effort" vs "Reliable").
*   **Security**: Native authentication and encryption for robot fleets.

In Module 1 of the book, we will build our first ROS 2 package and visualize topics using RVIZ. Let's get building!
