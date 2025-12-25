---
title: "Module 1: The Robotic Nervous System (ROS 2) - Chapter 2"
---

# Module 1: The Robotic Nervous System (ROS 2)

## Chapter 2: Communication Mechanisms

### Subchapter 1: Topics and Services

#### Understanding ROS 2 Topics

**Introduction**
This section explains ROS 2 topics, a fundamental communication pattern for real-time data exchange between nodes.

**Description**
Topics are the most common communication method in ROS 2. Nodes publish messages to a specific topic, and other nodes can subscribe to that topic to receive those messages. This publish-subscribe model allows for decoupling of nodes, as publishers and subscribers do not need to know about each other directly; they only need to agree on the topic name and message type. For example, a sensor node might publish temperature readings to a `/temperature` topic, and a logging node might subscribe to this topic to record the data.

**Code Example**
```python
# Publisher node example (Python)
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic')
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}!'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    try:
        rclpy.spin(minimal_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        minimal_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Diagram/Graph Placeholder**
![Diagram: A ROS 2 topic communication flow showing a publisher node sending messages to a subscriber node via a topic.](pathname:///static/img/placeholder_diagram_ros2_topic.png)

**Quiz**
What is the communication pattern used by ROS 2 topics?
a) Request-Reply
b) Publish-Subscribe
c) Client-Server
d) Peer-to-Peer

**Glossary**
-   **Topic**: A named bus over which nodes exchange messages using a publish-subscribe pattern.
-   **Publish**: To send a message to a topic.
-   **Subscribe**: To receive messages from a topic.

**References**
-   [ROS 2 Documentation - Topics](https://docs.ros.org/en/rolling/Concepts/About-Topics.html)

**History**
Topics have been a core communication mechanism since the early days of ROS. ROS 2 enhances topic communication with improved quality of service (QoS) settings and better real-time guarantees.