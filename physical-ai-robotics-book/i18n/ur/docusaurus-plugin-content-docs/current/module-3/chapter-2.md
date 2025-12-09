

# ماڈیول 3: AI-روبوٹ دماغ (NVIDIA Isaac™)

## باب 2: AI نیویگیشن اور پاتھ پلاننگ

### ذیلی باب 1: Isaac ROS اور Nav2

#### نیویگیشن کے لیے Isaac ROS اور Nav2 کو سمجھنا

**تعارف**
یہ سیکشن NVIDIA کے Isaac ROS فریم ورک کو Nav2 کے ساتھ مربوط کرنے کا طریقہ بتاتا ہے تاکہ خود مختار روبوٹس کے لیے جدید AI سے چلنے والی نیویگیشن اور پاتھ پلاننگ کی صلاحیتیں فراہم کی جا سکیں۔

**تفصیل**
خود مختار نیویگیشن جدید روبوٹکس کا ایک سنگ بنیاد ہے۔ Nav2 (Navigation2) معیاری ROS 2 نیویگیشن اسٹیک ہے، جو لوکلائزیشن، میپنگ، پاتھ پلاننگ، اور رکاوٹوں سے بچنے جیسی صلاحیتیں پیش کرتا ہے۔ NVIDIA کا Isaac ROS GPU پر تیز رفتار ROS 2 پیکیجز فراہم کر کے Nav2 کی تکمیل کرتا ہے جو پرسیپشن اور AI انفرنس کو بڑھاتے ہیں۔ جب مربوط کیا جاتا ہے، تو Isaac ROS اہم نیویگیشن کاموں جیسے گہرائی کا اندازہ، آبجیکٹ کا پتہ لگانے، اور ویژول اوڈومیٹری کو نمایاں طور پر تیز کر سکتا ہے، جو Nav2 کے پلاننگ الگورتھم کو اعلیٰ معیار کا ڈیٹا فراہم کرتا ہے۔ یہ ہم آہنگی روبوٹس کو متحرک ماحول میں زیادہ پیچیدہ اور قابل بھروسہ نیویگیشن انجام دینے کے قابل بناتی ہے، جو ریئل ٹائم فیصلہ سازی اور موثر پاتھ پر عمل درآمد کے لیے جدید GPUs کی طاقت کا فائدہ اٹھاتی ہے۔

