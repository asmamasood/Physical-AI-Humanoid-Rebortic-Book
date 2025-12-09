

# ماڈیول 2: ڈیجیٹل ٹوئن (Gazebo & Unity)

## باب 1: فزکس سمولیشن اور ماحول کی تعمیر

### ذیلی باب 1: فزکس سمولیشن کی بنیادی باتیں

#### فزکس سمولیشن کو سمجھنا

**تعارف**
یہ سیکشن روبوٹکس میں فزکس سمولیشن کے بنیادی تصورات کو متعارف کرائے گا، جو ڈیجیٹل ٹوئن اور ورچچول ماحول بنانے میں اس کی اہمیت پر توجہ مرکوز کرے گا۔

**تفصیل**
فزکس سمولیشن روبوٹکس کی ترقی کے لیے انتہائی اہم ہے کیونکہ یہ فزیکل ہارڈویئر پر تعیناتی سے پہلے ورچچول ماحول میں الگورتھم کی جانچ اور توثیق کی اجازت دیتا ہے۔ یہ نقصان کے خطرے کو کم کرتا ہے اور ترقی کے عمل کو تیز کرتا ہے۔ Gazebo اور Unity جیسے ٹولز پیچیدہ فزکس انجن فراہم کرتے ہیں جو حقیقی دنیا کی فزکس کا درست ماڈل بناتے ہیں، جس سے ڈیجیٹل ٹوئن - روبوٹس اور ان کے ماحول کی ورچچول نقل - بنانا ممکن ہوتا ہے۔ یہ سمولیشن سینسر ڈیٹا، ایکچیو ایٹر کے ردعمل، اور ماحولیاتی تعاملات کی نقل کر سکتے ہیں، تجربات کے لیے ایک محفوظ جگہ فراہم کرتے ہیں۔

**کوڈ مثال**
```python
# تصوراتی مثال: فزکس انجن میں ایک سمولیٹڈ روبوٹ کو شروع کرنا
# یہ سیوڈو-کوڈ ہے کیونکہ اصل شروعات سمولیٹر (جیسے Gazebo API، Unity C# اسکرپٹ) پر منحصر ہوتی ہے

class SimulatedRobot:
    def __init__(self, model_file, environment_sdf):
        self.robot_model = self.load_model(model_file)
        self.physics_engine = self.initialize_physics_engine()
        self.environment = self.load_environment(environment_sdf)
        self.robot_pose = self.place_robot_in_environment()

    def load_model(self, model_file):
        print(f"Loading robot model from {model_file}")
        # ... load URDF or other model file ...
        return "RobotModel"

    def initialize_physics_engine(self):
        print("Initializing physics engine (e.g., ODE, Bullet, PhysX)")
        # ... setup physics parameters ...
        return "PhysicsEngine"

    def load_environment(self, environment_sdf):
        print(f"Loading environment from {environment_sdf}")
        # ... load world SDF or scene file ...
        return "Environment"

    def place_robot_in_environment(self):
        print("Placing robot in the environment at initial pose.")
        # ... set initial position and orientation ...
        return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

# مثال استعمال:
# robot = SimulatedRobot("my_robot.urdf", "world.sdf")
```

**تصویر/گراف کا پلیس ہولڈر**
![تصویر: ایک تصوراتی ڈایاگرام جو ایک روبوٹ ماڈل، ایک فزکس انجن، اور ایک سمولیٹڈ ماحول کو دکھا رہا ہے جو ڈیجیٹل ٹوئن بناتے ہیں۔](pathname:///static/img/placeholder_diagram_physics_sim.png)

**کوئز**
روبوٹکس میں فزکس سمولیشن کیوں اہم ہے؟
a) یہ براہ راست فزیکل روبوٹ ہارڈویئر کو کنٹرول کرتا ہے۔
b) یہ خطرات کو کم کرتا ہے اور ترقیاتی اخراجات بچاتا ہے، ورچچول ماحول میں جانچ اور توثیق کی اجازت دیتا ہے۔
c) یہ صرف روبوٹس کی 3D اینیمیشن بنانے کے لیے استعمال ہوتا ہے۔
d) یہ جدید روبوٹکس کی ترقی کے لیے غیر متعلقہ ہے۔

**لغت**
-   **Physics Simulation**: کمپیوٹیشنل ماڈلز کا استعمال کرتے ہوئے حقیقی دنیا کے فزیکل رویے کی نقل کرنے کا عمل۔
-   **Digital Twin**: ایک فزیکل آبجیکٹ یا سسٹم کی ورچچول نمائندگی، جو سمولیشن اور تجزیہ کی اجازت دیتی ہے۔
-   **Gazebo**: ROS کمیونٹی میں وسیع پیمانے پر استعمال ہونے والا ایک مقبول اوپن سورس 3D روبوٹ سمولیٹر۔

**حوالہ جات**
-   [Gazebo دستاویزات](http://gazebosim.org/tutorials)
-   [Unity برائے روبوٹکس](https://docs.unity3d.com/Manual/Simulation.html)

**تاریخ**
روبوٹکس میں فزکس سمولیشن نے کافی ترقی کی ہے، ابتدائی 2D سمولیٹرز سے لے کر Gazebo اور Unity جیسے پیچیدہ 3D ماحول تک، جو بڑھتی ہوئی حقیقت پسندانہ فزکس اور رینڈرنگ کی صلاحیتیں پیش کرتے ہیں۔