**کوڈ مثال**
```python
# تصوراتی مثال: Isaac ROS نوڈ Nav2 کو ڈیٹا فراہم کر رہا ہے (Python)
# یہ سیوڈو-کوڈ ہے؛ اصل انٹیگریشن مخصوص Isaac ROS اور Nav2 APIs پر مشتمل ہے۔

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped

class IsaacROSPerceptionNode(Node):
    def __init__(self):
        super().__init__('isaac_ros_perception_node')
        # Isaac ROS کی جانب سے آپٹیمائزڈ گہرائی کے نقشے یا آبجیکٹ کا پتہ لگانے کی سمولیشن کریں
        self.depth_publisher = self.create_publisher(Image, '/isaac_ros/depth_map', 10)
        self.timer = self.create_timer(0.1, self.publish_fake_depth)
        self.get_logger().info('Isaac ROS Perception Node initialized.')

    def publish_fake_depth(self):
        # حقیقی منظرنامے میں، یہ Isaac ROS سے اصل پروسیس شدہ ڈیٹا ہوگا۔
        fake_depth_msg = Image()
        fake_depth_msg.header.stamp = self.get_clock().now().to_msg()
        fake_depth_msg.header.frame_id = 'camera_frame'
        fake_depth_msg.width = 640
        fake_depth_msg.height = 480
        fake_depth_msg.encoding = 'mono8'
        fake_depth_msg.data = [0] * (640 * 480) # ڈمی ڈیٹا
        self.depth_publisher.publish(fake_depth_msg)
        # self.get_logger().info('Published fake depth map.')

class Nav2IntegrationNode(Node):
    def __init__(self):
        super().__init__('nav2_integration_node')
        # Isaac ROS کے پروسیس شدہ ڈیٹا کو سبسکرائب کریں
        self.depth_subscriber = self.create_subscription(
            Image,
            '/isaac_ros/depth_map',
            self.depth_callback,
            10
        )
        # Nav2 اہداف شائع کر سکتا ہے، ہم مظاہرے کے لیے انہیں سبسکرائب کرتے ہیں۔
        self.goal_subscriber = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )
        self.get_logger().info('Nav2 Integration Node initialized.')

    def depth_callback(self, msg):
        # Isaac ROS سے اعلیٰ معیار کے گہرائی کے نقشے پر کارروائی کریں
        # یہ ڈیٹا Nav2 کے کوسٹ میپ یا پرسیپشن ماڈیولز میں جائے گا۔
        # self.get_logger().info(f'Received depth map from Isaac ROS: {msg.header.stamp}')
        pass

    def goal_callback(self, msg):
        self.get_logger().info(f'Received navigation goal: {msg.pose.position}')
        # ایک حقیقی Nav2 سیٹ اپ میں، یہ پاتھ پلاننگ اور عمل درآمد کو متحرک کرے گا۔
        pass

def main(args=None):
    rclpy.init(args=args)
    isaac_node = IsaacROSPerceptionNode()
    nav2_node = Nav2IntegrationNode()
    
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(isaac_node)
    executor.add_node(nav2_node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        isaac_node.destroy_node()
        nav2_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**تصویر/گراف کا پلیس ہولڈر**
![تصویر: ایک بلاک ڈایاگرام جو Isaac ROS پرسیپشن نوڈز (مثلاً، گہرائی کا اندازہ، آبجیکٹ کا پتہ لگانے) کے Nav2 کے لوکلائزیشن، میپنگ، اور پلاننگ ماڈیولز میں انٹیگریشن کو واضح کرتا ہے۔](pathname:///static/img/placeholder_diagram_isaac_nav2_integration.png)

**کوئز**
Isaac ROS بنیادی طور پر Nav2 کی صلاحیتوں کو کیسے بڑھاتا ہے؟
a) Nav2 کے پورے پلاننگ اسٹیک کو تبدیل کرکے۔
b) Nav2 کو ڈیٹا فراہم کرنے کے لیے GPU پر تیز رفتار پرسیپشن اور AI انفرنس فراہم کرکے۔
c) Nav2 کو چلانے کے لیے ایک نیا ہارڈویئر پلیٹ فارم پیش کرکے۔
d) Nav2 کے لیے ROS 2 مواصلاتی پروٹوکولز کو آسان بنا کر۔

**لغت**
-   **Isaac ROS**: ROS 2 کے لیے GPU پر تیز رفتار پیکیجز کا ایک مجموعہ جو روبوٹکس ایپلی کیشنز کے لیے NVIDIA ہارڈویئر کا فائدہ اٹھاتا ہے۔
-   **Nav2 (Navigation2)**: ROS 2 نیویگیشن اسٹیک، جو روبوٹ لوکلائزیشن، میپنگ، پاتھ پلاننگ، اور حرکت کے عمل درآمد کے لیے الگورتھم فراہم کرتا ہے۔
-   **GPU Acceleration**: کمپیوٹیشن کو تیز کرنے کے لیے گرافکس پروسیسنگ یونٹ (GPU) کا استعمال، خاص طور پر AI انفرنس جیسے متوازی کاموں کے لیے مفید ہے۔

**حوالہ جات**
-   [NVIDIA Isaac ROS دستاویزات](https://developer.nvidia.com/isaac-ros)
-   [ROS 2 Nav2 دستاویزات](https://navigation.ros.org/)

**تاریخ**
Isaac ROS جیسے خصوصی AI فریم ورکس کا Nav2 جیسے عمومی نیویگیشن اسٹیکس کے ساتھ انٹیگریشن ہارڈویئر ایکسیلریشن اور جدید AI کا فائدہ اٹھانے کے بڑھتے ہوئے رجحان کی نمائندگی کرتا ہے تاکہ زیادہ قابل اور موثر خود مختار روبوٹ رویوں کے لیے۔
